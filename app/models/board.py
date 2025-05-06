from exceptions import *
from database import get_random_word

alphabet_ru = "абвгдежзийклмнопрстуфхцчшщъыьэюя" # ё временно отсутствует

class Board:
    """
    Игровое поле.
    """
    def __init__(self, alphabet=alphabet_ru, dictionary="dictionary", width=5, height=5, start_word="балда"):
        """Игровое поле.

        Args:
            alphabet (str, optional): Список допустимых символов. Defaults to alphabet_ru.
            dictionary (str, optional): Название словаря в БД. Defaults to "dictionary".
            width (int, optional): Ширина. Defaults to 5.
            height (int, optional): Высота. Defaults to 5.
            start_word (str, optional): Слово на средней горизонтали, с которого начинается игра. Defaults to "балда".
        """
        self.alphabet = alphabet
        self.dictionary = dictionary
        self.board = [["" for j in range(width)] for i in range(height)]
        
        centery = height//2+1
        centerword = get_random_word(self.dictionary, self.width)
        coords = [(i, centery, centerword[i]) for i in range(width)]
        self.write_word(coords)


    def write(self, letter:chr, x:int, y:int):
        """Вписать букву в клетку

        Args:
            letter (chr): буква
            x (int): Координата X
            y (int): Координата Y
        """
        if letter not in self.alphabet:
            raise InvalidLetter(f"{letter} is not a valid letter")
        if x < 0 or x > self.width or y < 0 or y > self.height:
            raise InvalidCoordinates(f"({x},{y}) are not valid coordinates for {self.width}x{self.height} board")
        if self.board[x][y] != "":
            raise LetterOverride("Can't write in a cell that alredy contains a letter")
        else:
            self.board[x][y] = letter

    def write_word(self, coords:list):
        """Вписать слово в указанные клетки

        Args:
            coords (list): Список кортежей в формате (X, Y, Буква)
        """
        for coord in coords:
            if len(coord) != 3:
                raise InvalidCoordinates(f"{coord} is not a valid coordinate & letter tuple")
            x, y, letter = coord[0], coord[1], coord[2]
            self.write(letter, x, y)
