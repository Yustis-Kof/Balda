from flask import Blueprint, render_template, request, jsonify
from app.database import get_db_connection
from app.utils.dictionary import check_word

main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def index():
    return render_template('index.html')

@main_routes.route('/check', methods=['POST'])
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