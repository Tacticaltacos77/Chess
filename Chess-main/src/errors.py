class WrongTurnError(Exception):
    """Eception raised if a wrong color piece is selected"""
    def __init__(self, p):
        pass
class IllegalBoardStateError(Exception):
    pass