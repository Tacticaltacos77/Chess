from board import *
from gameState import GameState
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typedef import *
    from pieces import *

class Game:
    def __init__(self, pieces):
        self.state = GameState(pieces)

    def make_move(self, move: Move):
        pass

    def undo_move(self, move: Move):
        pass