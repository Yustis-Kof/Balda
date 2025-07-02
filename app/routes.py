import time
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, current_app
from random import randint
from functools import wraps
from app.database import *
from app.models.board import Board
from app.models.game import Game
from app.utils.dictionary import check_word as _check_word

main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def index():
    return render_template('index.html')

## Декоратор требования авторизации
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('main.login'))
        return f(*args, **kwargs)
    return decorated_function

## Декоратор участия в лобби
def in_lobby(f):
    @wraps(f)
    def decorated_function(game_id, *args, **kwargs):
        try:
            user = current_app.users[session["user_id"]]
        except:
            return redirect(url_for('main.login'))
        try:
            game = current_app.games[game_id]
        except:
            return jsonify({'error': 'Game not found'}), 404
        if user not in game.players:
            return jsonify({'error': 'You are not member of this room'}), 403


## Эндпоинты логина

@main_routes.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = authenticate_user(username, password)
        if user:
            session['user_id'] = user['id']
            session['username'] = user['username']
            return redirect(url_for('main.index'))
        
        return render_template('login.html', error="Неверные данные")
    
    return render_template('login.html')


@main_routes.route('/logout')
def logout():
    session.clear()
    return jsonify({'status': 'success', 'message': 'Разлогинен'}), 200


@main_routes.route('/check_session')
def check_session():
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'username': session['username']
        })
    return jsonify({'authenticated': False})


@main_routes.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username and password:
            add_user(username, password)
            return redirect(url_for('main.index'))
        
        return render_template('signup.html', error="Неверные данные")
    
    return render_template('signup.html')



@main_routes.route('/get_current_user', methods=['GET'])
def get_current_user():
    if 'user_id' in session:
        return jsonify({
            'username': session.get('username'),
            'user_id': session.get('user_id')
        })
    return jsonify({'error': 'Not authenticated'}), 401


## Игровые инструменты



@main_routes.route('/get_random_word', methods=['POST'])
def get_random_word():  # Мне ооочень страшно делать одинаковые имена у методов, но пока конфликтов нет
    """
    Выдаёт случайное слово указанной длины
    ---
    tags:
      - Game
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            length:
              type: integer
              example: 5
    responses:
      200:
        description: Слово
        schema:
          type: object
          properties:
            status:
              type: string
              enum: [success, error]
            word:
              type: string
    """
    data = request.json
    length = data.get('length').lower()

    try:
        word = get_random_word(length=length)
        return jsonify({'status': 'success', 'word': word}), 200
    except:
        return jsonify({'status': 'error'}), 400

## Игра

@login_required
@main_routes.route('/create_lobby', methods=['POST'])
def create_lobby():
    
    data = request.json
    name = data.get("name", "Без названия")
    
    host = current_app.users[session.get("user_id")]

    if len(name) == 5:
        new_game = Game(Board(start_word=name.lower()), [], host, name)
    else:
        new_game = Game(Board(), [], host, name)
    game_id = str(randint(0, 1000000))
    current_app.games[game_id] = new_game
    
    return jsonify({
        'status': 'success',
        'game_id': game_id
    })

@main_routes.route('/get_lobbies')
def get_lobbies():
    lobbies = []
    for lobby in current_app.games:
        lobbies.append({
            'id': lobby,
            'name': current_app.games[lobby].name,
            'host': current_app.games[lobby].host.name,
            'players': [{'username': p.name} for p in current_app.games[lobby].players],
            'max_players': 4
        })
    return jsonify(lobbies)

@login_required
@main_routes.route('/lobby/<game_id>')
def join_room(game_id):
    user = current_app.users[session.get("user_id")]
    try:
        game = current_app.games[game_id]
        
        players = [{"id": p.id, "name": p.name} for p in game.players]
        game_data = {
                "id": game_id,
                "name": game.name,
                "players": players,
                "board": game.board.board
            }
        if not game.started:
            current_app.games[game_id].add_player(user)
            return jsonify({
                "id": game_id,
                "name": game.name,
                "players": players
            })
        else:
            return render_template('game.html', game_data=game_data)
    except KeyError as e:
        return jsonify({'status': 'error', 'message': 'There is no such lobby'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@login_required
@main_routes.route('/lobby/<game_id>/start', methods=['POST'])
def start_game(game_id):
    try:
        game = current_app.games[game_id]
    except:
        return jsonify({'error': 'Game not found'}), 404
    
    if session['user_id'] != game.host.id:
        return jsonify({'error': 'Only host can start the game'}), 403
        
    game.start()
    return jsonify({'status': 'success'})

@login_required
@main_routes.route('/lobby/<game_id>/wait_start')
def wait_for_start(game_id):
    try:
        game = current_app.games[game_id]
    except:
        return jsonify({'error': 'Game not found'}), 404
    
    start_time = time.time()
    while not game.started:
        if time.time() - start_time > 25:
            return jsonify({'status': 'timeout'}), 408
        time.sleep(0.1)  # Плохо: грузит CPU
    
    return jsonify({'status': 'started'})
        

## Ход игры

@login_required # В последствии нужно, чтобы он проверял только слова из реальных партий, иначе читеры будут реконкструировать словарь на сервере
@main_routes.route('/check', methods=['POST'])
def check_word():
    """
    Проверяет наличие слова в словаре
    ---
    tags:
      - Game
    consumes:
      - application/json
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            word:
              type: string
              example: "балда"
    responses:
      200:
        description: Результат проверки слова
        schema:
          type: object
          properties:
            status:
              type: string
              enum: [success, error]
            message:
              type: string
    """
    data = request.json
    word = data.get('word').lower()

    if not word:
        return jsonify({'status': 'error', 'message': 'Слово не передано'}), 400
    
    if _check_word(word):
        return jsonify({'status': 'success', 'message': 'Слово принято'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Слова нет в словаре'}), 200

@in_lobby
@main_routes.route('/lobby/<game_id>/move', methods=['POST'])
def move(game_id):
    user = current_app.users[session["user_id"]]
    game:Game = current_app.games[game_id]

    data = request.json
    letter_coords = data.get('letter_coords')
    word_coords = data.get('word_coords')

    if user != game.whose_move():
        return jsonify({'status': 'error', 'message': 'Не ваш ход'}), 400
    
    try:
        word = game.move(tuple(letter_coords), word_coords)
        return jsonify({'status': 'success', 'word': word, 'state': game.board.board}), 200
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@in_lobby
@main_routes.route('/lobby/<game_id>/wait_move')
def wait_for_move(game_id):
    user = current_app.users[session["user_id"]]
    game:Game = current_app.games[game_id]

    curmove = game.move_num
    
    start_time = time.time()
    while game.move_num == curmove:
        if time.time() - start_time > 25:
            return jsonify({'status': 'timeout'}), 408
        time.sleep(0.1)
    
    return jsonify({'status': 'moved', 'word': game.word_history[-1], 'state': game.board.board})