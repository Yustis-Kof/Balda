import time
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for, current_app
from random import randint
from functools import wraps
from app.database import *
from app.models.board import Board
from app.models.exceptions import BaldaException
from app.models.game import Game
from app.utils.dictionary import check_word as _check_word

main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def index():
    """
    Главная страница
    ---
    responses:
      200:
        description: HTML главной страницы
    """
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
        return f(game_id, *args, **kwargs)
    return decorated_function

## Эндпоинты логина

@main_routes.route('/login', methods=['GET', 'POST'])
def login():
    """
    Аутентификация пользователя
    ---
    tags:
      - Auth
    parameters:
      - name: username
        in: formData
        type: string
        required: true
      - name: password
        in: formData
        type: string
        required: true
    responses:
      200:
        description: Форма входа или редирект при успехе
      302:
        description: Редирект после успешной аутентификации
    """
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
    """
    Выход из системы
    ---
    tags:
      - Auth
    responses:
      200:
        description: Успешный выход
        schema:
          type: object
          properties:
            status:
              type: string
            message:
              type: string
    """
    session.clear()
    return jsonify({'status': 'success', 'message': 'Разлогинен'}), 200


@main_routes.route('/check_session')
def check_session():
    """
    Проверка текущей сессии
    ---
    tags:
      - Auth
    responses:
      200:
        description: Статус аутентификации
        schema:
          oneOf:
            - type: object
              properties:
                authenticated:
                  type: boolean
                  example: true
                username:
                  type: string
            - type: object
              properties:
                authenticated:
                  type: boolean
                  example: false
    """
    if 'user_id' in session:
        return jsonify({
            'authenticated': True,
            'username': session['username']
        })
    return jsonify({'authenticated': False})


