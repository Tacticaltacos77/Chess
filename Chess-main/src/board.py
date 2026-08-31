from pieces import Rook, Bishop, Knight, Pawn, Queen, King, Piece, Pos, Capturable
from typing import TYPE_CHECKING
from errors import IllegalBoardStateError
if TYPE_CHECKING:
    from typedef import *
    
class Board:
    board: list[list[None|Piece]]
    def __init__(self, pieces: Teams[list[Piece]]):
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
    
    def get_square(self, y: int, x: int) -> Piece|None:
        return self.board[y][x]

    def get_piece(self, p: Piece) -> Piece:
        board_val = self.board[p.pos.y][p.pos.x] 
        if not isinstance(board_val, Piece):
            raise IllegalBoardStateError("Epected a piece at ")
        return board_val
    
    def set_board(self, both_team_pieces: Teams[list[Piece]]):
        self.board = [[None, None, None, None, None, None, None, None],
                      [None, None, None, None, None, None, None, None],
                      [None, None, None, None, None, None, None, None], 
                      [None, None, None, None, None, None, None, None],
                      [None, None, None, None, None, None, None, None],
                      [None, None, None, None, None, None, None, None], 
                      [None, None, None, None, None, None, None, None],
                      [None, None, None, None, None, None, None, None]]
        
        for team_pieces in both_team_pieces.values():
            for piece in team_pieces:
                prev_square_val = self.place_piece(piece)
                if prev_square_val !=None:
                    print(f"Replaced {prev_square_val} with {piece}")
                
    def place_piece(self, p: Piece) -> None:
        end_square_val = self.get_square(p.pos.y, p.pos.x)
        if end_square_val:
            raise IllegalBoardStateError(f"Tried to place {p} at ({p.pos}), but there was {end_square_val} already there")
        self.board[p.pos.y][p.pos.x] = p


    def move_piece(self, p:Piece, end:Pos)->None:
        self.remove_piece(p)
        p.set_pos(end)
        self.place_piece(p)
        
    
    def cap_piece(self, p:Piece, end: Pos, cap_p: Capturable)->Capturable:
        try:
            cap_piece_value = self.remove_piece(cap_p) 
        except:
            raise IllegalBoardStateError(f"{p} tried to move to ({p.pos}) capture a {cap_p} at ({cap_p.pos}), but there was nothing there")
        if p.color == cap_p.color:
            raise IllegalBoardStateError(f"{p} tried to capture {cap_p} which is the same color")
        if not isinstance(cap_piece_value, Capturable):
            raise IllegalBoardStateError(f"{p} tried to capture the enemy King at ({end})")
        self.remove_piece(p)
        p.set_pos(end)
        self.place_piece(p) 
        return cap_piece_value
    
    def remove_piece(self, p: Piece)->Piece:
        rmv_p = self.board[p.pos.y][p.pos.x]
        if not isinstance(rmv_p,Piece) or rmv_p !=p:
            raise IllegalBoardStateError(f"Tried to remove {p}, from ({p.pos.y, p.pos.x}), but there was {rmv_p} was there instead")
        self.board[p.pos.y][p.pos.x] = None
        return rmv_p

