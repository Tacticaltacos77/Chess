from pieces import Rook, Bishop, Knight, Pawn, Queen, King, Piece, Pos, Capturable
from typing import TYPE_CHECKING
from errors import IllegalBoardStateError

if TYPE_CHECKING:
    from typedef import *

class Board:
    board: list[list[None|Piece]]
    def __init__(self, pieces: list[Piece]):
        self.set_board(pieces)
        
    def __str__(self):
        board = []
        for y in range(8):
            for x in range(8):
                board.append(str(self.board[y][x]))
                if x!=7:
                    board.append(" ")
            if y!=7:
                board.append("\n")
        return "".join(board)

    def get_board(self) -> list[list[str]]:
        board = [[] for _ in range(8)]
        for y in range(8):
            for x in range(8):
                v = self.board[y][x]
                if not v:
                    v = ""
                board[y].append(str(v))
        return board

    def get_square(self, y: int, x: int) -> Piece|None:
        if not (0 <= y < 8 and 0 <= x < 8):
            return None
        return self.board[y][x]
    
    def set_board(self, both_team_pieces: list[Piece]):
        self.board = [[None, None, None, None, None, None, None, None],
                      [None, None, None, None, None, None, None, None],
                      [None, None, None, None, None, None, None, None], 
                      [None, None, None, None, None, None, None, None],
                      [None, None, None, None, None, None, None, None],
                      [None, None, None, None, None, None, None, None], 
                      [None, None, None, None, None, None, None, None],
                      [None, None, None, None, None, None, None, None]]
        
        for piece in both_team_pieces:
            self.place_piece(piece)
    
    def place_piece(self, p: Piece) -> None:
        end_square_val = self.get_square(p.pos.y, p.pos.x)
        if end_square_val:
            raise IllegalBoardStateError(f"Tried to place {p} at ({p.pos}), but there was {end_square_val} already there")
        self.board[p.pos.y][p.pos.x] = p


    def move_piece(self, p:Piece, end:Pos)->None:
        self.remove_piece(p)
        p.set_pos(end)
        self.place_piece(p)
        
    
    def cap_piece(self, p:Piece, end: Pos, cap_p: Capturable) -> Capturable:
        if p.color == cap_p.color:
            raise IllegalBoardStateError(f"{p} tried to capture {cap_p} which is the same color")

        if not isinstance(cap_p, Capturable):
            raise IllegalBoardStateError(f"{p} tried to capture {cap_p}, which is not capturable")

        cap_piece_v = self.remove_piece(cap_p)

        if cap_piece_v != cap_p:
            raise IllegalBoardStateError(f"expected to remove {cap_p} from ({cap_p.pos.y}, {cap_p.pos.x}), "
                                         f"but removed {cap_piece_v}")
        
        self.remove_piece(p)
        p.set_pos(end)
        self.place_piece(p) 
        return cap_p
    
    def remove_piece(self, p: Piece)->Piece:
        rmv_p = self.board[p.pos.y][p.pos.x]
        if not isinstance(rmv_p, Piece):
            raise IllegalBoardStateError(f"Tried to remove {p}, from ({p.pos.y, p.pos.x}), but there was {rmv_p} was there instead")
        
        self.board[p.pos.y][p.pos.x] = None
        return rmv_p

