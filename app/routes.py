from flask import Blueprint, render_template, request, jsonify
from app.database import get_db_connection
from app.utils.dictionary import check_word

main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def index():
    return render_template('index.html')

@main_routes.route('/move', methods=['POST'])
def make_move():
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
        description: Результат проверки
        schema:
          type: object
          properties:
            status:
              type: string
              example: "success"
            message:
              type: string
              example: "Слово принято"
      400:
        description: Ошибка
        schema:
          type: object
          properties:
            status:
              type: string
              example: "error"
            message:
              type: string
              example: "Слова нет в словаре"
    """
    data = request.json
    word = data.get('word').lower()

    if check_word(word):
        return jsonify({'status': 'success', 'message': 'Слово принято'})
    else:
        return jsonify({'status': 'error', 'message': 'Слова нет в словаре'}), 400