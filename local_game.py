from app import create_app
from app.models.game import Game
from app.models.player import Bot, Player

if __name__ == '__main__':
    try:
        app = create_app()
    except Exception as e:
        print(e)
        print("Невозможно подключиться к базе данных")
        input()
        
    биба = Bot(0, 'биба')
    боба = Player(1, 'боба')
    game = Game(board=None, players=[биба], host=боба, name="Игра")
    game.skip_move()
    while not game.winners:
        print(", ".join([game.players[i].name + ": " + str(game.count[i]) for i in range(len(game.players))]))
        print("Ход игрока " + game.whose_move().name)
        game.board.print_board()
        if type(game.whose_move()) != Bot:
            print("Введите координаты буквы (Б) и слово в формате XYБ СЛОВО")
            try:
                letter_coords, word = input().split(" ")
                letter_coords = (int(letter_coords[0]), int(letter_coords[1]), letter_coords[2].lower())
                word = word.lower()

                game.move(letter_coords=letter_coords, word=word)
            except Exception as e:
                print(e)
        else:
            print(game.whose_move().make_move(game))
    if len(game.winners > 1):
        winners = [game.players[game.winners[i]] for i in range(len(game.winners))]
        print("Победители: " + ", ".join(winners))
    else:
        print("Победитель: " + game.players[game.winners[0]])