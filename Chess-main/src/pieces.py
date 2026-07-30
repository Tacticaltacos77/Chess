from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, NamedTuple
from pieces import King
from move import *


if TYPE_CHECKING:
    from board import Board
    from gameState import GameState
    from pieces import Piece    
    from typedef import *

class Pos(NamedTuple):
    """(y, x) coordinates on the chess board."""
    y: int
    x: int

class HasMovedMixIn:
    moved: int
    def has_moved(self)->bool:
        return self.moved !=0
        
class Piece:
    moveDir: tuple[Pos, ...]
    maxMove: int
    def __init__(self, color: Team, y: int, x: int):
        self.color: Team = color
        self.pos: Pos = Pos(y, x)

    def moves(self, b: Board, gS: GameState)->list[Move]:
        moves = []
        for dir in self.moveDir:
            currMove = self.maxMove
            while currMove > 0 and 0 <=self.pos.y + dir[0] < 8 and 0 <= self.pos.x + dir[1] <8:
                new_y = self.pos.y + dir[0] 
                new_x = self.pos.x + dir[1]     
                end_square = b.get_square(new_y, new_x)
                if end_square == None:
                    moves.append((new_y,new_x))
                elif self.is_valid_capture(end_square):
                    moves.append((new_y,new_x))
                    break
                else:
                    break
        return moves
    
    def isAttacking(self, square: Pos, b:Board)->bool:
        y, x = square
        for y_atk_dir, x_atk_dir in self.moveDir:
            cur_y_dis = abs(y-self.pos.y)
            cur_x_dis = abs(x-self.pos.x)
            new_y_dis = abs(y-self.pos.y + y_atk_dir)
            new_x_dis = abs(x-self.pos.x + x_atk_dir)
            if cur_y_dis < new_y_dis or cur_x_dis < new_x_dis:
                continue
            currMove = self.maxMove
            while currMove > 0 and 0 <=self.pos.y + y_atk_dir < 8 and 0 <= self.pos.x + x_atk_dir <8:
                new_y = self.pos.y + y_atk_dir
                new_x = self.pos.x + x_atk_dir 
                if y == new_y and x == new_x:
                    return True
                if b.get_square(new_y, new_x)!=None:
                    break
        return False
    
    def is_valid_capture(self, end_p:Piece|None)->bool:
        if end_p == None:
            return False
        return end_p.color != self.color and not isinstance(end_p, King)
    
    def set_pos(self, end_pos: Pos):
        if not isinstance(end_pos, Pos):
            raise ValueError()
        self.pos = end_pos

class Pawn(Piece, HasMovedMixIn):
    maxMove:int =1
    forwardDir:int
    attackDir: Pos = Pos(-1, 1) 
    PROMOTION_PIECES_CONS = (Queen, Rook, Bishop, Knight)
    PROMOTION_ROW = {"W": 0, "B": 7}
    
    def __init__(self, color, y, x):
        super().__init__(color, y, x)
        self.moved = 0
        if color == "W":
            self.forward_dir = -1
            self.promo_square = 0
        else:
            self.forward_dir = 1
            self.promo_square = 7

    def moves(self, b: Board, gS: GameState)-> list[Move]:
        moves = []
        new_y = self.pos.y + self.forward_dir
        if b.get_square(new_y, self.pos.x) == None:
            new_pos = Pos(new_y, self.pos.x)
            if self.can_promote():
                for promo_piece_con in self.PROMOTION_PIECES_CONS:
                    moves.append(Promotion(self, new_pos, None, promo_piece_con(self.color,*new_pos)))
            else:
                moves.append(NormalMove(self, Pos(new_y, self.pos.x), None))
        moves += self.attackingMoves(b, gS)
        return moves
    
    def attackingMoves(self, b: Board, gS: GameState)->list[Move]:
        moves = []
        new_y = self.pos.y + self.forward_dir
        for x_attack_dir in self.attackDir:
            new_x = self.pos.x + x_attack_dir
            end_square_val = b.get_square(new_y, new_x)
            if self.is_valid_capture(end_square_val):
                end_square_pos = Pos(new_y, new_x)
                if new_y == self.promo_square:
                    for promo_piece_con in self.PROMOTION_PIECES_CONS:
                        moves.append(Promotion(self, end_square_pos, end_square_val, promo_piece_con(self.color, *end_square_pos)))
                elif gS.is_enPassSq(new_y, new_x):
                    moves.append(NormalMove(self, end_square_pos, end_square_val))   
        return moves      
    
    def isAttacking(self, square: Pos, b: Board)->bool:
        for a_dir in self.attackDir:
            if self.pos.y + self.forward_dir == square.y and self.pos.x + a_dir == square.x:
                return True
        return False
    
    def can_promote(self)->bool:
        return self.PROMOTION_ROW[self.color]==self.pos.y 
    
    def __str__(self):
        if self.color == "W":
            return "p"
        else:
            return "P"
    
class Rook(Piece, HasMovedMixIn):
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
        
class Knight(Piece):
    maxMove =1
    moveDir = (Pos(1,2),Pos(1,-2),Pos(2,1),Pos(2,-1),Pos(-2,-1),Pos(-2,1),Pos(-1,2),Pos(-1,-2))
    def __init__(self, color: Team, y:int, x:int):
        super().__init__(color, y, x)
    def __str__(self):
        if self.color == "W":
            return "n"
        else:
            return "N"
     
class Bishop(Piece):
    maxMove =7
    moveDir = (Pos(1,1), Pos(1,-1), Pos(-1,1), Pos(-1,-1))
    def __init__(self, color: Team, y:int, x:int):
        super().__init__(color, y, x)
    def __str__(self):
        if self.color == "W":
            return "b"
        else:
            return "B"
        
class Queen(Piece):
    maxMove =7
    moveDir = (Pos(0,1),Pos(1,0),Pos(-1,0),Pos(0,-1),Pos(1,1),Pos(1,-1),Pos(-1,1),Pos(-1,-1))
    def __init__(self, color: Team, y:int, x:int):
        super().__init__(color, y, x)
    def __str__(self):
        if self.color == "W":
            return "q"
        else:
            return "Q"
        
class King(Piece, HasMovedMixIn):
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
        for castle_direction in ("Q","K"):
            if gS.castle_rights[self.color][castle_direction]:
                moves.append(Castle(self, castle_direction))
        return moves