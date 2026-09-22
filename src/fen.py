from dataclasses import dataclass
from typing import TYPE_CHECKING
from pieces import Piece, Castle
from errors import InvalidFenError

if TYPE_CHECKING:
    from typedef import *

FILE = "abcdefgh"
KING_START_X = 4

class Fen:
    
    pieces: tuple[tuple[str,...]] # 8 x 8 grid
    turn: Team
    castle_rights: CastleRights
    en_passant: Pos | None
    half_turn: int 
    full_turn: int
    def __init__(self, fen: str):
        b, *state = fen.strip().split(" ")

        if len(state) < 3 or len(state) > 5:
            raise InvalidFenError()

        rows = b.split("/")
        if len(rows) != 8:
            raise InvalidFenError()
        
        board_grid: list[list[str]] = []

        for r in rows:
            squares: list[str] = []
            for c in r:
                if c in "12345678":
                    squares += [""] * int(c)
                elif c.upper() in "PRNBQK":
                    squares.append(c)
                else:
                    raise InvalidFenError()
                
            if len(squares) != 8:
                raise InvalidFenError()
            
            board_grid.append(squares)

        turn, castle, en_pass = state[0], state[1], state[2]

        if turn.upper() not in TEAMS:
            raise InvalidFenError()

        if castle != "-":
            if len(castle) > 4 or len(set(castle)) != len(castle):
                raise InvalidFenError()
            
            for c in castle:
                if c.upper() not in SIDES:
                    raise InvalidFenError()
                
                team: Team = "W" if c.isupper() else "B"
                side: Side = "K" if c.upper() == "K" else "Q"

                rook_start = Castle.CASTLE_POS[team][side].rook_start
                king_letter = "K" if team == "W" else "k"
                rook_letter = "R" if team == "W" else "r"

                if board_grid[rook_start.y][KING_START_X] != king_letter:
                    raise InvalidFenError()
                if board_grid[rook_start.y][rook_start.x] != rook_letter:
                    raise InvalidFenError()

        if en_pass != "-":
            if len(en_pass) != 2:
                raise InvalidFenError()
            if en_pass[0] not in FILE or en_pass[1] not in "36":
                raise InvalidFenError()
            x = FILE.index(en_pass[0])
            y = 8 - int(en_pass[1])

            if en_pass[1] == "6":
                mover, pawn, start_y, pawn_y = "W", "p", y - 1, y + 1
            else:
                mover, pawn, start_y, pawn_y = "B", "P", y + 1, y - 1
            if turn.upper() != mover:
                raise InvalidFenError()
            if board_grid[y][x] != "" or board_grid[start_y][x] != "" or board_grid[pawn_y][x] != pawn:
                raise InvalidFenError()

        for count in state[3:]:
            if not count.isdecimal():
                raise InvalidFenError()
            
        if len(state) == 5 and int(state[4]) < 1:
            raise InvalidFenError()

        return 

    def build_pieces(self) -> list[Piece]:
        pieces_obj = []
        return pieces_obj

DEFAULT_FEN = Fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")