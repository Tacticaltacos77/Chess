from typing import TYPE_CHECKING
from errors import *
from board import Board
from pieces import *
from collections import defaultdict
from enum import StrEnum
from fen import Fen, DEFAULT_FEN
from helper import to_square, get_square_color
from typedef import *


class Status(StrEnum):
    ACTIVE = "active"
    WHITE_CHECKMATE = "white checkmate"
    BLACK_CHECKMATE = "black checkmate"
    STALEMATE = "stalemate"
    DRAW_REPETITION = "draw repetition"
    DRAW_FIFTY_MOVE = "draw 50 move"
    DRAW_INSUFFICIENT_MATERIAL = "draw insufficient material"


class TeamState:
    color: Team
    king: King
    pieces: list[Piece]
    lost_pieces: list[Piece]
    castle_rights: set[Side]

    def __init__(self, pieces: list[Piece], color: Team, castle_rights: set):
        self.color = color
        self.pieces = pieces
        self.lost_pieces = []
        self.castle_rights = castle_rights
        if len(castle_rights) > len(SIDES):
            raise IllegalGameStateError(f"{color} has {len(castle_rights)} castle rights, expected at most {len(SIDES)}")

        for side in castle_rights:
            if side not in SIDES:
                raise IllegalGameStateError(f"{side} is not a castle side, expected one of {SIDES}")

        king_count = 0
        for p in pieces:
            if p.color != self.color:
                raise IllegalGameStateError(f"{p} is {p.color}, but it was given to the {color} team")
            if isinstance(p, King):
                self.king = p
                king_count+=1
        if king_count!=1:
            raise IllegalGameStateError(f"expected exactly 1 {color} king, got {king_count}")
        
    def refresh_castle_rights(self, board: Board) -> None:
        if self.king.moved !=0:
            self.castle_rights.discard("K")
            self.castle_rights.discard("Q")
            return
        
        for side in SIDES:
            rook_start = Castle.CASTLE_POS[self.color][side].rook_start
            rook = board.get_square(*rook_start)

            if isinstance(rook, Rook) and rook.moved ==0 and rook.color == self.color:
                self.castle_rights.add(side)
            else:
                self.castle_rights.discard(side)

    def lose_piece(self, piece: Piece):
        self.pieces.remove(piece)
        self.lost_pieces.append(piece)

    def regain_piece(self, piece: Piece):
        self.lost_pieces.remove(piece)

    def promote_piece(self, pawn: Pawn, piece: Piece):
        self.pieces.remove(pawn)
        self.pieces.append(piece)

    def demote_piece(self, pawn: Pawn, piece: Piece):
        self.pieces.remove(piece)
        self.pieces.append(pawn)

