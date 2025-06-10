from .exceptions import *
from ..database import get_random_word

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
        self.width = width
        self.height = height
        self.board = [["" for j in range(width)] for i in range(height)]
        
        centery = height//2
        centerword = start_word or get_random_word(self.dictionary, self.width)
        coords = [(i, centery, centerword[i]) for i in range(width)]
        self.write_word(coords)

    def print_board(self):
        """Напечатать игровое поле (для отладки)

        Уфф, в который раз мне приходится это делать...
        """
        print("+-"*self.width, end="+\n")
        for i in range(self.height):
            for j in range(self.width):
                print("|", end="")
                print(self.board[i][j] if self.board[i][j] else " ", end="")
            print("|")
            print("+-"*self.width, end="+\n")

    def write(self, letter:chr, x:int, y:int, ignore_exceptions=False):
        """Вписать букву в клетку

        Args:
            letter (chr): буква
            x (int): Координата X
            y (int): Координата Y
            ignore_exceptions (bool): Вписать принудительно
        """
        if letter not in self.alphabet:
            raise InvalidLetter(f"{letter} is not a valid letter")
        if x < 0 or x > self.width or y < 0 or y > self.height:
            raise InvalidCoordinates(f"({x},{y}) are not valid coordinates for {self.width}x{self.height} board")
        if self.board[y][x] != "":
            raise LetterOverride("Can't write in a cell that alredy contains a letter")
        else:
            isolated = True
            for i, j in [
                (-1, -1), (0, -1), (+1, -1),
                (-1,  0),          (+1,  0),
                (-1, +1), (0, +1), (+1, +1)
            ]:
                if 0 <= x+i < self.width and 0 <= y+j < self.height and self.board[y+j][x+i] != "":
                    isolated = False
            if isolated and not ignore_exceptions:
                raise IsolatedLetter("Can't put a letter not connected to any other letter")
            else:
                self.board[y][x] = letter

    def write_word(self, coords:list):
        """Вписать слово в указанные клетки

        Args:
            coords (list): Список кортежей в формате (X, Y, Буква)
        """
        for coord in coords:
            if len(coord) != 3:
                raise InvalidCoordinates(f"{coord} is not a valid coordinates & letter tuple")
            x, y, letter = coord[0], coord[1], coord[2]
            self.write(letter, x, y, ignore_exceptions=True)

    def get_word(self, coords:list):
        """Получить слово по координатам

        Args:
            coords (list): Список координат букв слова в формате (X, Y)
        """
        word = ""
        for x, y in coords:
            if x < 0 or x > self.width or y < 0 or y > self.height:
                raise InvalidCoordinates(f"({x},{y}) are not valid coordinates for {self.width}x{self.height} board")
            if self.board[y][x] == "":
                raise EmptyCell(f"Cell at ({x},{y}) is empty")
            else:
                word += self.board[y][x]
        return word