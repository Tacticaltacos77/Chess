from board import Board
from pieces import *
from helper import to_pos, to_square

# ---- Pawn movement ----

def test_white_pawn_normal_move():
    wp = Pawn("W", *to_pos("e3"))
    b = Board([wp])
    wp_moves = wp.moves(b)
    assert {str(m) for m in wp_moves} == {"pe3-e4"}

def test_white_pawn_double_move():
    wp = Pawn("W", *to_pos("e2"))
    b = Board([wp])
    wp_moves = wp.moves(b)
    assert {str(m) for m in wp_moves} == {"pe2-e3", "pe2-e4"}

def test_white_pawn_double_move_blocked():
    wp = Pawn("W", *to_pos("e2"))
    bn = Knight("B", *to_pos("e4"))
    b = Board([wp, bn])
    assert {str(m) for m in wp.moves(b)} == {"pe2-e3"}

def test_white_pawn_blocked_double_move():
    wp = Pawn("W", *to_pos("e2"))
    bn = Knight("B", *to_pos("e3"))
    b = Board([wp, bn])
    assert {str(m) for m in wp.moves(b)} == set()

def test_black_pawn_normal_move():
    bp = Pawn("B", *to_pos("e6"))
    b = Board([bp])
    bp_moves = bp.moves(b)
    assert {str(m) for m in bp_moves} == {"pe6-e5"}

def test_black_pawn_double_move():
    bp = Pawn("B", *to_pos("e7"))
    b = Board([bp])
    bp_moves = bp.moves(b)
    assert {str(m) for m in bp_moves} == {"pe7-e6", "pe7-e5"}

def test_pawn_blocked():
    wp = Pawn("W", *to_pos("e4"))
    bp = Pawn("B", *to_pos("e5"))
    b = Board([wp, bp])
    assert {str(m) for m in wp.moves(b)} == set()
    assert {str(m) for m in bp.moves(b)} == set()

# ---- Pawn captures ----

def test_pawn_capture_moves():
    wp = Pawn("W", *to_pos("d5"))
    bp = Pawn("B", *to_pos("c6"))
    bp2 = Pawn("B", *to_pos("e6"))
    b = Board([wp, bp, bp2])
    wp_moves = wp.moves(b)
    assert {str(m) for m in wp_moves} == {"pd5-d6", "pd5xc6", "pd5xe6"}

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

# ---- For checks ----

def test_white_pawn_is_attacking():
    wp = Pawn("W", *to_pos("e4"))
    b = Board([wp])
    attacked = {to_square(Pos(y, x)) for y in range(8) for x in range(8) if wp.isAttacking(Pos(y, x), b)}
    assert attacked == {"d5", "f5"}

def test_black_pawn_is_attacking():
    bp = Pawn("B", *to_pos("e5"))
    b = Board([bp])
    attacked = {to_square(Pos(y, x)) for y in range(8) for x in range(8) if bp.isAttacking(Pos(y, x), b)}
    assert attacked == {"d4", "f4"}

# ---- Pawn promotion ----

def test_white_pawn_promotion_move():
    wp = Pawn("W", *to_pos("e7"))
    b = Board([wp])
    wp_moves = wp.moves(b)
    assert {str(m) for m in wp_moves} == {"pe7-e8=Q", "pe7-e8=R", "pe7-e8=B", "pe7-e8=N"}
    assert all(isinstance(m, Promotion) for m in wp_moves)

def test_white_pawn_capture_promotion():
    wp = Pawn("W", *to_pos("e7"))
    br = Rook("B", *to_pos("d8"))
    bn = Knight("B", *to_pos("e8"))
    b = Board([wp, br, bn])
    assert {str(m) for m in wp.moves(b)} == {"pe7xd8=Q", "pe7xd8=R", "pe7xd8=B", "pe7xd8=N"}

def test_black_pawn_promotion():
    bp = Pawn("B", *to_pos("e2"))
    b = Board([bp])
    bp_moves = bp.moves(b)
    assert {str(m) for m in bp_moves} == {"pe2-e1=Q", "pe2-e1=R", "pe2-e1=B", "pe2-e1=N"}
    assert all(isinstance(m, Promotion) for m in bp_moves)

def test_black_pawn_capture_promotion():
    bp = Pawn("B", *to_pos("e2"))
    wr = Rook("W", *to_pos("d1"))
    wn = Knight("W", *to_pos("e1"))
    b = Board([bp, wr, wn])
    assert {str(m) for m in bp.moves(b)} == {"pe2xd1=Q", "pe2xd1=R", "pe2xd1=B", "pe2xd1=N"}

# ---- En passant ----

def test_white_pawn_en_passant():
    wp = Pawn("W", *to_pos("e5"))
    bp = Pawn("B", *to_pos("d5"))
    b = Board([wp, bp])
    wp_moves = wp.moves(b)
    assert {str(m) for m in wp_moves} == {"pe5-e6", "pe5xd6"}
    assert EnPassant(wp, to_pos("d6"), bp) in wp_moves

