from board import *
#Test actual board values (objects) and check if the objects are correct. ie correct position 
def test_default_board():
    b = Board("James", "Other")
    assert b.get_board() == [
            ["R","N","B","Q","K","B","N","R"],
            ["P","P","P","P","P","P","P","P"],
            [".",".",".",".",".",".",".","."],
            [".",".",".",".",".",".",".","."],
            [".",".",".",".",".",".",".","."],
            [".",".",".",".",".",".",".","."],
            ["p","p","p","p","p","p","p","p"],
            ["r","n","b","q","k","b","n","r"]
            ]

def set_board_test_castle(b):
    b.board = [
            [Rook("B", (0,0)),".", ".",".", King("B",(4,0)),".", ".", Rook("B",(7,0))],
            [".",".",".",".",".",".",".","."],
            [".",".",".",".",".",".",".","."],
            [".",".",".",".",".",".",".","."],
            [".",".",".",".",".",".",".","."],
            [".",".",".",".",".",".",".","."],
            [".",".",".",".",".",".",".","."],
            [Rook("W", (0,7)),".", ".",".", King("W",(4,7)), ".", ".", Rook("W",(7,7))]]

def set_board_test_bishop(b):
     b.board = [[".",".", ".",".", Bishop("B", (0,4)),".", ".","."],
            [".",".",".",".",".",King("W", (1, 5)),".","."],
            [".",".",".",".",".",".",".","."],
            [".",".",".",".",".",".",".","."],
            [".",".",".",".",".",".",".","."],
            [".",".",".",Bishop("W", (5,3)),".",".",".","."],
            [".",".",".",".",".",".",".","."],
            [".",".",".",".",".",".",".","."]]

def test_valid_moves():
    b = Board("James", "Other")
    moves = b.check_valid_moves(b.white_pieces)
    for m in moves:
        print(m)
    
    print("================================")
    moves = b.check_valid_moves(b.black_pieces)
    for m in moves:
        print(m)

def check_pieces_pos(b):
    for p in b.white_pieces:
        print(f"piece: {p}, color:{p.color}, pos: {p.pos} ")
        
    
def test_apply():
    b = Board("James", "Other")
    print(b)
    move = Move(b.white_pieces[0], (0,5))
    b.apply_move(move)
    check_pieces_pos(b)
    b.undo_apply(move)
    print(b)

def test_white_castle_king_side():
    b = Board("James", "Other")
    set_board_test_castle(b)
    print(b)
    print("==================")
    b.apply_move(Castle(b.white_king,"K"))
    print(b)
    print("==================")

def test_white_castle_queen_side():
    b = Board("James", "Other")
    set_board_test_castle(b)
    print(b)
    print("==================")
    b.apply_move(Castle(b.white_king,"Q"))
    print(b)
    print("==================")

def test_black_castle_king_side():
    b = Board("James", "Other")
    set_board_test_castle(b)
    print(b)
    print("==================")
    b.apply_move(Castle(b.black_king,"K"))
    print(b)
    print("==================")

def test_black_castle_queen_side():
    b = Board("James", "Other")
    set_board_test_castle(b)
    print(b)
    print("==================")
    b.apply_move(Castle(b.black_king,"Q"))
    print(b)
    print("==================")

def test_bishop_moves():
    b = Board()
    set_board_test_bishop(b)
    print(b)
    moves = b.check_piece_valid_moves(b.board[5][3])
    
    for i in moves:
        print(i.end)
    return moves
print(test_bishop_moves())