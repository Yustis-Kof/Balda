from app import create_app
from app.models.game import Game
from app.models.board import Board

app = create_app()

if __name__ == '__main__':
    game = Game(board=None, players=['биба', 'боба'])
    while not game.winners:
        print(", ".join([game.players[i] + ": " + str(game.count[i]) for i in range(len(game.players))]))
        print("Ход игрока " + game.players[game.current_player])
        game.board.print_board()
        print("Введите координаты буквы (Б) и слово в формате XYБ СЛОВО")
        letter_coords, word = input().split(" ")
        try:
            letter_coords = (int(letter_coords[0]), int(letter_coords[1]), letter_coords[2].lower())
            word = word.lower()

            game.move(letter_coords=letter_coords, word=word)
        except Exception as e:
            print(e)
    if len(game.winners > 1):
        winners = [game.players[game.winners[i]] for i in range(len(game.winners))]
        print("Победители: " + ", ".join(winners))
    else:
        print("Победитель: " + game.players[game.winners[0]])

    #app.run(debug=True)
