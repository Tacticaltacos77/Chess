import pytest

from board import Board
from errors import IllegalBoardStateError
from pieces import *
from game import Game
from fen import DEFAULT_FEN
from helper import to_pos

def test_pawn_normal_movement_empty_board():
    p = Pawn("W", *to_pos("e3"))
    b = Board([p])
    p_moves = p.moves(b)
    assert {str(m) for m in p_moves} == {"pe3-e4"}

def test_pawn_double_movement_empty_board():
    p = Pawn("W", *to_pos("e2"))
    b = Board([p])
    p_moves = p.moves(b)
    assert {str(m) for m in p_moves} == {"pe2-e3", "pe2-e4"}

def test_pawn_attacking():
    wp = Pawn("W", *to_pos("d5"))
    bp = Pawn("B", *to_pos("c6"))
    bp2 = Pawn("B", *to_pos("e6"))
    b = Board([wp, bp, bp2])
    wp_moves = wp.moves(b)
    assert {str(m) for m in wp_moves} == {"pd5-d6", "pd5xc6", "pd5xe6"}

def test_pawn_blocked():
    wp = Pawn("W", *to_pos("e4"))
    bp = Pawn("B", *to_pos("e5"))
    b = Board([wp, bp])
    assert {str(m) for m in wp.moves(b)} == set()

def test_pawn_double_move_blocked():
    wp = Pawn("W", *to_pos("e2"))
    bn = Knight("B", *to_pos("e4"))
    b = Board([wp, bn])
    assert {str(m) for m in wp.moves(b)} == {"pe2-e3"}

def test_pawn_cannot_jump_on_double_move():
    wp = Pawn("W", *to_pos("e2"))
    bn = Knight("B", *to_pos("e3"))
    b = Board([wp, bn])
    assert {str(m) for m in wp.moves(b)} == set()

def test_pawn_does_not_capture_own_pieces():
    wp = Pawn("W", *to_pos("d4"))
    wn = Knight("W", *to_pos("c5"))
    wn2 = Knight("W", *to_pos("e5"))
    b = Board([wp, wn, wn2])
    assert {str(m) for m in wp.moves(b)} == {"pd4-d5"}

def test_pawn_capture_on_edge_file():
    wp = Pawn("W", *to_pos("a4"))
    bp = Pawn("B", *to_pos("b5"))
    bp2 = Pawn("B", *to_pos("h5"))
    b = Board([wp, bp, bp2])
    assert {str(m) for m in wp.moves(b)} == {"pa4-a5", "pa4xb5"}

def test_black_pawn_moves_down_the_board():
    bp = Pawn("B", *to_pos("e7"))
    wn = Knight("W", *to_pos("d6"))
    wn2 = Knight("W", *to_pos("f6"))
    b = Board([bp, wn, wn2])
    assert {str(m) for m in bp.moves(b)} == {"pe7-e6", "pe7-e5", "pe7xd6", "pe7xf6"}

def test_pawn_promotion():
    wp = Pawn("W", *to_pos("e7"))
    b = Board([wp])
    wp_moves = wp.moves(b)
    assert {str(m) for m in wp_moves} == {"pe7-e8=Q", "pe7-e8=R", "pe7-e8=B", "pe7-e8=N"}
    assert all(isinstance(m, Promotion) for m in wp_moves)

def test_pawn_capture_promotion():
    wp = Pawn("W", *to_pos("e7"))
    br = Rook("B", *to_pos("d8"))
    bn = Knight("B", *to_pos("e8"))
    b = Board([wp, br, bn])
    assert {str(m) for m in wp.moves(b)} == {"pe7xd8=Q", "pe7xd8=R", "pe7xd8=B", "pe7xd8=N"}

def test_black_pawn_promotion():
    bp = Pawn("B", *to_pos("d2"))
    b = Board([bp])
    assert {str(m) for m in bp.moves(b)} == {"pd2-d1=Q", "pd2-d1=R", "pd2-d1=B", "pd2-d1=N"}

def test_pawn_en_passant():
    wp = Pawn("W", *to_pos("e5"))
    bp = Pawn("B", *to_pos("d5"))
    b = Board([wp, bp])
    wp_moves = wp.moves(b)
    assert {str(m) for m in wp_moves} == {"pe5-e6", "pe5xd6"}
    ep = next(m for m in wp_moves if m.end == to_pos("d6"))
    assert isinstance(ep, EnPassant)
    assert ep.capture is bp

def test_pawn_en_passant_does_not_replace_normal_capture():
    wp = Pawn("W", *to_pos("e5"))
    bp = Pawn("B", *to_pos("d5"))
    bn = Knight("B", *to_pos("d6"))
    b = Board([wp, bp, bn])
    cap = next(m for m in wp.moves(b) if m.end == to_pos("d6"))
    assert type(cap) is NormalMove
    assert cap.capture is bn

