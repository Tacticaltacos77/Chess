from .errors import *
from .board import Board
from .pieces import *
from collections import defaultdict
from enum import StrEnum
from .fen import Fen, DEFAULT_FEN
from .helper import to_square, get_square_color, get_other_color
from .typedef import *


class Status(StrEnum):
    ACTIVE = "active"
    WHITE_WINS = "white wins"
    BLACK_WINS = "black wins"
    STALEMATE = "stalemate"
    DRAW_REPETITION = "draw repetition"
    DRAW_FIFTY_MOVE = "draw 50 move"
    DRAW_INSUFFICIENT_MATERIAL = "draw insufficient material"


class Game:
    full_turn: int
    color_turn: Team
    half_turn_history: list[int]
    move_history: list[Move]
    allowed_moves_history: list[dict]
    enPassentHistory:list[None|Pos]
    castle_rights: set
    kings: Teams[King]
    board: Board
    positions: defaultdict[str, int]
    status: Status

    def __init__(self, fen: str|None = None):
        f = Fen(fen) if fen else DEFAULT_FEN
        self.full_turn = f.full_turn
        self.half_turn_history = [f.half_turn]
        self.color_turn = f.turn
        self.move_history = []
        self.enPassentHistory = [f.en_passant]
        self.board = Board(f.build_pieces())
        self.kings = self._set_kings()
        self.castle_rights = set(f.castle_rights)
        self.lost_pieces = {"W": [], "B": []}
        
        self.positions = defaultdict(int)
        self.update_castle_vars()
        self.allowed_moves_history = [self.compute_curr_turn_moves()]
        self.status = self.compute_gamestate_status()
        self.positions[self._get_position()] = 1

    def get_fen(self) -> str:
        ep = self.enPassentHistory[-1]
        half_turn = self.half_turn_history[-1]
        return Fen.to_fen(self.board.grid, self.color_turn, self.castle_rights, ep, half_turn, self.full_turn)

    def _get_position(self) -> str:
        # Positions shouldn't include the en passant in it unless the en passant pawn is actually
        # capturable because then it is actually a different position
        ep = self.enPassentHistory[-1]
        if ep:
            y, x = Pawn.EN_PASSANT_ROW[self.color_turn], ep.x
            for offset in (-1, 1):
                moves = self.get_curr_turn_moves().get((y, x+offset), [])
                for move in moves:
                    if isinstance(move, EnPassant):
                        return self.get_fen().rsplit(" ", 2)[0]
            
        return self.get_fen().rsplit(" ", 3)[0] +" -"

    def _set_kings(self) -> Teams[King]:
        kings = {}
        for p in self.board.get_pieces():
            if isinstance(p, King):
                if p.color == "W":
                    kings["W"] = p
                else:
                    kings["B"] = p
        return kings
        
    def get_curr_turn_moves(self):
        return self.allowed_moves_history[-1]
    
    def parse_move(self, move: str) -> Move:
        """'pe2-e4', 'Ng8xf6', 'pe7-e8=Q', 'O-O' -> the matching legal Move from moves."""
        move = move.strip()
        for move_list in self.get_curr_turn_moves().values():
            for m in move_list:
                if str(m) == move:
                    return m
        raise IllegalMoveError(f"{move} is not a legal move in this position")
    
    def _is_en_pass_sq(self, y, x)->bool:
        return self.enPassentHistory[-1] == Pos(y, x)
    
    def compute_all_moves(self) -> dict[Pos, list[Move]]:
        pieces = self.board.get_pieces(self.color_turn)
        moves: dict[Pos, list[Move]] = {}
        for p in pieces:
            moves[p.pos] = p.moves(self.board)
        return moves
    
    def compute_curr_turn_moves(self) -> defaultdict[Pos, list[Move]]:
        current_turn_all_moves = self.compute_all_moves()
        return self.get_valid_moves(current_turn_all_moves)
        
    def check_move_valid(self, move: Move):
       return move in self.allowed_moves_history[-1][move.start]

    def _add_en_passant(self, move: Move) -> None:
        if type(move.piece) ==Pawn and abs(move.start.y - move.end.y) ==2:
            y = move.start.y + move.piece.forward_dir
            self.enPassentHistory.append(Pos(y, move.end.x))
        else:
            self.enPassentHistory.append(None)
    
    def king_in_check(self, king: King) -> bool:
        if type(king) != King:
            raise TypeError(f"king_in_check expects a King, got {type(king).__name__}")
        color_p = king.color
        opp_pieces = self.board.get_pieces(get_other_color(color_p))
        for p in opp_pieces:
            if p.isAttacking(king.pos, self.board):
                return True
        return False
    
    def get_valid_moves(self, all_moves: dict[Pos, list[Move]]) -> defaultdict[Pos, list[Move]]:
        legal_moves: dict[Pos, list[Move]] = defaultdict(list)
        for p in all_moves:
            for m in all_moves[p]:
                if type(m)==Castle and self._validate_castle(m):
                    legal_moves[p].append(m)
                elif isinstance(m, NormalMove):
                    if isinstance(m, EnPassant) and not self._is_en_pass_sq(*m.end):
                        continue
                    m.apply(self.board)
                    if not self.king_in_check(self.kings[self.color_turn]):
                        legal_moves[p].append(m)
                    m.undo(self.board)
        return legal_moves
    
    def _validate_castle(self, castle: Castle) -> bool:
        king = castle.piece
        if self.king_in_check(king) or king.moved != 0 or castle.castle_side not in self.castle_rights:
            return False
        p = castle.piece
        opp_pieces = self.board.get_pieces(get_other_color(p.color))
        castle_squares = castle.squares()

        for pos in castle_squares.must_be_unattacked:
            for opp_p in opp_pieces:
                if opp_p.isAttacking(pos, self.board):
                    return False    
                
        for pos in castle_squares.must_be_empty:
            if self.board.get_square(*pos) != None:
                return False
        return True

    def update_castle_vars(self) -> None:
        for side, squares in Castle.CASTLE_POS.items():
            color = "W" if side.isupper() else "B"
            rook = self.board.get_square(*squares.rook_start)

            if self.kings[color].moved == 0 and isinstance(rook, Rook) and rook.moved == 0 and rook.color == color:
                self.castle_rights.add(side)
            else:
                self.castle_rights.discard(side)

    def make_move(self, move: Move) -> None:
        if not self.check_move_valid(move):
            raise IllegalMoveError(f"{move.piece} {to_square(move.start)}-{to_square(move.end)} "
                                   f"is not legal in this position")
        if move.piece.color != self.color_turn:
            raise IllegalGameStateError(f"it is {self.color_turn} to move, but {move.piece} is "
                                        f"{move.piece.color}")
        if self.status != Status.ACTIVE:
            raise IllegalGameStateError(f"Game is over. status: {self.status}")
        move.apply(self.board)
        half_turn = self.half_turn_history[-1] + 1
        
        if isinstance(move, NormalMove) and move.capture:
            half_turn = 0

        if isinstance(move.piece, Pawn):
            half_turn = 0
        self.half_turn_history.append(half_turn)
        self.move_history.append(move)
        
        self._add_en_passant(move)
        self.update_castle_vars()

        self.color_turn = get_other_color(self.color_turn)

        if self.color_turn == "W":
            self.full_turn+=1

        self.allowed_moves_history.append(self.compute_curr_turn_moves())
        position = self._get_position() 
        self.positions[position] +=1

        self.status = self.compute_gamestate_status(position)


    def undo_move(self) -> None:
        if not self.move_history:
            raise IllegalGameStateError()
        
        position = self._get_position()
        self.positions[position] -=1
        if self.positions[position] == 0:
            self.positions.pop(position)
        move = self.move_history.pop()
        move.undo(self.board)

        self.half_turn_history.pop()
        self.enPassentHistory.pop()
        self.update_castle_vars()

        self.color_turn = get_other_color(self.color_turn)
        if self.color_turn == "B":
            self.full_turn-=1
            
        self.allowed_moves_history.pop()
        self.status = self.compute_gamestate_status()

    def check_sufficient_material(self) -> bool:
        minor_pieces: dict[Team, list[Piece]] = {"W": [], "B": []}
        for t in TEAMS:
            for p in self.board.get_pieces(t):
                if isinstance(p, (Pawn, Rook, Queen)):
                    return True
                if not isinstance(p, King):
                    minor_pieces[p.color].append(p)

        if len(minor_pieces["W"]) <= 1 and len(minor_pieces["B"]) <= 1:
            return False

        first_square_color = get_square_color((minor_pieces["W"] + minor_pieces["B"])[0].pos)

        # Check to make sure not all the Bishops are on the same squares
        if all(isinstance(wp, Bishop) and first_square_color==get_square_color(wp.pos) for wp in minor_pieces["W"]):
            if all(isinstance(bp, Bishop) and first_square_color==get_square_color(bp.pos) for bp in minor_pieces["B"]):
                return False
            
        # Two Knights edge case
        if len(minor_pieces["W"]) == 2 and len(minor_pieces["B"]) == 0:
            wp1, wp2 = minor_pieces["W"]
            if isinstance(wp1, Knight) and isinstance(wp2, Knight):
                return False
        elif len(minor_pieces["W"]) == 0 and len(minor_pieces["B"]) == 2:
            bp1, bp2 = minor_pieces["B"]
            if isinstance(bp1, Knight) and isinstance(bp2, Knight):
                return False
        return True

    def compute_gamestate_status(self, last_position:str|None = None) -> Status:
        """Designed to be called at the start of turns"""
        if not self.allowed_moves_history[-1]:
            c = self.color_turn
            if self.king_in_check(self.kings[self.color_turn]):
                if c =="W":
                    return Status.BLACK_WINS
                else:
                    return Status.WHITE_WINS
            else:
                return Status.STALEMATE
        if not self.check_sufficient_material():
            return Status.DRAW_INSUFFICIENT_MATERIAL
        if self.half_turn_history[-1] >= 100:
            return Status.DRAW_FIFTY_MOVE
        if last_position and self.positions[last_position] == 3:
            return Status.DRAW_REPETITION
        return Status.ACTIVE