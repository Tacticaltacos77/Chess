from typing import TYPE_CHECKING
from errors import IllegalGameStateError
from pieces import *
if TYPE_CHECKING:
    from move import Move
    from typedef import *

TEAMS = ("W","B")
SIDES = ("K","Q")
CASTLE_CHECK_POS = {"W": {"Q": (Pos(7,3), Pos(7,2)), "K": (Pos(7,5), Pos(7,6))},
                    "B": {"Q": (Pos(0,3), Pos(0,2)), "K": (Pos(0,5), Pos(0,6))}}

CASTLE_ROOK_END_POS = {"W": {"Q": Pos(7,3), "K": Pos(7,5)}, 
                       "B": {"Q": Pos(0,3), "K": Pos(0,5)}}

CASTLE_ROOK_DEFAULT_POS = {"W": {"Q": Pos(7, 0), "K": Pos(7,7)}, 
                           "B": {"Q": Pos(0, 0), "K": Pos(0,7)}}

class GameState:
    half_turn: int 
    curr_turn_moves: dict[Pos, list[Move]] 
    enPassentSqHistory:list[None|Pos]
    kings: Teams[King]
    pieces: Teams[list[Piece]]
    captured_pieces: Teams[list[Capturable]]
    castle_rights: Teams[dict[Side, bool]]
    board: Board

    def __init__(self):
        self.half_turn = 1
        self.curr_turn_moves = {}
        self.enPassentSqHistory = []
        self.pieces = self._get_starting_pieces()
        self.kings = self._find_kings(self.pieces)
        self.cap_pieces = {"W":[], "B": []}
        self.castle_rights = {"W": {"Q":True, "K": True}, "B": {"Q":True, "K": True}}
        self.board = Board(self.pieces)

    def _get_starting_pieces(self)->dict[Team, list[Piece]]:
        starting_pieces: dict[Team,list[Piece]] = {"W":[Pawn("W",6,0), Pawn("W",6,1),Pawn("W",6,2),
                    Pawn("W",6,3),Pawn("W",6,4),Pawn("W",6,5),Pawn("W",6,6),Pawn("W",6,7),
                    Rook("W", 7,0),Knight("W", 7,1), Bishop("W",7,2),Queen("W",7,3),
                    King("W",7,4), Bishop("W",7,5), Knight("W",7,6), Rook("W",7,7)], 
                    
                        "B":[Rook("B", 0,0),Knight("B", 0, 1), Bishop("B", 0, 2),
                    Queen("B", 0, 3), King("B", 0, 4), Bishop("B",0, 5),
                    Knight("B",0,6), Rook("B",0,7), Pawn("B",1,0), Pawn("B",1,1),
                    Pawn("B",1,2),Pawn("B",1,3),Pawn("B",1,4),Pawn("B",1,5),
                    Pawn("B",1,6),Pawn("B",1,7)]}
        
        return starting_pieces

    def _find_kings(self, pieces: Teams[list[Piece]])->Teams[King]:
        kings = {}
        for team in TEAMS:
            for tpiece in pieces[team]:
                if isinstance(tpiece, King):
                    kings[team] = tpiece
                    break
        return kings
    
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

    def rmv_piece_from_pieces(self, p: Piece) -> None:
        for i in range(len(self.pieces[p.color])):
            if self.pieces[p.color][i] is p:
                self.pieces[p.color].pop(i)
                return
        raise IllegalGameStateError(f"Tried to remove {p} from {p.color} pieces but it wasn't there")
    
    def getAllMoves(self) -> dict[Pos, list[Move]]:
        pieces = self.pieces[self.get_color_turn()]
        moves: dict[Pos, list[Move]] = {}
        for p in pieces:
            moves[p.pos] = p.moves(self.board, self)
        return moves
    
    def upd_game_state_moves(self) -> None:
        current_turn_all_moves = self.getAllMoves()
        self.curr_turn_moves = self.get_valid_moves(current_turn_all_moves)
        
    def check_move_valid(self, move: Move):
       return move in self.curr_turn_moves[move.start]
    
    def add_en_passant(self, move: Move)->None:
        if type(move.piece) ==Pawn and abs(move.start.y - move.end.y) ==2:
            self.enPassentSqHistory.append(move.end)
        else:
            self.enPassentSqHistory.append(None)
    
    def king_in_check(self, king: King) -> bool:
        if type(king) != King:
            TypeError()
        color_p = king.color
        opp_pieces = self.pieces[self.get_other_color(color_p)]
        for p in opp_pieces:
            if p.isAttacking(king.pos, self.board):
                return True
        return False
    
    def get_valid_moves(self, moves: dict[Pos, list[Move]])->dict[Pos, list[Move]]:
        legal_moves: dict[Pos, list[Move]] = {}
        king = self.kings[self.get_color_turn()]
        assert king is not None
        for p in moves: 
            for m in moves[p]:   
                if type(m)==Castle and self._validate_castle(m):
                    legal_moves[p].append(m)
                else:
                    m.apply(self.board) 
                    if not self.king_in_check(king):
                        legal_moves[p].append(m)
                    m.undo(self.board)
        return legal_moves
    

    def _validate_castle(self, move:Castle) -> bool:
            king = move.piece
            if self.king_in_check(king):
                return False
            p = move.piece
            opp_pieces = self.pieces[self.get_other_color(p.color)]
            for pos in CASTLE_CHECK_POS[king.color][move.castle_side]:
                if self.board.get_square(*pos) != None:
                    return False
                for opp_p in opp_pieces:
                    if opp_p.isAttacking(pos, self.board):
                        return False    
            return True
    

    def add_captured_piece(self, cap_piece: Capturable) -> None:
        color = cap_piece.color
        for i in range(len(self.pieces[color])):
            if self.pieces[color][i] is cap_piece:
                self.pieces[color].pop(i)
                break
        self.cap_pieces[color].append(cap_piece)
       
    def return_captured_piece(self, cap_piece: Capturable) -> None:
        popped = self.cap_pieces[cap_piece.color].pop()
        if popped is not cap_piece:
            raise IllegalGameStateError("")
        self.pieces[cap_piece.color].append(popped)


    def add_promoted_piece(self, pawn: Pawn, piece: Capturable) -> None:
        self.rmv_piece_from_pieces(pawn)
        self.pieces[pawn.color].append(piece)


    def return_promoted_piece(self, pawn: Pawn, piece: Capturable) -> None:
        self.rmv_piece_from_pieces(piece)
        self.pieces[pawn.color].append(pawn)

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
        