def test_bishop_movement_empty_board():
    wb = Bishop("W", *to_pos("d5"))
    b = Board([wb])
    wb_moves = wb.moves(b)
    assert {str(m) for m in wb_moves} == {
        "Bd5-e4", "Bd5-f3", "Bd5-g2", "Bd5-h1",
        "Bd5-c4", "Bd5-b3", "Bd5-a2", "Bd5-e6",
        "Bd5-f7", "Bd5-g8", "Bd5-c6", "Bd5-b7", 
        "Bd5-a8",
    }

def test_bishop_attacking():
    wb = Bishop("W", *to_pos("d5"))
    bp = Pawn("B", *to_pos("b7"))
    bp2 = Pawn("B", *to_pos("f3"))
    b = Board([wb, bp, bp2])
    wb_moves = wb.moves(b)
    assert {str(m) for m in wb_moves} == {
        "Bd5-e4", "Bd5xf3", "Bd5-c4", "Bd5-b3", 
        "Bd5-a2", "Bd5-e6", "Bd5-f7", "Bd5-g8",
        "Bd5-c6", "Bd5xb7",
    }

def test_bishop_blocked_by_own_pieces():
    wb = Bishop("W", *to_pos("c1"))
    wp = Pawn("W", *to_pos("b2"))
    wp2 = Pawn("W", *to_pos("d2"))
    b = Board([wb, wp, wp2])
    assert {str(m) for m in wb.moves(b)} == set()

def test_rook_movement_empty_board():
    wr = Rook("W", *to_pos("d5"))
    b = Board([wr])
    wr_moves = wr.moves(b)
    assert {str(m) for m in wr_moves} == {
        "Rd5-d6", "Rd5-d7", "Rd5-d8", "Rd5-d4",
        "Rd5-d3", "Rd5-d2", "Rd5-d1", "Rd5-c5", 
        "Rd5-b5", "Rd5-a5", "Rd5-e5", "Rd5-f5", 
        "Rd5-g5", "Rd5-h5",
    }

def test_rook_attacking():
    wr = Rook("W", *to_pos("d5"))
    bp = Pawn("B", *to_pos("b5"))
    bp2 = Pawn("B", *to_pos("d3"))
    b = Board([wr, bp, bp2])
    wr_moves = wr.moves(b)
    assert {str(m) for m in wr_moves} == {
        "Rd5-d6", "Rd5-d7", "Rd5-d8", "Rd5-d4", 
        "Rd5xd3", "Rd5-c5", "Rd5xb5", "Rd5-e5", 
        "Rd5-f5", "Rd5-g5", "Rd5-h5",
    }

def test_rook_blocked_by_own_piece():
    wr = Rook("W", *to_pos("a1"))
    wp = Pawn("W", *to_pos("a4"))
    b = Board([wr, wp])
    assert {str(m) for m in wr.moves(b)} == {
        "Ra1-a2", "Ra1-a3", "Ra1-b1", "Ra1-c1",
        "Ra1-d1", "Ra1-e1", "Ra1-f1", "Ra1-g1",
        "Ra1-h1",
    }

def test_queen_movement_empty_board():
    wq = Queen("W", *to_pos("d5"))
    b = Board([wq])
    wq_moves = wq.moves(b)
    assert {str(m) for m in wq_moves} == {
        "Qd5-d6", "Qd5-d7", "Qd5-d8", "Qd5-d4",
        "Qd5-d3", "Qd5-d2", "Qd5-d1","Qd5-c5", 
        "Qd5-b5", "Qd5-a5", "Qd5-e5", "Qd5-f5", 
        "Qd5-g5", "Qd5-h5", "Qd5-e4", "Qd5-f3", 
        "Qd5-g2", "Qd5-h1", "Qd5-c4", "Qd5-b3", 
        "Qd5-a2", "Qd5-e6", "Qd5-f7", "Qd5-g8",
        "Qd5-c6", "Qd5-b7", "Qd5-a8",
    }

def test_queen_attacking():
    wq = Queen("W", *to_pos("d5"))
    bp = Pawn("B", *to_pos("d7"))
    bp2 = Pawn("B", *to_pos("f3"))
    b = Board([wq, bp, bp2])
    wq_moves = wq.moves(b)
    assert {str(m) for m in wq_moves} == {
        "Qd5-d6", "Qd5xd7", "Qd5-d4", "Qd5-d3", 
        "Qd5-d2", "Qd5-d1", "Qd5-c5", "Qd5-b5", 
        "Qd5-a5", "Qd5-e5", "Qd5-f5", "Qd5-g5", 
        "Qd5-h5", "Qd5-e4", "Qd5xf3", "Qd5-c4", 
        "Qd5-b3", "Qd5-a2", "Qd5-e6", "Qd5-f7",
        "Qd5-g8", "Qd5-c6", "Qd5-b7", "Qd5-a8",
    }