def test_black_pawn_en_passant():
    bp = Pawn("B", *to_pos("e4"))
    wp = Pawn("W", *to_pos("d4"))
    b = Board([bp, wp])
    bp_moves = bp.moves(b)
    assert {str(m) for m in bp_moves} == {"pe4-e3", "pe4xd3"}
    assert EnPassant(bp, to_pos("d3"), wp) in bp_moves

def test_pawn_en_passant_does_not_replace_normal_capture():
    wp = Pawn("W", *to_pos("e5"))
    bp = Pawn("B", *to_pos("d5"))
    bn = Knight("B", *to_pos("d6"))
    b = Board([wp, bp, bn])
    wp_moves = wp.moves(b)
    assert NormalMove(wp, to_pos("d6"), bn) in wp_moves
    assert EnPassant(wp, to_pos("d6"), bp) in wp_moves

# ---- Bishop ----

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

def test_bishop_capture_moves():
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

# ---- Rook ----

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

def test_rook_capture_moves():
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

# ---- Queen ----

def test_queen_movement_empty_board():
    wq = Queen("W", *to_pos("d5"))
    b = Board([wq])
    wq_moves = wq.moves(b)
    assert {str(m) for m in wq_moves} == {
        "Qd5-d6", "Qd5-d7", "Qd5-d8", "Qd5-d4",
        "Qd5-d3", "Qd5-d2", "Qd5-d1", "Qd5-c5",
        "Qd5-b5", "Qd5-a5", "Qd5-e5", "Qd5-f5",
        "Qd5-g5", "Qd5-h5", "Qd5-e4", "Qd5-f3",
        "Qd5-g2", "Qd5-h1", "Qd5-c4", "Qd5-b3",
        "Qd5-a2", "Qd5-e6", "Qd5-f7", "Qd5-g8",
        "Qd5-c6", "Qd5-b7", "Qd5-a8",
    }

# ---- For checks ----
# All pieces besides pawns inherit the same func but use their own movement dirs.

def test_queen_is_attacking_empty_board():
    wq = Queen("W", *to_pos("d5"))
    b = Board([wq])
    attacked = {to_square(Pos(y, x)) for y in range(8) for x in range(8) if wq.isAttacking(Pos(y, x), b)}
    assert attacked == {
        "d6", "d7", "d8", "d4",
        "d3", "d2", "d1", "c5",
        "b5", "a5", "e5", "f5",
        "g5", "h5", "e4", "f3",
        "g2", "h1", "c4", "b3",
        "a2", "e6", "f7", "g8",
        "c6", "b7", "a8",
    }

def test_queen_is_attacking_stops_at_blocker():
    wq = Queen("W", *to_pos("d5"))
    bp = Pawn("B", *to_pos("d7"))
    bp2 = Pawn("B", *to_pos("f3"))
    b = Board([wq, bp, bp2])
    attacked = {to_square(Pos(y, x)) for y in range(8) for x in range(8) if wq.isAttacking(Pos(y, x), b)}
    assert attacked == {
        "d6", "d7", "d4", "d3",
        "d2", "d1", "c5", "b5",
        "a5", "e5", "f5", "g5",
        "h5", "e4", "f3", "c4",
        "b3", "a2", "e6", "f7",
        "g8", "c6", "b7", "a8",
    }

# ---- King ----

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

# ---- Knight ----

def test_knight_movement_empty_board():
    wn = Knight("W", *to_pos("d5"))
    b = Board([wn])
    wn_moves = wn.moves(b)
    assert {str(m) for m in wn_moves} == {
        "Nd5-c7", "Nd5-e7", "Nd5-f6", "Nd5-f4",
        "Nd5-e3", "Nd5-c3", "Nd5-b4", "Nd5-b6",
    }

# ---- For checks ----

def test_knight_is_attacking_over_pieces():
    wn = Knight("W", *to_pos("b1"))
    pawns = [Pawn("W", *to_pos(sq)) for sq in ("a2", "b2", "c2", "d2")]
    b = Board([wn, *pawns])
    attacked = {to_square(Pos(y, x)) for y in range(8) for x in range(8) if wn.isAttacking(Pos(y, x), b)}
    # d2 is defended even though the knight can't move there
    assert attacked == {"a3", "c3", "d2"}


# ---- Move applying and undoing ----

def test_normal_move_apply_and_undo():
    wr = Rook("W", *to_pos("e4"))
    b = Board([wr])
    m = NormalMove(wr, to_pos("g4"), None)
    m.apply(b)
    assert b.get_square(*to_pos("e4")) is None
    assert b.get_square(*to_pos("g4")) is wr
    assert wr.moved == 1
    m.undo(b)
    assert b.get_square(*to_pos("e4")) is wr
    assert b.get_square(*to_pos("g4")) is None
    assert wr.moved == 0

def test_normal_capture_apply_and_undo():
    wr = Rook("W", *to_pos("e4"))
    bp = Pawn("B", *to_pos("g4"))
    b = Board([wr, bp])
    m = NormalMove(wr, to_pos("g4"), bp)
    m.apply(b)
    assert b.get_square(*to_pos("e4")) is None
    assert b.get_square(*to_pos("g4")) is wr
    assert wr.moved == 1
    m.undo(b)
    assert b.get_square(*to_pos("e4")) is wr
    assert b.get_square(*to_pos("g4")) is bp
    assert wr.moved == 0

