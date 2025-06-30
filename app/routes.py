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

    new_game = Game(Board(), [], host, name)
    game_id = str(randint(0, 1000000))
    current_app.games[game_id] = new_game
    
    return jsonify({
        'status': 'success',
        'game_id': game_id
    })

@main_routes.route('/get_lobbies')
def get_lobbies():
    host = current_app.users[session.get("user_id")]
    lobbies = []
    for lobby in current_app.games:
        lobbies.append({
            'id': lobby,
            'name': host.name,
            'players': len(current_app.games[lobby].players),
            'max_players': 4
        })
    return jsonify(lobbies)

@login_required
@main_routes.route('/lobby/<game_id>')
def join_room(game_id):
    user = current_app.users[session.get("user_id")]
    try:
        current_app.games[game_id].add_player(user)
        return render_template('game.html')
    except Exception as e:
        return jsonify({'status': 'error', 'message': e}), 400

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


@main_routes.route('/get_current_user', methods=['GET'])
def get_current_user():
    if 'user_id' in session:
        return jsonify({
            'username': session.get('username'),
            'user_id': session.get('user_id')
        })
    return jsonify({'error': 'Not authenticated'}), 401
