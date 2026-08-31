from typing import Literal
type Team = Literal["W", "B"]
"""Team Colors"""
type Side = Literal["K", "Q"] 
"""Sides of the chess board"""
type Sides[T] = dict[Side, T]
"""A container for both sides"""
type Teams[T] = dict[Team, T]
"""A container for both of the teams"""
type CastleRights = Teams[dict[Side, bool]]

type GameStatus = Literal["in_progress", "checkmate", "stalemate", "draw_50_move", "draw_repetion", "draw_insufficent_material"]