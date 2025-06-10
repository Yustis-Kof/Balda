from ..database import get_user


class Player:
    """Игрок."""

    def __init__(self, id):
        user_data = get_user(id)
        self.id = id
        self.name = user_data["username"]
