# Chess

A Python chess library for legal move generation, game state management, FEN positions, draw detection, and reversible move execution.

I built this project because I enjoy chess and wanted a challenging way to practice designing and reasoning through a state driven application.

## Features

- Legal move generation and validation, including checks and pinned pieces.
- Castling, en passant, promotion, checkmate, and stalemate.
- Threefold repetition, fifty move rule, and insufficient material detection.
- FEN parsing for creating and exporting game positions.
- Reversible move application for position searching and future engine usage.

## Installation

Requires Python 3.12 or newer.

Clone the repository and install the project:

```bash
git clone https://github.com/Tacticaltacos77/Chess.git
cd Chess
pip install .
```

To install directly from GitHub:

```bash
pip install git+https://github.com/Tacticaltacos77/Chess.git
```

For development and testing:

```bash
git clone https://github.com/Tacticaltacos77/Chess.git
cd Chess
pip install -e .
pip install pytest
pytest
```

## Usage

### Creating a game

```python
from chesslibrary import Game

game = Game()

print(game.get_fen())
# rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1
```

The game keeps track of the current position, turn, castling rights, en passant state, move counters, repetition history, legal moves, and game status.

### Making moves

`parse_move()` converts the library's move notation into the matching legal move for the current position.

```python
from chesslibrary import Game

game = Game()

move = game.parse_move("pe2-e4")
game.make_move(move)

move = game.parse_move("pe7-e5")
game.make_move(move)

print(game.get_fen())
```
If the move is not legal in the current position, `parse_move()` raises an `IllegalMoveError`.

Move strings use the piece, starting square, move type, and ending square:

| Move | Example |
| --- | --- |
| Pawn | `pe2-e4` |
| Piece | `Ng1-f3` |
| Capture | `Bf1xc4`, `pe4xd5` |
| Promotion | `pe7-e8=Q` |
| Castling | `O-O`, `O-O-O` |

### Getting legal moves

Legal moves for the current turn can also be accessed directly:

```python
game = Game()

for moves in game.get_curr_turn_moves().values():
    for move in moves:
        print(move)
```

Each legal move is represented as a `Move` object that can be passed directly into `Game.make_move()`.

### Loading positions with FEN

A game can be initialized from any valid FEN position:

```python
from chesslibrary import Game

game = Game("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")

print(game.get_fen())
```

The FEN parser validates piece placement, castling rights, en passant state, turn information, and move counters before creating the game.

### Searching positions

Moves can be made and undone without rebuilding the game, allowing the library to be used for recursive position searching.

```python
from chesslibrary import Game, Status

game = Game("6k1/5ppp/8/8/8/8/8/R5K1 w - - 0 1")

for moves in game.get_curr_turn_moves().values():
    for move in moves:
        game.make_move(move)

        if game.status == Status.WHITE_WINS:
            print(f"{move} is checkmate")

        game.undo_move()
```

## Architecture

### Move generation and validation

Piece movement and legal move validation are intentionally separated.

Pieces generate moves based on their individual movement rules. The `Game` layer then filters those moves against game level rules/state, such as whether making the move would leave the player's king in check.

This keeps basic piece movement separate from rules that depend on the state of the entire game and makes each layer easier to test.

### Board mutations and game state transitions

Checking whether a move is legal requires temporarily applying the move to the board and checking the position to see if the king is in check or not.

Using the full `Game.make_move()` process for every potential move would unnecessarily update the current turn allowed moves, repetition history, en passant state, castling rights, and other persistent game data which would make it much slower.

Moves therefore support lightweight `apply()` and `undo()` directly against the board. 

### Reversible move objects

Different move types handle the behavior needed to apply and undo themselves.

`NormalMove`, `Castle`, `Promotion`, and `EnPassant` share a common move class, so the board level move logic does not need a large dispatcher to decide how each type of move should be applied or reversed.

Some game rules still depend on the type of move being made, but the actual board changes and the information needed to undo them stay with the move object itself. For example, a capture keeps track of the captured piece and a promotion keeps track of the promoted piece.

### Shared piece movement

Early versions of the project implemented movement separately for each piece.

The current design uses direction offsets and maximum movement distances to share the core movement algorithm between pieces when possible. Rooks, bishops, queens, and knights use this system, while pieces with special rules such as pawns and kings extend or override the behavior they need.

This reduced duplicated movement logic and made the rules easier to maintain.

## Challenges

### Separating move generation from legal move validation

One of the harder design problems was deciding where move legality should be handled.

A piece can determine how it is allowed to move, but it cannot determine whether that move is legal for the current game by itself. For example, a rook may be able to move to a square based on its movement rules, but the move still cannot be played if it leaves its own king in check.

Earlier versions mixed more of this logic together. I eventually separated the two steps: pieces generate possible moves, and the `Game` layer filters them based on the current game state.

This made the responsibilities of each layer clearer and made it easier to test piece movement separately from full chess rules.

### Applying moves without changing the full game state

Legal move validation requires temporarily making a move and checking the resulting position.

At first, it seemed natural to use the same move process everywhere. The problem is that a real game move updates much more than the board. It changes things such as turn state, en passant, castling rights, repetition history, move counters, and the list of legal moves.

Doing all of that just to test every possible move would add unnecessary work and make temporary move checking much harder to reason about.

I ended up separating the lower level board change from the full game update. Move objects can apply and undo themselves directly on the board, while `Game.make_move()` handles the additional state that should only change when an actual move is played.

### Making moves fully reversible

Adding undo support became more complicated than simply moving a piece back to its original square.

Captures need to restore the captured piece, promotions replace one piece with another, castling moves two pieces, and game level state such as en passant, move counters, repetition tracking, and castling rights also needs to return to its previous value.

This became especially important once I wanted the library to support future engine searching, where many moves may be made and undone while exploring positions.

The final design keeps the information needed to reverse board changes on the move objects while the `Game` keeps the history needed to restore the rest of the game state.

### Handling rule interactions and edge cases

Implementing the individual chess rules was not too difficult on its own. The harder part was making sure they still behaved correctly when they interacted with the rest of the game state.

Rules such as castling, en passant, repetition, promotion, check, and draw detection all depend on more than just the current piece positions. For example, an en passant capture can expose the king to check, castling depends on both move history and attacked squares, and repetition depends on whether two positions are actually considered the same under chess rules.

A large part of the project was finding these edge cases, understanding what state each rule depended on, and writing tests for situations where multiple rules affected the same position.

## Testing

The project uses `pytest` to test piece movement, chess rules, state transitions, invalid states, and edge cases.

Tests cover:

- Normal piece movement and captures.
- Promotion.
- En passant.
- Castling.
- Check and pinned pieces.
- Checkmate and stalemate.
- Draw conditions.
- Move application and reversal.
- FEN parsing and serialization.
- Position repetition.
- Illegal moves and invalid game states.

The move generator is also tested using **perft**, a standard chess programming technique that recursively counts all legal positions reachable to a given depth.

For the standard starting position, the library currently verifies:

| Depth | Positions |
| ---: | ---: |
| 1 | 20 |
| 2 | 400 |
| 3 | 8,902 |
| 4 | 197,281 |

These tests help catch errors in move generation that may only appear several moves into a position.

## Roadmap

- Build a search based chess engine using the reversible move system.
- Create a multiplayer chess application using this library as the game rules layer.
- Continue expanding test coverage for FEN validation and unusual game state edge cases.