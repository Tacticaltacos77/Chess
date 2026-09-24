from collections import defaultdict
from pieces import Piece, Rook, PIECE_BY_LETTER, Castle
from errors import InvalidFenError
from helper import to_square, to_pos
from typedef import *


FILE = "abcdefgh"
KING_START_X = 4

class Fen:
    placement: list[tuple[str, Pos]]
    turn: Team
    castle_rights: set[str]
    en_passant: Pos | None
    half_turn: int 
    full_turn: int

    def __init__(self, fen: str):
        b, *state = fen.strip().split(" ")

        # Verify structure of the fen str
        if len(state) < 3 or len(state) > 5:
            raise InvalidFenError(f"expected 4 to 6 space separated fields, got {len(state) + 1}: {fen}")
        
        # Verify the stucture of the board
        rows = b.split("/")
        if len(rows) != 8:
            raise InvalidFenError(f"expected 8 ranks separated by '/', got {len(rows)}: {b}")

        board_grid: list[list[str]] = []
        self.placement = []

        for r in range(8):
            squares: list[str] = []
            row = rows[r]
            for c in row:
                if c in "12345678":
                    squares += [""] * int(c)
                elif c.upper() in "PRNBQK":
                    self.placement.append((c, Pos(r, len(squares))))
                    squares.append(c)
                else:
                    raise InvalidFenError(f"rank {8 - r}: {c} is not a piece letter or a digit 1-8")

            if len(squares) != 8:
                raise InvalidFenError(f"rank {8 - r} describes {len(squares)} files, expected 8: {row}")

            board_grid.append(squares)
        counter = defaultdict(int)

        # Verify piece count
        for p, pos in self.placement:
            if p.upper() == "P" and pos.y in (0, 7):
                raise InvalidFenError(f"a pawn cannot be on rank {8-pos.y}, it would have promoted")
            counter[p]+=1
        
        for name, king, pawn in (("white", "K", "P"), ("black", "k", "p")):
            if counter[king] != 1:
                raise InvalidFenError(f"expected exactly 1 {name} king, got {counter[king]}")
            total = 0
            for l in PIECE_BY_LETTER:
                total+= counter[l.upper()] if name == "white" else counter[l.lower()]
            if total > 16:
                raise InvalidFenError(f"expected at most 16 total pieces for {name}, got {total}")
            if counter[pawn] > 8:
                raise InvalidFenError(f"expected at most 8 {name} pawns, got {counter[pawn]}")
            
        turn, castle, en_pass = state[0].upper(), state[1], state[2]
        
        if turn not in TEAMS:
            raise InvalidFenError(f"{turn} is not a side to move, expected 'w' or 'b'")
        self.turn = turn

        self.castle_rights = set()
        if castle != "-":
            # Verify structure
            if len(castle) > 4 or len(set(castle)) != len(castle):
                raise InvalidFenError(f"{castle} is not a castling field, expected up to 4 unique rights or '-'")
            
            for c in castle:
                if c.upper() not in SIDES:
                    raise InvalidFenError(f"{c} is not a castling right, expected one of 'KQkq'")
                # Verify Leagality
                team: Team = "W" if c.isupper() else "B"
                side: Side = "K" if c.upper() == "K" else "Q"

                rook_start = Castle.CASTLE_POS[team][side].rook_start
                king_letter = "K" if team == "W" else "k"
                rook_letter = "R" if team == "W" else "r"

                if board_grid[rook_start.y][KING_START_X] != king_letter:
                    raise InvalidFenError(f"castling right {c} needs {king_letter} on "
                                          f"{to_square(Pos(rook_start.y, KING_START_X))}")
                
                if board_grid[rook_start.y][rook_start.x] != rook_letter:
                    raise InvalidFenError(f"castling right {c} needs {rook_letter} on {to_square(rook_start)}")
                self.castle_rights.add(c)

        self.en_passant = None
        
        if en_pass != "-":
            # Verify Structure
            try:
                ep_pos = to_pos(en_pass)

            except ValueError as e:
                raise InvalidFenError(f"{en_pass} is not a square name") from e

            if ep_pos.y not in (2, 5):
                raise InvalidFenError(f"{en_pass} is not an en passant square, its rank must be 3 or 6")
            # Verify Leagality
            if ep_pos.y == 2:
                color, pawn, start_y, pawn_y = "W", "p", ep_pos.y - 1, ep_pos.y + 1
            else:
                color, pawn, start_y, pawn_y = "B", "P", ep_pos.y + 1, ep_pos.y - 1

            if turn.upper() != color:
                raise InvalidFenError(f"en passant on {en_pass} means {color} is to move, but the FEN says {turn}")

            if board_grid[ep_pos.y][ep_pos.x] != "" or board_grid[start_y][ep_pos.x] != "" or board_grid[pawn_y][ep_pos.x] != pawn:
                raise InvalidFenError(f"en passant on {en_pass} needs {pawn} on {to_square(Pos(pawn_y, ep_pos.x))} "
                                      f"with {to_square(Pos(start_y, ep_pos.x))} and {en_pass} empty")

            self.en_passant = ep_pos

        for count in state[3:]:
            if not count.isdecimal():
                raise InvalidFenError(f"{count} is not a move counter, expected a non negative whole number")

        self.half_turn = int(state[3]) if len(state) > 3 else 0
        self.full_turn = int(state[4]) if len(state) > 4 else 1

        if self.full_turn < 1:
            raise InvalidFenError(f"the full move number must be at least 1, got {self.full_turn}")
        
    # Builds a list of pieces for a game object to use. This is to allow for one fen to be used on many game objects.
    def build_pieces(self) -> list[Piece]:
        pieces = []
        for p_str, pos in self.placement:
            cls = PIECE_BY_LETTER[p_str.lower()]

            color = "W" if p_str.isupper() else "B"
            piece = cls(color, pos.y, pos.x)

            # Sets the moved flag based on rights
            if isinstance(piece, Rook):
                side = "K" if pos.x == 7 else "Q"
                rights = side if color == "W" else side.lower()
                if pos != Castle.CASTLE_POS[color][side].rook_start or rights not in self.castle_rights:
                    piece.moved = 1 
                
            pieces.append(piece)
        return pieces
    


DEFAULT_FEN = Fen("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")