def test_king_movement_empty_board():
    wk = King("W", *to_pos("d5"))
    b = Board([wk])
    wk_moves = wk.moves(b)
    # King.moves always adds both castles and Game filters them
    assert {str(m) for m in wk_moves} == {
        "Kd5-c6", "Kd5-d6", "Kd5-e6", "Kd5-c5", 
        "Kd5-e5", "Kd5-c4", "Kd5-d4", "Kd5-e4",
        "O-O", "O-O-O",
    }

def test_king_attacking():
    wk = King("W", *to_pos("d5"))
    bp = Pawn("B", *to_pos("c6"))
    bp2 = Pawn("B", *to_pos("e4"))
    b = Board([wk, bp, bp2])
    wk_moves = wk.moves(b)
    assert {str(m) for m in wk_moves} == {
        "Kd5xc6", "Kd5-d6", "Kd5-e6", "Kd5-c5",
        "Kd5-e5", "Kd5-c4", "Kd5-d4", "Kd5xe4",
        "O-O", "O-O-O",
    }

def test_king_in_corner():
    wk = King("W", *to_pos("h1"))
    b = Board([wk])
    assert {str(m) for m in wk.moves(b)} == {"Kh1-g1", "Kh1-g2", "Kh1-h2", "O-O", "O-O-O"}

def test_knight_movement_empty_board():
    wn = Knight("W", *to_pos("d5"))
    b = Board([wn])
    wn_moves = wn.moves(b)
    assert {str(m) for m in wn_moves} == {
        "Nd5-c7", "Nd5-e7", "Nd5-f6", "Nd5-f4",
        "Nd5-e3", "Nd5-c3", "Nd5-b4", "Nd5-b6",
    }

def test_knight_attacking():
    wn = Knight("W", *to_pos("d5"))
    bp = Pawn("B", *to_pos("c7"))
    bp2 = Pawn("B", *to_pos("e3"))
    b = Board([wn, bp, bp2])
    wn_moves = wn.moves(b)
    assert {str(m) for m in wn_moves} == {
        "Nd5xc7", "Nd5-e7", "Nd5-f6", "Nd5-f4",
        "Nd5xe3", "Nd5-c3", "Nd5-b4", "Nd5-b6",
    }

def test_knight_in_corner():
    wn = Knight("W", *to_pos("a1"))
    b = Board([wn])
    assert {str(m) for m in wn.moves(b)} == {"Na1-b3", "Na1-c2"}

def test_knight_jumps_over_pieces():
    wn = Knight("W", *to_pos("b1"))
    pawns = [Pawn("W", *to_pos(sq)) for sq in ("a2", "b2", "c2", "d2")]
    b = Board([wn, *pawns])
    assert {str(m) for m in wn.moves(b)} == {"Nb1-a3", "Nb1-c3"}

def test_black_piece_notation_is_uppercase():
    bn = Knight("B", *to_pos("b8"))
    b = Board([bn])
    assert {str(m) for m in bn.moves(b)} == {"Nb8-a6", "Nb8-c6", "Nb8-d7"}

def test_rook_is_attacking_stops_at_blocker():
    wr = Rook("W", *to_pos("a1"))
    bp = Pawn("B", *to_pos("a4"))
    b = Board([wr, bp])
    assert wr.isAttacking(to_pos("a3"), b)
    assert wr.isAttacking(to_pos("a4"), b)
    assert not wr.isAttacking(to_pos("a5"), b)

def test_bishop_is_not_attacking_straight_lines():
    wb = Bishop("W", *to_pos("d5"))
    b = Board([wb])
    assert wb.isAttacking(to_pos("e6"), b)
    assert not wb.isAttacking(to_pos("d6"), b)
    assert not wb.isAttacking(to_pos("e5"), b)

def test_knight_is_attacking_over_pieces():
    wn = Knight("W", *to_pos("b1"))
    pawns = [Pawn("W", *to_pos(sq)) for sq in ("a2", "b2", "c2", "d2")]
    b = Board([wn, *pawns])
    assert wn.isAttacking(to_pos("a3"), b)
    assert wn.isAttacking(to_pos("c3"), b)
    assert not wn.isAttacking(to_pos("b3"), b)

def test_pawn_is_attacking_diagonals_only():
    wp = Pawn("W", *to_pos("e4"))
    b = Board([wp])
    assert wp.isAttacking(to_pos("d5"), b)
    assert wp.isAttacking(to_pos("f5"), b)
    assert not wp.isAttacking(to_pos("e5"), b)
    assert not wp.isAttacking(to_pos("d3"), b)

def test_black_pawn_is_attacking_down_the_board():
    bp = Pawn("B", *to_pos("e5"))
    b = Board([bp])
    assert bp.isAttacking(to_pos("d4"), b)
    assert bp.isAttacking(to_pos("f4"), b)
    assert not bp.isAttacking(to_pos("d6"), b)
