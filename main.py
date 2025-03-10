from flask import Flask, render_template, request, jsonify
from flask_cors import CORS  # Импортируем CORS

app = Flask(__name__)
CORS(app)

# Пример словаря
dictionary = set(["балда", "слово", "игра", "поле", "клетка"])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/move', methods=['POST'])
def make_move():
    data = request.json
    word = data.get('word').lower()
    if word in dictionary:
        return jsonify({'status': 'success', 'message': 'Слово принято'})
    else:
        return jsonify({'status': 'error', 'message': 'Слово не найдено'}), 400

if __name__ == '__main__':
    app.run(debug=True)