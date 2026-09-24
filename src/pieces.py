from typing import TYPE_CHECKING, ClassVar
from typedef import Pos, CastleSquares
from dataclasses import dataclass, field
from abc import ABC, abstractmethod

if TYPE_CHECKING:
    from board import Board
    from typedef import *

class Piece:
    moveDir: tuple[Pos, ...]
    maxMove: int
    def __init__(self, color: Team, y: int, x: int):
        self.color: Team = color
        self.pos: Pos = Pos(y, x)

    def _get_letter(self, p:str) -> str:
        return p.upper() if self.color =="W" else p.lower()
    
    def moves(self, b: Board)->list[Move]:
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
                elif isinstance(end_square, Capturable) and end_square.color != self.color:
                    moves.append(NormalMove(self, Pos(y, x), capture=end_square))
                    break
                else:
                    break
        return moves
    ### 
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
            raise ValueError(f"set_pos expects a Pos, got {type(end_pos)}: {end_pos}")
        self.pos = end_pos

    
class Capturable(Piece):
    pass
    
class Rook(Capturable):
    maxMove =7
    moveDir = (Pos(0,1),Pos(1,0),Pos(-1,0),Pos(0,-1))
    def __init__(self, color:Team, y:int, x:int):
        super().__init__(color, y, x)
        self.moved = 0

    def __str__(self) -> str:
        return super()._get_letter("r")
    
class Knight(Capturable):
    maxMove =1
    moveDir = (Pos(1,2),Pos(1,-2),Pos(2,1),Pos(2,-1),Pos(-2,-1),Pos(-2,1),Pos(-1,2),Pos(-1,-2))
    def __init__(self, color: Team, y:int, x:int):
        super().__init__(color, y, x)

    def __str__(self):
        return super()._get_letter("n")
    
class Bishop(Capturable):
    maxMove =7
    moveDir = (Pos(1,1), Pos(1,-1), Pos(-1,1), Pos(-1,-1))
    def __init__(self, color: Team, y:int, x:int):
        super().__init__(color, y, x)

    def __str__(self):
        return super()._get_letter("b")
        
class Queen(Capturable):
    maxMove =7
    moveDir = (Pos(0,1),Pos(1,0),Pos(-1,0),Pos(0,-1),Pos(1,1),Pos(1,-1),Pos(-1,1),Pos(-1,-1))
    def __init__(self, color: Team, y:int, x:int):
        super().__init__(color, y, x)

    def __str__(self):
        return super()._get_letter("q")
        
class King(Piece):
    maxMove =1
    moveDir = (Pos(0,1),Pos(1,0),Pos(-1,0),Pos(0,-1),Pos(1,1),Pos(1,-1),Pos(-1,1),Pos(-1,-1))
    def __init__(self, color: Team, y:int, x: int):
        super().__init__(color, y, x)
        self.moved = 0

    def __str__(self):
        return super()._get_letter("k")
        
    def moves(self, b: Board)->list[Move]:
        moves = super().moves(b)
        moves.append(Castle(self, "K"))
        moves.append(Castle(self, "Q"))
        return moves

class Pawn(Capturable):
    maxMove = 1
    forwardDir:int
    attackDir = Pos(-1, 1)
    PROMOTION_PIECES_CONS = (Queen, Rook, Bishop, Knight)
    PROMOTION_ROW = {"W": 0, "B": 7}
    EN_PASSANT_ROW = {"W": 3, "B": 4}
    START_ROW = {"W": 6, "B": 1}
    
    def __init__(self, color, y, x):
        super().__init__(color, y, x)
        if color == "W":
            self.forward_dir = -1
        else:
            self.forward_dir = 1

    def __str__(self):
        return super()._get_letter("p")

    def moves(self, b: Board)-> list[Move]:
        moves = []
        y = self.pos.y + self.forward_dir
        if b.get_square(y, self.pos.x) == None:
            new_pos = Pos(y, self.pos.x)
            if self.PROMOTION_ROW[self.color] == y:
                for promo_piece_con in self.PROMOTION_PIECES_CONS:
                    moves.append(Promotion(self, new_pos, None, promo_piece_con(self.color, y, self.pos.x)))
            else:
                moves.append(NormalMove(self, new_pos, None))
                double_y = y + self.forward_dir
                if self.START_ROW[self.color] == self.pos.y and b.get_square(double_y, self.pos.x) == None:
                    moves.append(NormalMove(self, Pos(double_y, self.pos.x), capture=None))

        moves += self.attackingMoves(b)
        return moves
    
    def attackingMoves(self, b: Board)->list[Move]:
        moves = []
        y = self.pos.y + self.forward_dir
        for x_attack_dir in self.attackDir:
            x = self.pos.x + x_attack_dir
            if not 0 <= x < 8:
                continue
            
            end_pos = Pos(y, x)
            en_pass_val = b.get_square(self.pos.y, x)
            end_val = b.get_square(y, x)
            if self.pos.y == self.EN_PASSANT_ROW[self.color] and (isinstance(en_pass_val, Pawn) and en_pass_val.color != self.color):
                moves.append(EnPassant(self, end_pos, en_pass_val))
            elif isinstance(end_val, Capturable) and end_val.color !=self.color:
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

PIECE_BY_LETTER: dict[str, type[Piece]] = {"r": Rook, "n": Knight, "b": Bishop, "q": Queen, "k":King, "p": Pawn}

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
        if isinstance(self.piece, (King, Rook)):
            self.piece.moved+=1

    @abstractmethod
    def undo(self, board: Board):
        board.move_piece(self.piece, self.start)
        if isinstance(self.piece, (King, Rook)):
            self.piece.moved-=1


@dataclass(frozen=True)
class NormalMove(Move):
    capture: Capturable | None 
    def apply(self, board: Board):
        if isinstance(self.capture, Capturable):
            board.cap_piece(self.piece, self.end, self.capture)
        else:
            board.move_piece(self.piece, self.end)
        if isinstance(self.piece, (King, Rook)):
            self.piece.moved+=1

    def undo(self, board: Board):
        board.move_piece(self.piece, self.start)
        if isinstance(self.capture, Capturable):
            board.place_piece(self.capture)
        if isinstance(self.piece, (King, Rook)):
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
        super().apply(board)

        rook = board.get_square(*self.squares().rook_start)
        assert isinstance(rook, Rook)

        board.move_piece(rook, self.squares().rook_end)
        rook.moved+=1

    def undo(self, board: Board):
        super().undo(board)
        rook = board.get_square(*self.squares().rook_end)

        assert isinstance(rook, Rook)
        board.move_piece(rook, self.squares().rook_start)
        rook.moved-=1

@dataclass(frozen=True)
class EnPassant(NormalMove):
    pass


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