def test_en_passant_apply_and_undo():
    wp = Pawn("W", *to_pos("e5"))
    bp = Pawn("B", *to_pos("d5"))
    b = Board([wp, bp])
    m = EnPassant(wp, to_pos("d6"), bp)
    m.apply(b)
    assert b.get_square(*to_pos("e5")) is None
    assert b.get_square(*to_pos("d5")) is None
    assert b.get_square(*to_pos("d6")) is wp
    m.undo(b)
    assert b.get_square(*to_pos("e5")) is wp
    assert b.get_square(*to_pos("d5")) is bp
    assert b.get_square(*to_pos("d6")) is None

def test_promotion_apply_and_undo():
    wp = Pawn("W", *to_pos("e7"))
    wq = Queen("W", *to_pos("e8"))
    b = Board([wp])
    m = Promotion(wp, to_pos("e8"), None, wq)
    m.apply(b)
    assert b.get_square(*to_pos("e7")) is None
    assert b.get_square(*to_pos("e8")) is wq
    m.undo(b)
    assert b.get_square(*to_pos("e7")) is wp
    assert b.get_square(*to_pos("e8")) is None

def test_promotion_capture_apply_and_undo():
    wp = Pawn("W", *to_pos("e7"))
    br = Rook("B", *to_pos("d8"))
    wq = Queen("W", *to_pos("d8"))
    b = Board([wp, br])
    m = Promotion(wp, to_pos("d8"), br, wq)
    m.apply(b)
    assert b.get_square(*to_pos("e7")) is None
    assert b.get_square(*to_pos("d8")) is wq
    m.undo(b)
    assert b.get_square(*to_pos("e7")) is wp
    assert b.get_square(*to_pos("d8")) is br

def test_white_kingside_castle_apply_and_undo():
    wk = King("W", *to_pos("e1"))
    wr = Rook("W", *to_pos("h1"))
    b = Board([wk, wr])
    m = Castle(wk, "K")
    m.apply(b)
    assert b.get_square(*to_pos("e1")) is None
    assert b.get_square(*to_pos("h1")) is None
    assert b.get_square(*to_pos("g1")) is wk
    assert b.get_square(*to_pos("f1")) is wr
    assert wk.moved == 1 and wr.moved == 1
    m.undo(b)
    assert b.get_square(*to_pos("e1")) is wk
    assert b.get_square(*to_pos("h1")) is wr
    assert b.get_square(*to_pos("g1")) is None
    assert b.get_square(*to_pos("f1")) is None
    assert wk.moved == 0 and wr.moved == 0

def test_white_queenside_castle_apply_and_undo():
    wk = King("W", *to_pos("e1"))
    wr = Rook("W", *to_pos("a1"))
    b = Board([wk, wr])
    m = Castle(wk, "Q")
    m.apply(b)
    assert b.get_square(*to_pos("e1")) is None
    assert b.get_square(*to_pos("a1")) is None
    assert b.get_square(*to_pos("c1")) is wk
    assert b.get_square(*to_pos("d1")) is wr
    assert wk.moved == 1 and wr.moved == 1
    m.undo(b)
    assert b.get_square(*to_pos("e1")) is wk
    assert b.get_square(*to_pos("a1")) is wr
    assert b.get_square(*to_pos("c1")) is None
    assert b.get_square(*to_pos("d1")) is None
    assert wk.moved == 0 and wr.moved == 0

def test_black_kingside_castle_apply_and_undo():
    bk = King("B", *to_pos("e8"))
    br = Rook("B", *to_pos("h8"))
    b = Board([bk, br])
    m = Castle(bk, "K")
    m.apply(b)
    assert b.get_square(*to_pos("e8")) is None
    assert b.get_square(*to_pos("h8")) is None
    assert b.get_square(*to_pos("g8")) is bk
    assert b.get_square(*to_pos("f8")) is br
    assert bk.moved == 1 and br.moved == 1
    m.undo(b)
    assert b.get_square(*to_pos("e8")) is bk
    assert b.get_square(*to_pos("h8")) is br
    assert b.get_square(*to_pos("g8")) is None
    assert b.get_square(*to_pos("f8")) is None
    assert bk.moved == 0 and br.moved == 0

def test_black_queenside_castle_apply_and_undo():
    bk = King("B", *to_pos("e8"))
    br = Rook("B", *to_pos("a8"))
    b = Board([bk, br])
    m = Castle(bk, "Q")
    m.apply(b)
    assert b.get_square(*to_pos("e8")) is None
    assert b.get_square(*to_pos("a8")) is None
    assert b.get_square(*to_pos("c8")) is bk
    assert b.get_square(*to_pos("d8")) is br
    assert bk.moved == 1 and br.moved == 1
    m.undo(b)
    assert b.get_square(*to_pos("e8")) is bk
    assert b.get_square(*to_pos("a8")) is br
    assert b.get_square(*to_pos("c8")) is None
    assert b.get_square(*to_pos("d8")) is None
    assert bk.moved == 0 and br.moved == 0
