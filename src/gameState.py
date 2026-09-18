from typing import TYPE_CHECKING
from errors import IllegalGameStateError
from pieces import *
from collections import defaultdict
if TYPE_CHECKING:
    from typedef import *

TEAMS = ("W","B")
SIDES = ("K","Q")

class Status:
    ACTIVE = 0
    WHITE_CHECKMATE = 1
    BLACK_CHECKMATE = 2
    STALEMATE = 3
    DRAW_REPITITION = 4
    DRAW_FIFTY_MOVE = 5
    DRAW_INSUFFICIANT_MATERIAL = 6


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

class GameState:
    half_turn: int 
    curr_turn_moves: dict[Pos, list[Move]] 
    enPassentSqHistory:list[None|Pos]
    team_state:dict[Team,TeamState] 
    board: Board
    status: Status
    def __init__(self, pieces: list[Piece]):
        self.half_turn = 1
        self.curr_turn_moves = {}
        self.enPassentSqHistory = []
        self.team_state = self._create_teams_states(pieces)
        self.board = Board(pieces)

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
    
    def get_other_color(self, color:Team)->Team:
        if color =="W":
            return "B"
        return "W"
    
    def is_enPassSq(self, y, x)->bool:
        if len(self.enPassentSqHistory)==0:
            return False
        return self.enPassentSqHistory[-1] == Pos(y, x)
        
    def update_half_turn(self, turn_inc)->None:
        if turn_inc not in (1, -1):
            raise ValueError("Can only change turn by value of 1")
        self.half_turn += turn_inc

    
    def getAllMoves(self) -> dict[Pos, list[Move]]:
        pieces = self.team_state[self.get_color_turn()].pieces
        moves: dict[Pos, list[Move]] = {}
        for p in pieces:
            moves[p.pos] = p.moves(self.board, self)
        return moves
    
    def upd_game_state_moves(self) -> None:
        current_turn_all_moves = self.getAllMoves()
        self.curr_turn_moves = self.get_valid_moves(current_turn_all_moves)
        
    def check_move_valid(self, move: Move):
       return move in self.curr_turn_moves.get(move.start, [])
    

    def add_en_passant(self, move: Move)->None:
        if type(move.piece) ==Pawn and abs(move.start.y - move.end.y) ==2:
            self.enPassentSqHistory.append(move.end)
        else:
            self.enPassentSqHistory.append(None)
    
    def king_in_check(self, king: King) -> bool:
        if type(king) != King:
            raise TypeError()
        color_p = king.color
        opp_pieces = self.team_state[self.get_other_color(color_p)].pieces
        for p in opp_pieces:
            if p.isAttacking(king.pos, self.board):
                return True
        return False
    
    def get_valid_moves(self, moves: dict[Pos, list[Move]])->dict[Pos, list[Move]]:
        legal_moves: dict[Pos, list[Move]] = defaultdict(list)
        king = self.team_state[self.get_color_turn()].king
        for p in moves:
            for m in moves[p]:
                if type(m)==Castle and self._validate_castle(m):
                    legal_moves[p].append(m)
                elif isinstance(m, NormalMove):
                    m.apply(self.board)
                    if not self.king_in_check(king):
                        legal_moves[p].append(m)
                    m.undo(self.board)
        return legal_moves
    

    def _validate_castle(self, castle: Castle) -> bool:
            king = castle.piece
            if self.king_in_check(king):
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
        for team in TEAMS:
            krook_pos = CASTLE_ROOK_DEFAULT_POS[team]["K"]
            qrook_pos = CASTLE_ROOK_DEFAULT_POS[team]["Q"]
            rook_pos_vals = {"K": self.board.get_square(*krook_pos),  
                             "Q": self.board.get_square(*qrook_pos)}

            if self.kings[team].has_moved():
                self.castle_rights[team]["K"] = False
                self.castle_rights[team]["Q"] = False
            else:
                for side in SIDES:
                    rook = rook_pos_vals[side]
                    if isinstance(rook, Rook) and not rook.has_moved():
                        self.castle_rights[team][side] = True
                    else:
                        self.castle_rights[team][side] = False
        
    def make_move(self, move: Move) -> None:
        if self.status.WHITE_CHECKMATE or self.status.BLACK_CHECKMATE:
            return
        move.apply(self.board)
        if isinstance(move, NormalMove) and move.capture:
            self.add_captured_piece(move.capture)
        if isinstance(move, Promotion):
            self.add_promoted_piece(move.piece, move.promo_piece)

    def undo_move(self, move: Move):
        move.undo(self.board)
        if isinstance(move, NormalMove) and move.capture:
            self.return_captured_piece(move.capture)
        if isinstance(move, Promotion):
            self.return_promoted_piece(move.piece, move.promo_piece)


    def check_gamestate_condtion(self)-> GameStatus:


        return "checkmate"
        

