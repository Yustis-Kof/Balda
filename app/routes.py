from flask import Blueprint, render_template, request, jsonify
from app.database import get_db_connection
from app.utils.dictionary import check_word

main_routes = Blueprint('main', __name__)

@main_routes.route('/')
def index():
    return render_template('index.html')

@main_routes.route('/move', methods=['POST'])
def make_move():
    data = request.json
    word = data.get('word').lower()

    if check_word(word):
        return jsonify({'status': 'success', 'message': 'Слово принято'})
    else:
        return jsonify({'status': 'error', 'message': 'Слова нет в словаре'})