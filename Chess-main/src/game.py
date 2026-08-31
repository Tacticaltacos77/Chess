from board import *
from gameState import GameState
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from typedef import *
    from move import Move
    from pieces import *

class Game:
    def __init__(self, white_player, black_player):
        self.white = white_player 
        self.black = black_player     
        self.state = GameState()
        self.board = Board(self.state.pieces)

    def make_move(self, move: Move):
        pass
    def undo_move(self, move: Move):
        pass