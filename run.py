from app import create_app
from app.models.game import Game
from app.models.board import Board



if __name__ == '__main__':
    app = create_app()

    app.run(debug=True, threaded=True)
