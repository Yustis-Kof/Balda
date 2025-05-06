from app import create_app
from app.models.board import Board

app = create_app()

if __name__ == '__main__':
    board = Board()
    board.print_board()
    #app.run(debug=True)