import pytest

from game import Game, Status
from pieces import *
from errors import IllegalMoveError, IllegalGameStateError
from helper import to_pos

START_FEN = "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1"

# ---- Setup ----

def test_start_position():
    g = Game(START_FEN)
    assert g.color_turn == "W"
    assert g.full_turn == 1
    assert g.status == Status.ACTIVE
    assert g.half_turn_history == [0]
    assert g.enPassentHistory == [None]
    assert g.move_history == []
    assert g.positions == {START_FEN.rsplit(" ", 2)[0]: 1}
    assert {str(m) for ms in g.get_curr_turn_moves().values() for m in ms} == {
        "pa2-a3", "pa2-a4", "pb2-b3", "pb2-b4",
        "pc2-c3", "pc2-c4", "pd2-d3", "pd2-d4",
        "pe2-e3", "pe2-e4", "pf2-f3", "pf2-f4",
        "pg2-g3", "pg2-g4", "ph2-h3", "ph2-h4",
        "Nb1-a3", "Nb1-c3", "Ng1-f3", "Ng1-h3",
    }

def test_castle_rights_from_fen():
    g = Game("r3k2r/8/8/8/8/8/8/R3K2R w Kq - 0 1")
    assert g.castle_rights == {"K", "q"}

    g = Game("r3k2r/8/8/8/8/8/8/R3K2R w Qk - 0 1")
    assert g.castle_rights == {"Q", "k"}

    g = Game("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    assert g.castle_rights == {"Q", "K", "q", "k"}

    g = Game("r3k2r/8/8/8/8/8/8/R3K2R w - - 0 1")
    assert g.castle_rights == set()
    
# ---- Turns ----

def test_make_move_switches_turn_and_full_turn():
    g = Game(START_FEN)
    g.make_move(NormalMove(g.board.get_piece(*to_pos("g1")), to_pos("f3"), None))
    assert g.color_turn == "B"
    assert g.full_turn == 1
    g.make_move(NormalMove(g.board.get_piece(*to_pos("g8")), to_pos("f6"), None))
    assert g.color_turn == "W"
    assert g.full_turn == 2

def test_make_move_rejects_illegal_move():
    g = Game(START_FEN)
    wp = g.board.get_piece(*to_pos("e2"))
    with pytest.raises(IllegalMoveError):
        g.make_move(NormalMove(wp, to_pos("e5"), None))
    assert g.board.get_square(*to_pos("e2")) is wp

def test_make_move_after_game_over_raises():
    g = Game("4k3/8/8/8/8/8/8/4K3 w - - 0 1")
    with pytest.raises(IllegalGameStateError):
        g.make_move(NormalMove(g.kings["W"], to_pos("e2"), None))

# ---- Half turn clock ----

def test_half_turn_increments():
    g = Game(START_FEN)
    g.make_move(NormalMove(g.board.get_piece(*to_pos("g1")), to_pos("f3"), None))
    assert g.half_turn_history[-1] == 1

def test_half_turn_resets_on_pawn_move():
    g = Game(START_FEN)
    g.make_move(NormalMove(g.board.get_piece(*to_pos("g1")), to_pos("f3"), None))
    g.make_move(NormalMove(g.board.get_piece(*to_pos("e7")), to_pos("e5"), None))
    assert g.half_turn_history[-1] == 0

def test_half_turn_resets_on_capture():
    g = Game("r3k3/8/8/8/8/8/8/R3K3 w - - 5 1")
    br = g.board.get_piece(*to_pos("a8"))
    g.make_move(NormalMove(g.board.get_piece(*to_pos("a1")), to_pos("a8"), br))
    assert g.half_turn_history[-1] == 0

# ---- Full turn ----

def test_full_turn_change_on_black_move():
    g = Game("4k3/8/8/8/8/8/8/R3K3 b - - 0 7")
    assert g.full_turn == 7
    g.make_move(NormalMove(g.kings["B"], to_pos("d8"), None))
    assert g.full_turn == 8
    g.undo_move()
    assert g.full_turn == 7

# ---- Team state ----

def test_capture_moves_piece_to_lost_pieces():
    g = Game("r3k3/8/8/8/8/8/8/R3K3 w - - 0 1")
    br = g.board.get_square(*to_pos("a8"))
    g.make_move(NormalMove(g.board.get_piece(*to_pos("a1")), to_pos("a8"), br))
    assert br not in g.board.get_pieces("B")
    

def test_promotion_replaces_pawn_in_team():
    g = Game("4k3/P7/8/8/8/8/8/4K3 w - - 0 1")
    wp = g.board.get_square(*to_pos("a7"))
    promo = {str(m): m for m in g.get_curr_turn_moves()[to_pos("a7")]}["pa7-a8=Q"]
    assert isinstance(promo, Promotion)
    g.make_move(promo)
    assert wp not in g.board.get_pieces()
    assert promo.promo_piece in g.board.get_pieces()

# ---- Undo ----

def test_undo_normal_move():
    g = Game(START_FEN)
    start_moves = {str(m) for ms in g.get_curr_turn_moves().values() for m in ms}
    wn = g.board.get_piece(*to_pos("g1"))
    bn = g.board.get_piece(*to_pos("g8"))
    g.make_move(NormalMove(wn, to_pos("f3"), None))
    g.make_move(NormalMove(bn, to_pos("f6"), None))
    g.undo_move()
    assert g.board.get_square(*to_pos("g8")) is bn
    assert g.board.get_square(*to_pos("f6")) is None
    assert g.color_turn == "B"
    assert g.full_turn == 1
    g.undo_move()
    assert g.board.get_square(*to_pos("g1")) is wn
    assert g.board.get_square(*to_pos("f3")) is None
    assert g.color_turn == "W"
    assert g.full_turn == 1
    assert {str(m) for ms in g.get_curr_turn_moves().values() for m in ms} == start_moves

def test_undo_capture():
    g = Game("r3k3/8/8/8/8/8/8/R3K3 w - - 0 1")
    wr = g.board.get_piece(*to_pos("a1"))
    br = g.board.get_piece(*to_pos("a8"))
    g.make_move(NormalMove(wr, to_pos("a8"), br))
    g.undo_move()
    assert g.board.get_piece(*to_pos("a1")) is wr
    assert g.board.get_piece(*to_pos("a8")) is br
    assert br in g.board.get_pieces("B")
    

def test_undo_promotion():
    g = Game("4k3/P7/8/8/8/8/8/4K3 w - - 0 1")
    wp = g.board.get_square(*to_pos("a7"))
    promo = {str(m): m for m in g.get_curr_turn_moves()[to_pos("a7")]}["pa7-a8=Q"]
    assert isinstance(promo, Promotion)
    g.make_move(promo)
    g.undo_move()
    assert g.board.get_square(*to_pos("a7")) is wp
    assert g.board.get_square(*to_pos("a8")) is None
    w_pieces = g.board.get_pieces("W")
    assert wp in w_pieces
    assert promo.promo_piece not in w_pieces
###
def test_undo_restores_half_turn_and_en_passant():
    g = Game(START_FEN)
    g.make_move(NormalMove(g.board.get_piece(*to_pos("e2")), to_pos("e4"), None))
    g.make_move(NormalMove(g.board.get_piece(*to_pos("g8")), to_pos("f6"), None))
    g.undo_move()
    assert g.half_turn_history[-1] == 0
    assert g.enPassentHistory[-1] == to_pos("e3")

# ---- Check and legal moves ----

def test_king_in_check():
    g = Game("4k3/8/8/8/8/8/8/4K2r w - - 0 1")
    assert g.king_in_check(g.kings["W"])
    assert not g.king_in_check(g.kings["B"])

def test_pinned_piece_cannot_move():
    g = Game("4r1k1/8/8/8/8/8/4N3/4K3 w - - 0 1")
    assert g.allowed_moves_history[-1][to_pos("e2")] == []

def test_must_get_out_of_check():
    g = Game("4k3/8/8/8/8/8/PPP5/4K2r w - - 0 1")
    assert {str(m) for ms in g.get_curr_turn_moves().values() for m in ms} == {"Ke1-d2", "Ke1-e2", "Ke1-f2"}

def test_king_cannot_move_into_check():
    g = Game("4k3/8/8/8/8/8/r7/4K3 w - - 0 1")
    assert {str(m) for ms in g.get_curr_turn_moves().values() for m in ms} == {"Ke1-d1", "Ke1-f1"}

# ---- En passant ----

def test_en_passant_legal_right_after_double_move():
    g = Game("4k3/3p4/8/4P3/8/8/8/4K3 b - - 0 1")
    wp = g.board.get_piece(*to_pos("e5"))
    bp = g.board.get_piece(*to_pos("d7"))
    g.make_move(NormalMove(bp, to_pos("d5"), None))
    assert EnPassant(wp, to_pos("d6"), bp) in g.get_curr_turn_moves()[to_pos("e5")]

def test_en_passant_expires_after_one_turn():
    g = Game("4k3/3p4/8/4P3/8/8/8/4K3 b - - 0 1")
    wp = g.board.get_piece(*to_pos("e5"))
    bp = g.board.get_piece(*to_pos("d7"))
    g.make_move(NormalMove(bp, to_pos("d5"), None))
    g.make_move(NormalMove(g.kings["W"], to_pos("d1"), None))
    g.make_move(NormalMove(g.kings["B"], to_pos("f8"), None))
    assert EnPassant(wp, to_pos("d6"), bp) not in g.get_curr_turn_moves()[to_pos("e5")]

def test_en_passant_illegal_if_it_exposes_king():
    g = Game("4k3/2p5/8/KP5r/8/8/8/8 b - - 0 1")
    wp = g.board.get_piece(*to_pos("b5"))
    bp = g.board.get_piece(*to_pos("c7"))
    g.make_move(NormalMove(bp, to_pos("c5"), None))
    # Taking removes both pawns from the 5th rank and opens the rook onto the king
    assert g.enPassentHistory[-1] == to_pos("c6")
    assert EnPassant(wp, to_pos("c6"), bp) not in g.get_curr_turn_moves()[to_pos("b5")]

# ---- Castling ----

def test_castle_legal():
    g = Game("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    wk = g.kings["W"]
    assert Castle(wk, "K") in g.get_curr_turn_moves()[to_pos("e1")]
    assert Castle(wk, "Q") in g.get_curr_turn_moves()[to_pos("e1")]

def test_castle_blocked_by_piece():
    g = Game("r3k2r/8/8/8/8/8/8/RN2K2R w KQkq - 0 1")
    wk = g.kings["W"]
    assert Castle(wk, "K") in g.get_curr_turn_moves()[to_pos("e1")]
    assert Castle(wk, "Q") not in g.get_curr_turn_moves()[to_pos("e1")]

def test_castle_illegal_while_in_check():
    g = Game("r3k2r/8/8/8/4r3/8/8/R3K2R w KQkq - 0 1")
    wk = g.kings["W"]
    assert Castle(wk, "K") not in g.get_curr_turn_moves()[to_pos("e1")]
    assert Castle(wk, "Q") not in g.get_curr_turn_moves()[to_pos("e1")]

def test_castle_illegal_through_attacked_square():
    g = Game("r3k2r/8/8/8/5r2/8/8/R3K2R w KQkq - 0 1")
    wk = g.kings["W"]
    assert Castle(wk, "K") not in g.get_curr_turn_moves()[to_pos("e1")]
    assert Castle(wk, "Q") in g.get_curr_turn_moves()[to_pos("e1")]

def test_castle_rights_lost_after_king_moves():
    g = Game("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    g.make_move(NormalMove(g.kings["W"], to_pos("f1"), None))
    assert g.castle_rights == {"k", "q"}

def test_castle_rights_lost_after_rook_moves():
    g = Game("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    g.make_move(NormalMove(g.board.get_piece(*to_pos("h1")), to_pos("h2"), None))
    assert g.castle_rights == {"Q", "k", "q"}

def test_castle_rights_lost_when_rook_captured():
    g = Game("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
    br = g.board.get_square(*to_pos("a8"))
    g.make_move(NormalMove(g.board.get_piece(*to_pos("a1")), to_pos("a8"), br))
    assert g.castle_rights == {"K", "k"}

# ---- Game status ----

def test_white_checkmate():
    g = Game("6k1/5ppp/8/8/8/8/8/R3K3 w - - 0 1")
    g.make_move(NormalMove(g.board.get_piece(*to_pos("a1")), to_pos("a8"), None))
    assert g.status == Status.WHITE_CHECKMATE

def test_black_checkmate():
    g = Game("r3k3/8/8/8/8/8/5PPP/6K1 b - - 0 1")
    g.make_move(NormalMove(g.board.get_piece(*to_pos("a8")), to_pos("a1"), None))
    assert g.status == Status.BLACK_CHECKMATE

def test_stalemate():
    g = Game("7k/8/8/8/8/8/8/4K1Q1 w - - 0 1")
    g.make_move(NormalMove(g.board.get_piece(*to_pos("g1")), to_pos("g6"), None))
    assert g.status == Status.STALEMATE

def test_fifty_move_draw():
    g = Game("4k3/8/8/8/8/8/8/R3K3 w - - 99 50")
    g.make_move(NormalMove(g.board.get_piece(*to_pos("a1")), to_pos("a2"), None))
    assert g.status == Status.DRAW_FIFTY_MOVE

def test_insufficient_material_kings_only():
    g = Game("4k3/8/8/8/8/8/8/4K3 w - - 0 1")
    assert g.status == Status.DRAW_INSUFFICIENT_MATERIAL

def test_insufficient_material_single_minor_piece():
    g = Game("4k3/8/8/8/8/8/8/2B1K3 w - - 0 1")
    assert g.status == Status.DRAW_INSUFFICIENT_MATERIAL

def test_insufficient_material_same_color_bishops():
    g = Game("4kb2/8/8/8/8/8/8/2B1K3 w - - 0 1")
    assert g.status == Status.DRAW_INSUFFICIENT_MATERIAL

def test_opposite_color_bishops_is_sufficient_material():
    g = Game("2b1k3/8/8/8/8/8/8/2B1K3 w - - 0 1")
    assert g.status == Status.ACTIVE

def test_threefold_repetition():
    g = Game(START_FEN)
    for start, end in [("g1", "f3"), ("g8", "f6"), ("f3", "g1"), ("f6", "g8")] * 2:
        g.make_move(NormalMove(g.board.get_piece(*to_pos(start)), to_pos(end), None))
    assert g.status == Status.DRAW_REPETITION

# ---- Positions ----

def test_get_fen():
    for fen in [START_FEN, "r3k2r/8/8/8/8/8/8/R3K2R b Kq - 5 20"]:
        assert Game(fen).get_fen() == fen

def test_undo_removes_position():
    g = Game(START_FEN)
    shuffle = [("g1", "f3"), ("g8", "f6"), ("f3", "g1"), ("f6", "g8")]
    for start, end in shuffle:
        g.make_move(NormalMove(g.board.get_piece(*to_pos(start)), to_pos(end), None))
    for _ in shuffle:
        g.undo_move()
    for start, end in shuffle:
        g.make_move(NormalMove(g.board.get_piece(*to_pos(start)), to_pos(end), None))
    # Start position has only been reached twice, the undone visit shouldn't count
    assert g.status == Status.ACTIVE

def test_unusable_en_passant_square_does_not_change_position():
    g = Game("4k3/8/8/8/8/8/4P3/4K3 w - - 0 1")
    g.make_move(NormalMove(g.board.get_piece(*to_pos("e2")), to_pos("e4"), None))
    # No black pawn can take on e3, so this is the same position as after each king shuffle
    for start, end in [("e8", "d8"), ("e1", "d1"), ("d8", "e8"), ("d1", "e1")] * 2:
        g.make_move(NormalMove(g.board.get_piece(*to_pos(start)), to_pos(end), None))
    assert g.status == Status.DRAW_REPETITION

# ---- Perft Move Count----

def test_perft_start_position():
    def perft(g: Game, depth: int) -> int:
        if depth == 0:
            return 1
        total = 0
        for move_list in g.get_curr_turn_moves().values():
            for move in move_list:
                g.make_move(move)
                total += perft(g, depth - 1)
                g.undo_move()
        return total

    g = Game(START_FEN)
    assert perft(g, 1) == 20
    assert perft(g, 2) == 400
    assert perft(g, 3) == 8902
    assert perft(g, 4) == 197281