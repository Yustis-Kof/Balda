from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for
from functools import wraps
from app.database import *
from app.utils.dictionary import check_word

main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def index():
    return render_template('index.html')



## Декоратор требования авторизации (хз пока зачем, мб пригодится)
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
        
        # Проверка в базе данных (заглушка)
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
    
    if check_word(word):
        return jsonify({'status': 'success', 'message': 'Слово принято'}), 200
    else:
        return jsonify({'status': 'error', 'message': 'Слова нет в словаре'}), 200



@main_routes.route('/createlobby')
def create_lobby():
    
    data = request.json
    user_id = data.get("user_id")
    public = bool(data.get("public"))
    password = data.get("password")

    return "<p>{user_id}, {public}, {password}</p>"