class Game:
    full_turn: int
    color_turn: Team
    half_turn_history: list[int]
    curr_turn_moves: defaultdict[Pos, list[Move]] 
    move_history: list[Move]
    enPassentHistory:list[None|Pos]
    team_state:dict[Team,TeamState] 
    board: Board
    postitions: defaultdict[str, int]
    status: Status

    def __init__(self, fen: str):
        f = Fen(fen) if fen else DEFAULT_FEN
        self.full_turn = f.full_turn
        self.half_turn_history = [f.half_turn]
        self.color_turn = f.turn
        self.move_history = []
        self.enPassentHistory = [f.en_passant]
        pieces = f.build_pieces()
        self.board = Board(pieces)
        self.team_state = self._create_teams_states(pieces, f.castle_rights)
        self.postitions = defaultdict(int)
        self.update_castle_vars()
        self.curr_turn_moves = self.compute_curr_turn_moves()
        self.status = self.compute_gamestate_status()

    def _create_teams_states(self, pieces: list[Piece], castle_rights: set[str]) -> dict[Team, TeamState]:
        white_pieces, black_pieces = [], []
        for p in pieces:
            if p.color =="W":
                white_pieces.append(p)
            elif p.color == "B":
                black_pieces.append(p)
            else:
                raise IllegalGameStateError(f"{p} on {to_square(p.pos)} has color {p.color}, expected one of {TEAMS}")
            
        white_rights, black_rights = set(), set()
        for side in SIDES:
            if side in castle_rights:
                white_rights.add(side)
            if side.lower() in castle_rights:
                black_rights.add(side)

        return {"W": TeamState(white_pieces, "W", white_rights), "B": TeamState(black_pieces, "B", black_rights)}
    
    def get_other_color(self, color:Team) -> Team:
        if color =="W":
            return "B"
        return "W"
    
    def _is_en_pass_sq(self, y, x)->bool:
        return self.enPassentHistory[-1] == Pos(y, x)
    
    def compute_all_moves(self) -> dict[Pos, list[Move]]:
        pieces = self.team_state[self.color_turn].pieces
        moves: dict[Pos, list[Move]] = {}
        for p in pieces:
            moves[p.pos] = p.moves(self.board)
        return moves
    
    def compute_curr_turn_moves(self) -> defaultdict[Pos, list[Move]]:
        current_turn_all_moves = self.compute_all_moves()
        return self.get_valid_moves(current_turn_all_moves)
        
    def check_move_valid(self, move: Move):
       return move in self.curr_turn_moves[move.start]

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
        opp_pieces = self.team_state[self.get_other_color(color_p)].pieces
        for p in opp_pieces:
            if p.isAttacking(king.pos, self.board):
                return True
        return False
    
    def get_valid_moves(self, all_moves: dict[Pos, list[Move]]) -> defaultdict[Pos, list[Move]]:
        legal_moves: dict[Pos, list[Move]] = defaultdict(list)
        king = self.team_state[self.color_turn].king
        for p in all_moves:
            for m in all_moves[p]:
                if type(m)==Castle and self._validate_castle(m):
                    legal_moves[p].append(m)
                elif isinstance(m, NormalMove):
                    if isinstance(m, EnPassant) and not self._is_en_pass_sq(*m.end):
                        continue
                    m.apply(self.board)
                    if not self.king_in_check(king):
                        legal_moves[p].append(m)
                    m.undo(self.board)
        return legal_moves
    
    def _validate_castle(self, castle: Castle) -> bool:
        king = castle.piece
        ts = self.team_state[king.color]
        if self.king_in_check(king) or king.moved != 0 or castle.castle_side not in ts.castle_rights:
            return False
        p = castle.piece
        opp_pieces = self.team_state[self.get_other_color(p.color)].pieces
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
        self.team_state["W"].refresh_castle_rights(self.board)
        self.team_state["B"].refresh_castle_rights(self.board)

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
            self.team_state[move.capture.color].lose_piece(move.capture)
        
        if isinstance(move, Promotion):
            self.team_state[move.piece.color].promote_piece(move.piece, move.promo_piece)

        if isinstance(move.piece, Pawn):
            half_turn = 0
        self.half_turn_history.append(half_turn)

        self._add_en_passant(move)
        self.update_castle_vars()

        self.color_turn = self.get_other_color(self.color_turn)

        if self.color_turn == "W":
            self.full_turn+=1
        self.curr_turn_moves = self.compute_curr_turn_moves()

    def undo_move(self) -> None:
        if not self.move_history:
            return
        move = self.move_history.pop()
        move.undo(self.board)
        if isinstance(move, NormalMove) and move.capture:
            self.team_state[move.capture.color].regain_piece(move.capture)
        if isinstance(move, Promotion):
            self.team_state[move.piece.color].demote_piece(move.piece, move.promo_piece)

        self.half_turn = self.half_turn_history.pop
        self.enPassentHistory.pop()
        self.update_castle_vars()

        self.color_turn = self.get_other_color(self.color_turn)
        if self.color_turn == "B":
            self.full_turn-=1
            
        self.curr_turn_moves = self.compute_curr_turn_moves()
        self.status = self.compute_gamestate_status()

    def check_sufficient_material(self) -> bool:
        minor_pieces: list[Piece] = []
        for t in TEAMS:
            for p in self.team_state[t].pieces:
                if isinstance(p, (Pawn, Rook, Queen)):
                    return True
                if not isinstance(p, King):
                    minor_pieces.append(p)

        if len(minor_pieces) <=1:
            return False
        
        first_square_color = get_square_color(minor_pieces[0].pos)
        if all(isinstance(p, Bishop) and first_square_color==get_square_color(p.pos) for p in minor_pieces):
            return False

        return True

    def compute_gamestate_status(self) -> Status:
        """Designed to be called at the start of turns"""
        if not self.curr_turn_moves:
            c = self.color_turn
            team = self.team_state[c]
            if self.king_in_check(team.king):
                if c =="W":
                    return Status.BLACK_CHECKMATE
                else:
                    return Status.WHITE_CHECKMATE
            else:
                return Status.STALEMATE
        elif not self.check_sufficient_material():
            return Status.DRAW_INSUFFICIENT_MATERIAL
        elif self.half_turn_history[-1] >= 100:
            return Status.DRAW_FIFTY_MOVE
        
        return Status.ACTIVE