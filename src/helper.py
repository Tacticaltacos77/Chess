from typedef import Pos, SquareColor

FILES = "abcdefgh"


def to_square(pos: Pos) -> str:
    """Pos(0, 0) -> 'a8', Pos(7, 7) -> 'h1'."""
    if not (0 <= pos.y < 8 and 0 <= pos.x < 8):
        raise ValueError(f"{pos} is off the board")
    return f"{FILES[pos.x]}{8 - pos.y}"


def to_pos(square: str) -> Pos:
    """'a8' -> Pos(0, 0), 'h1' -> Pos(7, 7)."""
    square = square.strip().lower()
    if len(square) != 2 or square[0] not in FILES or square[1] not in "12345678":
        raise ValueError(f"{square} is not a square name")
    return Pos(8 - int(square[1]), FILES.index(square[0]))

def get_square_color(pos: Pos) -> SquareColor:
    v = (pos.y + pos.x) % 2
    return "light" if v ==0 else "dark"