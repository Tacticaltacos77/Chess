from pieces import Piece, Pos
from board import *
from typing import TYPE_CHECKING, ClassVar
from dataclasses import dataclass, field
from gameState import GameState

if TYPE_CHECKING:
    from typedef import *

@dataclass(frozen=True)
class Move:
    """Parent Class!!! Shouldnt be used on its own!!!"""
    piece: Piece
    end: Pos
    start: Pos = field(init=False)
    def __post_init__(self):
        object.__setattr__(self, "start", self.piece.pos)

@dataclass(frozen=True)
class NormalMove(Move):
    capture: Piece | None 
    def apply(self, gs: GameState):
        if self.capture:
            gs.capture_p(self.capture)
        if gs.board.move_piece(self.piece,self.end):
            raise ValueError("Tried to make move but there is another piece in the spot")
    def undo(self, gs: GameState):
        if gs.board.move_piece(self.piece, self.start):
            raise ValueError("Tried to undo move but there is another piece in the spot")
        if self.capture:
            gs.return_p(self.capture)

ROOK_START_POS: Teams[Sides[Pos]] = {"W": {"Q": Pos(7, 0), "K": Pos(7,7)}, 
                                           "B": {"Q": Pos(0, 0), "K": Pos(0,7)}}
ROOK_END_POS: Teams[Sides[Pos]] = {"W": {"Q": Pos(7, 0), "K": Pos(7,7)}, 
                                         "B": {"Q": Pos(0, 0), "K": Pos(0,7)}}
KING_END_POS: Teams[Sides[Pos]] = {"W": {"Q": Pos(7, 0), "K": Pos(7,7)}, 
                                   "B": {"Q": Pos(0, 0), "K": Pos(0,7)}}
@dataclass(frozen=True)
class Castle(Move):
    piece: King
    castle_side: Side
    rook: Rook
    end: Pos = field(init=False)
    def __post_init__(self):
        object.__setattr__(self, "end", KING_END_POS[self.piece.color][self.castle_side])

    def apply(self, gs: GameState):
        gs.board.move_piece(self.rook, ROOK_END_POS[self.piece.color][self.castle_side])
        gs.board.move_piece(self.piece, self.end)

    def undo(self, gs: GameState):
        gs.board.move_piece(self.rook, ROOK_START_POS[self.piece.color][self.castle_side])
        gs.board.move_piece(self.piece, self.start)

@dataclass(frozen=True)     
class EnPassant(NormalMove):
    piece: Pawn
    def __post_init__(self):
        if not isinstance(self.piece, Pawn):
            raise TypeError("EnPassant can only be done with a Pawn")
    def apply(self, gs: GameState):
        super().apply(gs)
    def undo(self, gs: GameState):
        super().apply(gs)

@dataclass(frozen=True)
class Promotion(NormalMove):
    piece: Pawn
    promo: Queen|Knight|Bishop|Rook
    def __post_init__(self):
        if not isinstance(self.piece, Pawn):
            raise TypeError("Promotion can only be done with a Pawn")
    def apply(self, gs: GameState):
        pass
    def undo(self, gs: GameState):
        pass