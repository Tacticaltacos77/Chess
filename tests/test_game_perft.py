import pytest

from chesslibrary.game import Game

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

    g = Game()
    assert perft(g, 1) == 20
    assert perft(g, 2) == 400
    assert perft(g, 3) == 8902
    assert perft(g, 4) == 197281
    assert perft(g, 5) == 4865609
    assert perft(g, 6) == 119060324