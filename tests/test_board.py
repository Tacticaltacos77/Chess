import pytest

from board import Board, DEFUALT_PIECES
from errors import IllegalBoardStateError
from pieces import Bishop, King, Knight, Pawn, Piece, Pos, Queen, Rook


def make_board(*pieces: Piece) -> Board:
    return Board({"W": [p for p in pieces if p.color == "W"],
                  "B": [p for p in pieces if p.color == "B"]})


def test_set_board_puts_every_piece_on_its_own_square():
    b = Board(DEFUALT_PIECES)
    for team_pieces in DEFUALT_PIECES.values():
        for p in team_pieces:
            assert b.get_square(p.pos.y, p.pos.x) is p


def test_set_board_leaves_the_middle_empty():
    b = Board(DEFUALT_PIECES)
    for y in range(2, 6):
        for x in range(8):
            assert b.get_square(y, x) is None


def test_set_board_back_rank_order():
    b = Board(DEFUALT_PIECES)
    back_rank = [Rook, Knight, Bishop, Queen, King, Bishop, Knight, Rook]
    for x, piece_type in enumerate(back_rank):
        assert isinstance(b.get_square(0, x), piece_type)
        assert isinstance(b.get_square(7, x), piece_type)


def test_remove_piece():
    r = Rook("W", 4, 4)
    b = make_board(r)
    assert b.remove_piece(r) is r
    assert b.get_square(4, 4) is None


def test_remove_piece_on_empty_spot():
    b = make_board()
    with pytest.raises(IllegalBoardStateError):
        b.remove_piece(Rook("W", 4, 4))


def test_place_piece():
    b = make_board()
    r = Rook("W", 4, 4)
    b.place_piece(r)
    assert b.get_square(4, 4) is r


def test_place_piece_on_top_of_another():
    r = Rook("W", 4, 4)
    b = make_board(r)
    with pytest.raises(IllegalBoardStateError):
        b.place_piece(Knight("B", 4, 4))


def test_move_piece():
    r = Rook("W", 7, 0)
    b = make_board(r)
    b.move_piece(r, Pos(4, 0))
    assert b.get_square(7, 0) is None
    assert b.get_square(4, 0) is r
    assert r.pos == Pos(4, 0)


def test_cap_piece():
    r = Rook("W", 4, 4)
    p = Pawn("B", 4, 6)
    b = make_board(r, p)
    assert b.cap_piece(r, Pos(4, 6), p) is p
    assert b.get_square(4, 4) is None
    assert b.get_square(4, 6) is r


def test_cap_piece_empty():
    r = Rook("W", 4, 4)
    b = make_board(r)
    with pytest.raises(IllegalBoardStateError):
        b.cap_piece(r, Pos(4, 6), Pawn("B", 4, 6))


def test_cap_piece_same_color():
    r = Rook("W", 4, 4)
    p = Pawn("W", 4, 6)
    b = make_board(r, p)
    with pytest.raises(IllegalBoardStateError):
        b.cap_piece(r, Pos(4, 6), p)
    assert b.get_square(4, 6) is p


def test_get_piece_on_empty_square():
    b = make_board()
    with pytest.raises(IllegalBoardStateError):
        b.get_piece(Rook("W", 4, 4))

