import pytest

from board import Board
from fen import DEFAULT_FEN
from errors import IllegalBoardStateError
from pieces import Bishop, King, Knight, Pawn, Piece, Queen, Rook
from helper import to_pos



def test_set_board_puts_every_piece_on_its_own_square():
    pieces = DEFAULT_FEN.build_pieces()
    b = Board(pieces)
    for p in pieces:
        assert b.get_square(p.pos.y, p.pos.x) is p

def test_empty_board():
    b = Board([])
    for y in range(8):
        for x in range(8):
            assert b.get_square(y, x) is None


def test_set_board_leaves_the_middle_empty():
    pieces = DEFAULT_FEN.build_pieces()
    b = Board(pieces)
    for y in range(2, 6):
        for x in range(8):
            assert b.get_square(y, x) is None


def test_set_board_back_rank_order():
    pieces = DEFAULT_FEN.build_pieces()
    b = Board(pieces)
    back_rank = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
    for x, piece_type in enumerate(back_rank):
        assert isinstance(b.get_square(0, x), piece_type)
        assert isinstance(b.get_square(7, x), piece_type)


def test_remove_piece():
    r = Rook("W", *to_pos("e4"))
    b = Board([r])
    assert b.remove_piece(r) is r
    assert b.get_square(*to_pos("e4")) is None


def test_remove_piece_on_empty_spot():
    b = Board([])
    with pytest.raises(IllegalBoardStateError):
        b.remove_piece(Rook("W", *to_pos("e4")))


def test_place_piece():
    b = Board([])
    r = Rook("W", *to_pos("e4"))
    b.place_piece(r)
    assert b.get_square(*to_pos("e4")) is r


def test_place_piece_on_top_of_another():
    r = Rook("W", *to_pos("e4"))
    b = Board([r])
    with pytest.raises(IllegalBoardStateError):
        b.place_piece(Knight("B", *to_pos("e4")))


def test_move_piece():
    r = Rook("W", *to_pos("a1"))
    b = Board([r])
    b.move_piece(r, to_pos("a4"))
    assert b.get_square(*to_pos("a1")) is None
    assert b.get_square(*to_pos("a4")) is r
    assert r.pos == to_pos("a4")


def test_cap_piece():
    r = Rook("W", *to_pos("e4"))
    p = Pawn("B", *to_pos("g4"))
    b = Board([r, p])
    assert b.cap_piece(r, to_pos("g4"), p) is p
    assert b.get_square(*to_pos("e4")) is None
    assert b.get_square(*to_pos("g4")) is r


def test_cap_piece_empty():
    r = Rook("W", *to_pos("e4"))
    b = Board([r])
    with pytest.raises(IllegalBoardStateError):
        b.cap_piece(r, to_pos("g4"), Pawn("B", *to_pos("g4")))


def test_cap_piece_same_color():
    r = Rook("W", *to_pos("e4"))
    p = Pawn("W", *to_pos("g4"))
    b = Board([r, p])
    with pytest.raises(IllegalBoardStateError):
        b.cap_piece(r, to_pos("g4"), p)
    assert b.get_square(*to_pos("g4")) is p
