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
        self.count = [0] * len(players)
        self.current_player = 0
        self.history = []
        self.winners = None

    def move(self, letter_coords:tuple, word_coords:list=None, word:str=None):
        """Совершить ход

        Args:
            letter_coords (tuple): Координаты новой буквы в формате (X, Y, Буква)
            word_coords (list, optional): Список координат букв слова в формате (X, Y)
            word (str, optional): Само слово
        """
        next_board = deepcopy(self.board)
        next_board.write(letter_coords[2], letter_coords[0], letter_coords[1])

        if not word_coords and not word:
            raise NoWordGiven("No word coords list nor word given")
        if word_coords:
            if (letter_coords[0], letter_coords[1]) not in word_coords:
                raise WordDoesNotContainNewLetter("Word doesn't contain new letter")
            word = next_board.get_word(word_coords)
        elif word:
            next_board.find_word(word, obligatory_coords=(letter_coords[0], letter_coords[1]))


        if check_word(word):
            self.history.append(deepcopy(self.board))
            
            self.count[self.current_player] += len(word)
            self.current_player = (self.current_player + 1) % len(self.players)
        
            self.board = next_board

            self.check_end()
        else:
            raise NoSuchWord(f"Can't find word {word} in dictionary")

    def skip_move(self):
        self.history.append(deepcopy(self.board))
        self.current_player = (self.current_player + 1) % len(self.players)

        self.check_end()
            


    
    def check_end(self):
        """Проверить, завершена ли партия
        """
        if not self.board.check_space():
            max_count = max(self.count)
            self.winners = [i for i in self.count if self.count[i]==max_count]