from typing import Literal
type Team = Literal["W"] | Literal["B"]
"""Team Colors"""
type Side = Literal["K"] | Literal["Q"]
"""Sides of the chess board"""
type Sides[T] = dict[Side, T]
"""A container for both sides"""
type Teams[T] = dict[Team, T]
"""A container for both of the teams"""
type CastleRights = Teams[dict[Side, bool]]