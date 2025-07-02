from app import create_app
from app.models.game import Game
from app.models.board import Board



if __name__ == '__main__':
    app = create_app()

    app.run(host='0.0.0.0', debug=True, threaded=True)
    test_response = app.blueprints.wait_for_move("test_game_id")
    print("Тест декоратора:", test_response)
