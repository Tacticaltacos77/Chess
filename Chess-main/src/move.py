from pieces import Capturable, Piece
from board import *
from typing import TYPE_CHECKING, ClassVar
from dataclasses import dataclass, field
from gameState import GameState
from abc import ABC, abstractmethod
if TYPE_CHECKING:
    from typedef import *


@dataclass(frozen=True)
class Move(ABC):
    """Parent Class!!! Shouldnt be used on its own!!!"""
    piece: Piece
    end: Pos
    start: Pos = field(init=False)
    def __post_init__(self):
        object.__setattr__(self, "start", self.piece.pos)
    @abstractmethod
    def apply(self, board: Board):
        board.move_piece(self.piece, self.end)
        self.piece.moved+=1

    @abstractmethod
    def undo(self, board: Board):
        board.move_piece(self.piece, self.start)
        self.piece.moved-=1

@dataclass(frozen=True)
class NormalMove(Move):
    capture: Capturable | None 
    def apply(self, board: Board):
        if isinstance(self.capture, Capturable):
            board.cap_piece(self.piece, self.end, self.capture)
        else:
            board.move_piece(self.piece, self.end)
        self.piece.moved+=1

    def undo(self, board: Board):
        board.move_piece(self.piece, self.start)   

        if isinstance(self.capture, Capturable):
            board.place_piece(self.capture)
        self.piece.moved-=1

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
    end: Pos = field(init=False)
    def __post_init__(self):
        object.__setattr__(self, "end", KING_END_POS[self.piece.color][self.castle_side])

    def apply(self, board: Board):
        rook = board.get_square(*ROOK_START_POS[self.piece.color][self.castle_side])

        assert isinstance(rook, Rook)
        board.move_piece(rook, ROOK_END_POS[self.piece.color][self.castle_side])
        board.move_piece(self.piece, self.end)
        self.piece.moved+=1
        rook.moved+=1

    def undo(self, board: Board):
        rook = board.get_square(*ROOK_END_POS[self.piece.color][self.castle_side])

        assert isinstance(rook, Rook)
        board.move_piece(rook, ROOK_START_POS[self.piece.color][self.castle_side])
        board.move_piece(self.piece, self.start)
        self.piece.moved-=1
        rook.moved-=1

@dataclass(frozen=True)     
class EnPassant(NormalMove):
    piece: Pawn
    def __post_init__(self):
        if not isinstance(self.piece, Pawn):
            raise TypeError("EnPassant can only be done with a Pawn")

@dataclass(frozen=True)
class Promotion(NormalMove):
    piece: Pawn
    promo_piece: Queen|Knight|Bishop|Rook
    def __post_init__(self):
        if not isinstance(self.piece, Pawn):
            raise TypeError("Promotion can only be done with a Pawn")