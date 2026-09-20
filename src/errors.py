class IllegalBoardStateError(Exception):
    """The board was asked to do something that contradicts what is on it."""

class IllegalGameStateError(Exception):
    """The game state was built from, or moved into, a position that cannot exist."""

class IllegalMoveError(Exception):
    """The move is not one of the legal moves for the side to move."""