import pytest

from board import Board
from errors import IllegalBoardStateError
from pieces import Bishop, King, Knight, Pawn, Piece, Pos, Queen, Rook
from game import Game, get_default_pieces

def test_pawn_movement():
    p = Pawn("W", 0, 5)
    b = Board(get_default_pieces())
    p.moves(b)

def test_pawn_attacking():
    b = Board([])

def test_bishop_movement():
    pass

def test_rook_movement():
    pass

def test_king_movement():
    pass 

def test_kight_movement():
    pass