from app import create_app
from app.models.game import Game
from app.models.board import Board

app = create_app()

if __name__ == '__main__':
    game = Game(board=None, players=[])
    game.board.print_board()
    #app.run(debug=True)
