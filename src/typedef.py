from typing import Literal, NamedTuple


## Redo to be enums
type Team = Literal["W", "B"]
"""Team Colors"""
type Side = Literal["K", "Q"] 
"""Sides of the chess board"""

type Sides[T] = dict[Side, T]
"""A container for both sides"""
type Teams[T] = dict[Team, T]
"""A container for both of the teams"""
type CastleRights = Teams[dict[Side, bool]]
""""""
type SquareColor = Literal["light", "dark"]

type GameStatus = Literal["in_progress", "checkmate", "stalemate", "draw_50_move", "draw_repetion", "draw_insufficent_material"]

TEAMS = ("W","B")
SIDES = ("K","Q")

class Pos(NamedTuple):
    """(y, x) coordinates on the chess board."""
    y: int
    x: int

class CastleSquares(NamedTuple):
    rook_start: Pos
    rook_end: Pos
    king_end: Pos
    must_be_empty: tuple[Pos, ...]
    must_be_unattacked: tuple[Pos, ...]