class BaldaException(Exception):
    pass

class InvalidLetter(BaldaException):
    pass

class InvalidCoordinates(BaldaException):
    pass

class LetterOverride(BaldaException):
    pass

class IsolatedLetter(BaldaException):
    pass

class EmptyCell(BaldaException):
    pass

class NoSuchWord(BaldaException):
    pass

class WordNotOnBoard(BaldaException):
    pass

class WordDoesNotContainNewLetter(BaldaException):
    pass

class NoWordGiven(BaldaException):
    pass

class GameStarted(BaldaException):
    pass

class LobbyIsFull(BaldaException):
    pass