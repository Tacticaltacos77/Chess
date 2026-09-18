from typing import TYPE_CHECKING, ClassVar
from typedef import Pos, CastleSquares
from dataclasses import dataclass, field
from abc import ABC, abstractmethod
if TYPE_CHECKING:
    from board import Board
    from gameState import GameState  
    from typedef import *

class Piece:
    moveDir: tuple[Pos, ...]
    maxMove: int
    def __init__(self, color: Team, y: int, x: int):
        self.color: Team = color
        self.pos: Pos = Pos(y, x)
        self.moved = 0

    def moves(self, b: Board, gS: GameState)->list[Move]:
        moves = []
        for dir in self.moveDir:
            currMove = self.maxMove
            y, x = self.pos.y, self.pos.x
            while currMove > 0 and 0 <= y + dir[0] < 8 and 0 <= x+ dir[1] <8:
                currMove -= 1
                y += dir[0]
                x += dir[1]
                end_square = b.get_square(y, x)
                if end_square == None:
                    moves.append(NormalMove(self, Pos(y, x), capture=None))
                elif isinstance(end_square, Capturable):
                    moves.append(NormalMove(self, Pos(y, x), capture=end_square))
                    break
                else:
                    break
        return moves
    def isAttacking(self, end_square: Pos, b:Board)->bool:
        end_y, end_x = end_square
        for y_atk_dir, x_atk_dir in self.moveDir:
            cur_y_dis = abs(end_y-self.pos.y)
            cur_x_dis = abs(end_x-self.pos.x)
            new_y_dis = abs(end_y - (self.pos.y + y_atk_dir))
            new_x_dis = abs(end_x - (self.pos.x + x_atk_dir))
            if cur_y_dis < new_y_dis or cur_x_dis < new_x_dis:
                continue
            currMove = self.maxMove
            y, x = self.pos.y, self.pos.x
            while currMove > 0 and 0 <= y + y_atk_dir < 8 and 0 <= x + x_atk_dir <8:
                currMove-=1
                y += y_atk_dir
                x += x_atk_dir
                if y == end_y and x == end_x:
                    return True
                if b.get_square(y, x)!=None:
                    break
        return False
    
    def set_pos(self, end_pos: Pos):
        if not isinstance(end_pos, Pos):
            raise ValueError()
        self.pos = end_pos

    def has_moved(self)->bool:
        return self.moved !=0
    
class Capturable(Piece):
    pass
    
class Rook(Capturable):
    maxMove =7
    moveDir = (Pos(0,1),Pos(1,0),Pos(-1,0),Pos(0,-1))
    def __init__(self, color:Team, y:int, x:int):
        super().__init__(color, y, x)
        self.moved = 0
    def __str__(self):
        if self.color == "W":
            return "r"
        else:
            return "R" 
        
class Knight(Capturable):
    maxMove =1
    moveDir = (Pos(1,2),Pos(1,-2),Pos(2,1),Pos(2,-1),Pos(-2,-1),Pos(-2,1),Pos(-1,2),Pos(-1,-2))
    def __init__(self, color: Team, y:int, x:int):
        super().__init__(color, y, x)
    def __str__(self):
        if self.color == "W":
            return "n"
        else:
            return "N"
     
class Bishop(Capturable):
    maxMove =7
    moveDir = (Pos(1,1), Pos(1,-1), Pos(-1,1), Pos(-1,-1))
    def __init__(self, color: Team, y:int, x:int):
        super().__init__(color, y, x)
    def __str__(self):
        if self.color == "W":
            return "b"
        else:
            return "B"
        
class Queen(Capturable):
    maxMove =7
    moveDir = (Pos(0,1),Pos(1,0),Pos(-1,0),Pos(0,-1),Pos(1,1),Pos(1,-1),Pos(-1,1),Pos(-1,-1))
    def __init__(self, color: Team, y:int, x:int):
        super().__init__(color, y, x)
    def __str__(self):
        if self.color == "W":
            return "q"
        else:
            return "Q"
        
class King(Piece):
    maxMove =1
    moveDir = (Pos(0,1),Pos(1,0),Pos(-1,0),Pos(0,-1),Pos(1,1),Pos(1,-1),Pos(-1,1),Pos(-1,-1))
    def __init__(self, color: Team, y:int, x: int):
        super().__init__(color, y, x)
        self.moved = 0
    def __str__(self):
        if self.color == "W":
            return "k"
        else:
            return "K"
        
    def moves(self, b: Board, gS: GameState)->list[Move]:
        moves = super().moves(b, gS)
        for castle_dir in ("Q","K"):
            if gS.team_state[self.color].castle_rights[castle_dir]:
                moves.append(Castle(self, castle_dir))
        return moves
    
