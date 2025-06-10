from .board import Board
from ..utils.dictionary import check_word
from .exceptions import *
from copy import deepcopy

class Game:
    """
    Игровая партия.
    """

    def __init__(self, board:Board, players:dict):
        """Игровая партия.

        Args:
            board (Board): Игровое поле
            players (dict): Игроки
        """

        if not board:
            self.board = Board()
        else:
            self.board = board
        self.players = players
        self.history = []

    def move(self, letter_coords:tuple, word_coords:list):
        """Совершить ход

        Args:
            letter_coords (tuple): Координаты новой буквы в формате (X, Y, Буква)
            word_coords (list): Список координат букв слова в формате (X, Y)
        """
        next_board = deepcopy(self.board)
        next_board.write(letter_coords[2], letter_coords[0], letter_coords[1])
        word = next_board.get_word(word_coords)
        if check_word(word):
            self.history.append(deepcopy(self.board))
            self.board = next_board
        else:
            raise NoSuchWord(f"Can't find word {word} in dictionary")
