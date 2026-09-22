from typing import TYPE_CHECKING
from errors import *
from pieces import *
from collections import defaultdict
from enum import StrEnum
from fen import Fen, DEFAULT_FEN

if TYPE_CHECKING:
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
    color: str
    king: King
    pieces: list[Piece]
    lost_pieces: list[Piece]
    castle_rights: dict[Side, bool]

    def __init__(self, pieces: list[Piece], color: str):
        self.color = color
        self.pieces = pieces
        king_count = 0
        for p in pieces:
            if p.color != self.color:
                raise IllegalGameStateError()
            if isinstance(p, King):
                self.king = p
                king_count+=1
        if king_count!=1:
            raise IllegalGameStateError()
        
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

def get_default_pieces() -> list[Piece]:
    pawns = [Pawn("W", 6, x) for x in range(8)] + [Pawn("B", 1, x) for x in range(8)]
    pieces = [Rook("W", 7, 0), Knight("W", 7, 1), Bishop("W", 7, 2), Queen("W", 7, 3),
            King("W", 7, 4), Bishop("W", 7, 5), Knight("W", 7, 6), Rook("W", 7, 7),
            Rook("B", 7, 0), Knight("B", 7, 1), Bishop("B", 7, 2), Queen("B", 7, 3),
            King("B", 7, 4), Bishop("B", 7, 5), Knight("B", 7, 6), Rook("B", 7, 7)]
    return  pieces + pawns

class Game:
    half_turn: int 
    full_turn: int
    curr_turn_moves: defaultdict[Pos, list[Move]] 
    move_history: list[Move]
    enPassentHistory:list[None|Pos]
    team_state:dict[Team,TeamState] 
    board: Board
    postitions: defaultdict[str, int]
    last_turn_capture_or_pawn_move: list[int]
    status: Status

    def __init__(self, fen: str):
        f = Fen(fen) if fen else DEFAULT_FEN
        self.half_turn = f.half_turn
        self.full_turn = f.full_turn
        self.curr_turn_moves = defaultdict(list)
        self.move_history = []
        self.enPassentHistory = []
        pieces = f.build_pieces()
        self.team_state = self._create_teams_states(pieces)
        self.board = Board(pieces)
        self.postitions = defaultdict(int)
        self.last_turn_capture_or_pawn_move = [0]
        self.status = self.check_gamestate_condtion()

    def _create_teams_states(self, pieces: list[Piece]) -> dict[Team, TeamState]:
        teams_pieces: dict[Team,list[Piece]] = {"W":[], "B":[]}
        for p in pieces:
            if p.color not in ("W", "B"):
                raise IllegalGameStateError()
            teams_pieces[p.color].append(p)
        return {"W": TeamState(teams_pieces["W"], "W"), "B": TeamState(teams_pieces["B"], "B")}
    
    def get_color_turn(self)->Team:
        if self.half_turn % 2==1:
            return "W"
        return "B"
    
    def get_other_color(self, color:Team) -> Team:
        if color =="W":
            return "B"
        return "W"
    
    def _is_en_pass_sq(self, y, x)->bool:
        if not self.enPassentHistory:
            return False
        return self.enPassentHistory[-1] == Pos(y, x)
    
    def get_all_moves(self) -> dict[Pos, list[Move]]:
        pieces = self.team_state[self.get_color_turn()].pieces
        moves: dict[Pos, list[Move]] = {}
        for p in pieces:
            moves[p.pos] = p.moves(self.board)
        return moves
    
    def upd_game_state_moves(self) -> None:
        current_turn_all_moves = self.get_all_moves()
        self.curr_turn_moves = self.get_valid_moves(current_turn_all_moves)
        
    def check_move_valid(self, move: Move):
       return move in self.curr_turn_moves

    def _add_en_passant(self, move: Move) -> None:
        if type(move.piece) ==Pawn and abs(move.start.y - move.end.y) ==2:
            y = move.start.y + move.piece.forward_dir
            self.enPassentHistory.append(Pos(y, move.end.x))
        else:
            self.enPassentHistory.append(None)
    
    def king_in_check(self, king: King) -> bool:
        if type(king) != King:
            raise TypeError()
        color_p = king.color
        opp_pieces = self.team_state[self.get_other_color(color_p)].pieces
        for p in opp_pieces:
            if p.isAttacking(king.pos, self.board):
                return True
        return False
    
    def get_valid_moves(self, all_moves: dict[Pos, list[Move]]) -> defaultdict[Pos, list[Move]]:
        legal_moves: dict[Pos, list[Move]] = defaultdict(list)
        king = self.team_state[self.get_color_turn()].king
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
            if self.king_in_check(king) or king.moved!=0 or ts.castle_rights[castle.castle_side]:
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
        ts = self.team_state

        for team in TEAMS:
            krook_pos =  Castle.CASTLE_POS[team]["K"].rook_start
            qrook_pos =  Castle.CASTLE_POS[team]["Q"].rook_start
            rook_pos_vals = {"K": self.board.get_square(*krook_pos),  
                             "Q": self.board.get_square(*qrook_pos)}

            if ts[team].king.moved != 0:
                ts[team].castle_rights["K"] = False
                ts[team].castle_rights["Q"] = False
            else:
                for side in SIDES:
                    rook = rook_pos_vals[side]
                    if isinstance(rook, Rook) and rook.moved == 0 and rook.color == team:
                        ts[team].castle_rights[side] = True
                    else:
                        ts[team].castle_rights[side] = False
        
    def make_move(self, move: Move) -> None:
        if not self.check_move_valid(move):
            raise IllegalMoveError()
        if move.piece.color != self.get_color_turn():
            raise IllegalGameStateError()
        if self.status != Status.ACTIVE:
            raise IllegalGameStateError(f"Game is over. status: {self.status}")
        move.apply(self.board)
        if isinstance(move, NormalMove) and move.capture:
            self.team_state[move.capture.color].lose_piece(move.capture)
        if isinstance(move, Promotion):
            self.team_state[move.piece.color].promote_piece(move.piece, move.promo_piece)
        
        self.half_turn+=1
        self._add_en_passant(move)
        self.update_castle_vars()
        self.upd_game_state_moves()

    def undo_move(self) -> None:
        if not self.move_history:
            return
        move = self.move_history.pop()
        move.undo(self.board)
        if isinstance(move, NormalMove) and move.capture:
            self.team_state[move.capture.color].regain_piece(move.capture)
        if isinstance(move, Promotion):
            self.team_state[move.piece.color].demote_piece(move.piece, move.promo_piece)

        self.half_turn-=1
        self.enPassentHistory.pop()
        self.update_castle_vars()
        self.upd_game_state_moves()

    def check_sufficient_material(self) -> bool:
        piece_counter = defaultdict(int)

        for t in TEAMS:
            for p in self.team_state[t].pieces:
                piece_counter[str(p)] +=1

        total_pawns = piece_counter["P"] + piece_counter["p"]
        
            

        return True

    def check_gamestate_condtion(self) -> Status:
        """Designed to be called at the start of turns"""
        if not self.curr_turn_moves:
            c = self.get_color_turn()
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
        elif self.half_turn - self.last_turn_capture_or_pawn_move[-1] >= 100:
            return Status.DRAW_FIFTY_MOVE
        
        return Status.ACTIVE