class Pawn(Capturable):
    maxMove = 1
    forwardDir:int
    attackDir = Pos(-1, 1)
    PROMOTION_PIECES_CONS = (Queen, Rook, Bishop, Knight)
    PROMOTION_ROW = {"W": 0, "B": 7}
    
    def __init__(self, color, y, x):
        super().__init__(color, y, x)
        self.moved = 0
        if color == "W":
            self.forward_dir = -1
        else:
            self.forward_dir = 1

    def moves(self, b: Board, gS: GameState)-> list[Move]:
        moves = []
        y = self.pos.y + self.forward_dir
        if b.get_square(y, self.pos.x) == None:
            new_pos = Pos(y, self.pos.x)
            if self.PROMOTION_ROW[self.color] == y:
                for promo_piece_con in self.PROMOTION_PIECES_CONS:
                    moves.append(Promotion(self, new_pos, None, promo_piece_con(self.color, *new_pos)))
            else:
                moves.append(NormalMove(self, Pos(y, self.pos.x), None))
                if self.moved ==0:
                    y+=self.forward_dir
                    moves.append(NormalMove(self, Pos(y, self.pos.x), capture=None))

        moves += self.attackingMoves(b, gS)
        return moves
    
    def attackingMoves(self, b: Board, gS: GameState)->list[Move]:
        moves = []
        y = self.pos.y + self.forward_dir
        for x_attack_dir in self.attackDir:
            x = self.pos.x + x_attack_dir
            if not 0 <= x < 8:
                continue

            end_val = b.get_square(y, x)
            end_pos = Pos(y, x)
            if gS.is_enPassSq(y, x):
                y_offset = 1 if self.forward_dir == -1 else -1
                end_val = b.get_square(y+y_offset, x)
            
            if isinstance(end_val, Capturable) and end_val.color !=self.color:
                if y == self.PROMOTION_ROW[self.color]:
                    for promo_piece_con in self.PROMOTION_PIECES_CONS:
                        moves.append(Promotion(self, end_pos, end_val, promo_piece_con(self.color, *end_pos)))
                else:
                    moves.append(NormalMove(self, end_pos, end_val))

        return moves
    
    def isAttacking(self, end_square: Pos, b: Board)->bool:
        for a_dir in self.attackDir:
            if self.pos.y + self.forward_dir == end_square.y and self.pos.x + a_dir == end_square.x:
                return True
        return False
    
    def __str__(self):
        if self.color == "W":
            return "p"
        else:
            return "P"


@dataclass(frozen=True)
class Move(ABC):
    """Parent Class!!! Shouldnt be used on its own!!!"""
    piece: Piece
    end: Pos
    start: Pos = field(init=False)
    def __post_init__(self):
        object.__setattr__(self, "start", self.piece.pos)
    @abstractmethod
    def apply(self, board: Board):
        board.move_piece(self.piece, self.end)
        self.piece.moved+=1

    @abstractmethod
    def undo(self, board: Board):
        board.move_piece(self.piece, self.start)
        self.piece.moved-=1


@dataclass(frozen=True)
class NormalMove(Move):
    capture: Capturable | None 
    def apply(self, board: Board):
        if isinstance(self.capture, Capturable):
            board.cap_piece(self.piece, self.end, self.capture)
        else:
            board.move_piece(self.piece, self.end)
        self.piece.moved+=1

    def undo(self, board: Board):
        board.move_piece(self.piece, self.start)
        if isinstance(self.capture, Capturable):
            board.place_piece(self.capture)
        self.piece.moved-=1



def _get_castle_squares(color: str) -> Sides[CastleSquares]:
    if color =="W":
        row = 7
    else:
        row = 0
    return {
        "Q": CastleSquares(rook_start=Pos(row,0), rook_end=Pos(row,3), king_end=Pos(row,2),
                           must_be_empty=(Pos(row,3), Pos(row,2), Pos(row,1)),
                           must_be_unattacked=(Pos(row,4), Pos(row,3), Pos(row,2))),
        "K": CastleSquares(rook_start=Pos(row,7), rook_end=Pos(row,5), king_end=Pos(row,6),
                           must_be_empty=(Pos(row,5), Pos(row,6)),
                           must_be_unattacked=(Pos(row,4), Pos(row,5), Pos(row,6))),
    }

@dataclass(frozen=True)
class Castle(Move):
    CASTLE_POS: ClassVar[Teams[Sides[CastleSquares]]] = {"W": _get_castle_squares("W"),
                                                         "B": _get_castle_squares("B")}
    piece: King
    castle_side: Side
    end: Pos = field(init=False)
    def __post_init__(self):
        super().__post_init__()
        object.__setattr__(self, "end", self.squares().king_end)

    def squares(self) -> CastleSquares:
        return self.CASTLE_POS[self.piece.color][self.castle_side]

    def apply(self, board: Board):
        rook = board.get_square(*self.squares().rook_start)

        assert isinstance(rook, Rook)
        board.move_piece(rook, self.squares().rook_end)
        board.move_piece(self.piece, self.end)
        self.piece.moved+=1
        rook.moved+=1

    def undo(self, board: Board):
        rook = board.get_square(*self.squares().rook_end)

        assert isinstance(rook, Rook)
        board.move_piece(rook, self.squares().rook_start)
        board.move_piece(self.piece, self.start)
        self.piece.moved-=1
        rook.moved-=1


@dataclass(frozen=True)
class Promotion(NormalMove):
    piece: Pawn
    promo_piece: Queen|Knight|Bishop|Rook
    def apply(self, board: Board):
        super().apply(board)
        board.remove_piece(self.piece)
        board.place_piece(self.promo_piece)
    def undo(self, board: Board):
        super().undo(board)
        board.remove_piece(self.promo_piece)
        board.place_piece(self.piece)