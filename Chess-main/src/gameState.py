from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from move import Move
    from pieces import *
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
    captured_pieces: Teams[list[Piece]]
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

    def getAllMoves(self)->dict[Pos, list[Move]]:
        pieces = self.pieces[self.get_color_turn()]
        moves: dict[Pos, list[Move]] = {}
        for p in pieces:
            moves[p.pos] = p.moves(self.board, self)
        return moves
    
    def upd_game_state_moves(self):
        current_turn_all_moves = self.getAllMoves()
        self.curr_turn_moves = self.validate_legal(current_turn_all_moves)
        
    def check_move_valid(self, move: Move):
       return move in self.curr_turn_moves[move.start]
    
    def add_en_passant(self, move: Move)->None:
        if type(move.piece) ==Pawn and abs(move.start.y - move.end.y) ==2:
            self.enPassentSqHistory.append(move.end)
        else:
            self.enPassentSqHistory.append(None)
    
    def king_in_check(self, king: King):
        if type(king) != King:
            TypeError()
        color_p = king.color
        opp_pieces = self.pieces[self.get_other_color(color_p)]
        for p in opp_pieces:
            if p.isAttacking(king.pos, self.board):
                return True
        return False
    
    def validate_legal(self, moves: dict[Pos, list[Move]])->dict[Pos, list[Move]]:
        legal_moves: dict[Pos, list[Move]] = {}
        king = self.kings[self.get_color_turn()]
        assert king is not None
        for p in moves: 
            for m in moves[p]:   
                if type(m)==Castle and self._validate_castle(m):
                    legal_moves[p].append(m)
                    continue
                elif self.apply_move(m) and not self.king_in_check(king):
                    legal_moves[p].append(m)
                    self.undo_apply(m)
        return legal_moves
    

    def _validate_castle(self, move:Castle)->bool:
            king:Piece= move.piece
            if not isinstance(king, King):
                raise ValueError(f"Castle objects piece must be a king. Instead was ({king})")
            
            if self.king_in_check(king):
                return False
            p = move.piece
            opp_pieces = self.pieces[self.get_other_color(p.color)]
            ######
            for gap_pos in CASTLE_CHECK_POS[king.color][move.castle_side]:
                    
                    return True 
            return False
    
    def return_p(self, ret_piece: Piece):
        self.cap_pieces[ret_piece.color].pop()
        self.pieces[ret_piece.color].append(ret_piece)
        self.board.place_piece(ret_piece)


    def capture_p(self, cap_piece: Piece)->None:
        if isinstance(cap_piece, King):
            raise TypeError("Can't capture a King")
        color = cap_piece.color
        for i in range(len(self.pieces[color])):
            if self.pieces[color][i] is cap_piece:
                self.pieces[color].pop(i)
                break
        self.cap_pieces[color].append(cap_piece)
        self.board.remove_piece(cap_piece)


    def update_castle_vars(self):
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
                        self.castle_rights[team][side] = False
                    else:
                        self.castle_rights[team][side] = True
    
    def apply_move(self, move: Move):
        pass




    def undo_apply(self, move: Move):
        pass
        
    def promote_pawn(self, move:Promotion):
        p = move.piece
        self.board.remove_piece(p)
        self.board.place_piece(move.promo)
        self.pieces[p.color].append(p)

    def demote_pawn(self, move: Promotion):
        p = move.piece
        self.board.remove_piece
        popped = self.pieces[p.color].pop()
        if popped is not move.promo:
            raise ValueError(f"Piece removed from {p.color} Player was ({popped}) not the promoted piece ({move.promo})")
        