@main_routes.route('/signup', methods=['GET', 'POST'])
def signup():
    """
    Регистрация нового пользователя
    ---
    tags:
      - Auth
    parameters:
      - name: username
        in: formData
        type: string
        required: true
      - name: password
        in: formData
        type: string
        required: true
    responses:
      200:
        description: Форма регистрации
      302:
        description: Редирект после успешной регистрации
    """
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
    """
    Получение данных текущего пользователя
    ---
    tags:
      - Auth
    responses:
      200:
        description: Данные пользователя
        schema:
          type: object
          properties:
            username:
              type: string
            user_id:
              type: integer
      401:
        description: Не аутентифицирован
        schema:
          type: object
          properties:
            error:
              type: string
    """
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
    Получение случайного слова
    ---
    tags:
      - Game
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
        description: Случайное слово
        schema:
          type: object
          properties:
            status:
              type: string
              enum: [success, error]
            word:
              type: string
      400:
        description: Ошибка генерации слова
    """
    data = request.json
    length = data.get('length')

    try:
        word = get_random_word(length=length)
        return jsonify({'status': 'success', 'word': word}), 200
    except:
        return jsonify({'status': 'error'}), 400

## Игра

def get_game_data(game_id):
    game = current_app.games[game_id]
    
    players = [{"id": p.id, "name": p.name} for p in game.players]

    state = "waiting"
    if game.started:
        state = "ingame"
        players = []
        for p in game.players:
            p_order = game.players.index(p)
            players += [{"id": p.id, "name": p.name, "words": game.player_words[p_order], "score": game.count[p_order]}]
    if game.winners:
        state = "ended"

    

    game_data = {
            "id": game_id,
            "name": game.name,
            "players": players,
            "board": game.board.board,
            "state": state,
            "move_num": game.move_num,
            "current_player_num": game.current_player_num,
            "last_word": game.word_history[-1],
            "winners": game.winners
        }
    
    return game_data


@login_required
@main_routes.route('/create_lobby', methods=['POST'])
def create_lobby():
    """
    Создание игрового лобби
    ---
    tags:
      - Lobby
    security:
      - cookieAuth: []
    parameters:
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            name:
              type: string
              example: "Моя игра"
    responses:
      200:
        description: Лобби создано
        schema:
          type: object
          properties:
            status:
              type: string
            game_id:
              type: string
      401:
        description: Требуется аутентификация
    """
    
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
    """
    Получение списка активных лобби
    ---
    tags:
      - Lobby
    responses:
      200:
        description: Список лобби
        schema:
          type: array
          items:
            type: object
            properties:
              id:
                type: string
              name:
                type: string
              host:
                type: string
              players:
                type: array
                items:
                  type: object
                  properties:
                    username:
                      type: string
              max_players:
                type: integer
    """
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
    """
    Присоединение к игровому лобби
    ---
    tags:
      - Lobby
    security:
      - cookieAuth: []
    parameters:
      - name: game_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Данные лобби
        schema:
          type: object
          properties:
            id:
              type: string
            name:
              type: string
            players:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  name:
                    type: string
            board:
              type: array
              items:
                type: array
                items:
                  type: string
            state:
              type: string
            move_num:
              type: integer
            current_player_num:
              type: integer
            last_word:
              type: string
            winners:
              type: array
              items:
                type: integer
      404:
        description: Лобби не найдено
      400:
        description: Ошибка присоединения
    """
    user = current_app.users[session.get("user_id")]
    try:
        game = current_app.games[game_id]
        game_data = get_game_data(game_id)

        if game_data["state"] == "waiting" or user not in game.players:
            current_app.games[game_id].add_player(user)
            return jsonify(game_data)
        else:
            return render_template('game.html', game_data=game_data)
    except KeyError as e:
        return jsonify({'status': 'error', 'message': 'There is no such lobby'}), 404
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400


@login_required
@main_routes.route('/lobby/<game_id>/start', methods=['POST'])
def start_game(game_id):
    """
    Запуск игры в лобби
    ---
    tags:
      - Game
    security:
      - cookieAuth: []
    parameters:
      - name: game_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Игра начата
        schema:
          type: object
          properties:
            status:
              type: string
      404:
        description: Лобби не найдено
      403:
        description: Только создатель может начать игру
    """
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
    """
    Ожидание начала игры
    ---
    tags:
      - Game
    security:
      - cookieAuth: []
    parameters:
      - name: game_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Игра началась
        schema:
          type: object
          properties:
            status:
              type: string
      404:
        description: Лобби не найдено
      408:
        description: Таймаут ожидания
    """
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

# В последствии нужно, чтобы он проверял только слова из реальных партий, иначе читеры будут реконкструировать словарь на сервере
@login_required
@main_routes.route('/check', methods=['POST'])
def check_word():
    """
    Проверка слова в словаре
    ---
    tags:
      - Game
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
        description: Результат проверки
        schema:
          type: object
          properties:
            status:
              type: string
              enum: [success, error]
            message:
              type: string
      400:
        description: Не передано слово
    """
    data = request.json
    word = data.get('word').lower()

    if not word:
        return jsonify({'status': 'error', 'message': 'Слово не передано'}), 400
    
    if _check_word(word):
        return jsonify({'status': 'success', 'message': 'Слово принято'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Слова нет в словаре'}), 200


@main_routes.route('/lobby/<game_id>/move', methods=['POST'])
@in_lobby
def move(game_id):
    """
    Совершение хода в игре
    ---
    tags:
      - Game
    security:
      - cookieAuth: []
    parameters:
      - name: game_id
        in: path
        type: string
        required: true
      - in: body
        name: body
        required: true
        schema:
          type: object
          properties:
            letter_coords:
              type: array
              items:
                type: integer
              example: [1, 2, "б"]
            word_coords:
              type: array
              items:
                type: array
                items:
                  type: integer
              example: [[0,2], [1,2], [2,2], [3,2], [4,2]]
    responses:
      200:
        description: Ход успешно выполнен
        schema:
          type: object
          properties:
            status:
              type: string
            word:
              type: string
            state:
              type: array
              items:
                type: array
                items:
                  type: string
      400:
        description: Ошибка хода
        schema:
          type: object
          properties:
            status:
              type: string
            message:
              type: string
      403:
        description: Не участник лобби
      404:
        description: Лобби не найдено
    """
    user = current_app.users[session["user_id"]]
    game:Game = current_app.games[game_id]

    data = request.json
    letter_coords = data.get('letter_coords')
    word_coords = data.get('word_coords')

    if user != game.whose_move():
        return jsonify({'status': 'error', 'message': 'Не ваш ход'}), 400
    
    try:
        word = game.move(tuple(letter_coords), word_coords)
        game.board.print_board()
        return jsonify({'status': 'success', 'word': word, 'state': game.board.board}), 200
    except BaldaException as e:
        return jsonify({'status': 'error', 'message': str(e)}), 400
    

@main_routes.route('/lobby/<game_id>/wait_move')
@in_lobby
def wait_for_move(game_id):
    """
    Ожидание хода в игре
    ---
    tags:
      - Game
    security:
      - cookieAuth: []
    parameters:
      - name: game_id
        in: path
        type: string
        required: true
    responses:
      200:
        description: Данные игры после хода
        schema:
          type: object
          properties:
            id:
              type: string
            name:
              type: string
            players:
              type: array
              items:
                type: object
                properties:
                  id:
                    type: integer
                  name:
                    type: string
                  words:
                    type: array
                    items:
                      type: string
                  score:
                    type: integer
            board:
              type: array
              items:
                type: array
                items:
                  type: string
            state:
              type: string
            move_num:
              type: integer
            current_player_num:
              type: integer
            last_word:
              type: string
            winners:
              type: array
              items:
                type: integer
      404:
        description: Лобби не найдено
      408:
        description: Таймаут ожидания
    """
    user = current_app.users[session["user_id"]]
    game:Game = current_app.games[game_id]

    curmove = game.move_num
    
    start_time = time.time()
    while game.move_num == curmove:
        if time.time() - start_time > 25:
            return jsonify({'status': 'timeout'}), 408
        time.sleep(0.1)

    game_data = get_game_data(game_id)
    return jsonify(game_data)