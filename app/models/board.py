from exceptions import *

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
            raise LetterOverride("Can't write in cell where is alredy a letter")
        else:
            self.board[x][y] = letter