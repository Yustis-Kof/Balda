from copy import deepcopy
from random import choice
from models import dictionary


class Player:
    """Игрок."""

    def __init__(self, id, name):
        self.id = id
        self.name = name

class Bot(Player):
    """Бот."""
    def __init__(self, id, name, dictionary=dictionary.Dictionary()):
        super().__init__(id, name)
        self.dictionary = dictionary

    def make_move(self, game):
        board = game.board
        alphabet = board.alphabet
        width = board.width
        height = board.height
        word_history = game.word_history

        boards = []

        for i in range(width):
            for j in range(height):
                for letter in alphabet:
                    new_board = deepcopy(board)
                    try:
                        new_board.write(letter, i, j)
                        #new_board.print_board()
                        boards.append((new_board, letter, (i, j)))
                    except:
                        del new_board
        
        global words
        words = []
        moves = []
        found = False

        def find_words(board, coords, obligatory_coords):
            global words

            n = len(coords)

            x, y = coords[n-1]

            word = board.get_word(coords)

            if not self.dictionary.check_prefix(word):
                return
            if self.dictionary.check_word(word) and word not in word_history and obligatory_coords in coords:
                words += [coords]

            for i, j in [
                        (0, -1), 
                (-1,  0),      (+1,  0),
                        (0, +1)
            ]:
                if 0 <= x+i < width and 0 <= y+j < height and (x+i, y+j) not in coords and board.board[y+j][x+i]:
                    find_words(board, coords + [(x+i, y+j)], obligatory_coords)

        for b in boards:
            for x in range(width):
                for y in range(height):
                    if board.board[y][x]:
                        find_words(b[0], [(x, y)], b[2])
                        if words != []:
                            for w in words:
                                moves.append(((*b[2], b[1]), w))
                            words = []  # Сбрасываем найденные слова для этой буквы

        max_len = max(len(move[1]) for move in moves)
        best_moves = [move for move in moves if len(move[1]) == max_len]

        best_move = choice(best_moves)

        return game.move(letter_coords=best_move[0], word_coords=best_move[1])
            

