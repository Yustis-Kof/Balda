from models.game import Game
from models.player import Bot, Player
from utils.dictionary import Dictionary

if __name__ == '__main__':
    game_dictionary = Dictionary()
    game_dictionary.load_dictionary(dictionary="balda.db", pos=["сущ"], min_freq=0, max_freq=1000000, min_length=1, max_length=100)
    bot_dictionary = Dictionary()
    bot_dictionary.load_dictionary(dictionary="balda.db", pos=["сущ"], min_freq=0, max_freq=1000000, min_length=1, max_length=100)

    биба = Bot(0, 'биба', dictionary=bot_dictionary)
    боба = Player(1, 'боба')
    game = Game(board=None, players=[биба], host=боба, name="Игра", dictionary=game_dictionary)
    game.start()
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