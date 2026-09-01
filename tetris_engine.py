"""Shared Tetris physics: piece shapes, colors, and pure board logic.

Used both by the word-clock's tetris transition (clock.py, via
update_clock_tetris) and by the standalone playable game (tetris_game.py)
that records traces for it. Keeping the rules in one place guarantees a
trace recorded while playing replays identically in the transition.

Piece shapes/colors and the movement feel are inspired by
github.com/samuelchassot/Tetris.
"""

ROWS = 10
COLS = 11

PIECE_SHAPES = {
    'I': [
        [[0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0], [0, 1, 0, 0]],
        [[0, 0, 0, 0], [1, 1, 1, 1], [0, 0, 0, 0], [0, 0, 0, 0]],
    ],
    'O': [
        [[1, 1], [1, 1]],
    ],
    'T': [
        [[0, 1, 0], [1, 1, 1], [0, 0, 0]],
        [[0, 1, 0], [0, 1, 1], [0, 1, 0]],
        [[0, 0, 0], [1, 1, 1], [0, 1, 0]],
        [[0, 1, 0], [1, 1, 0], [0, 1, 0]],
    ],
    'L': [
        [[1, 1, 1], [1, 0, 0], [0, 0, 0]],
        [[0, 1, 0], [0, 1, 0], [0, 1, 1]],
        [[0, 0, 1], [1, 1, 1], [0, 0, 0]],
        [[1, 1, 0], [0, 1, 0], [0, 1, 0]],
    ],
    'J': [
        [[0, 0, 0], [1, 1, 1], [0, 0, 1]],
        [[0, 1, 1], [0, 1, 0], [0, 1, 0]],
        [[1, 0, 0], [1, 1, 1], [0, 0, 0]],
        [[0, 1, 0], [0, 1, 0], [1, 1, 0]],
    ],
    'S': [
        [[0, 0, 0], [0, 1, 1], [1, 1, 0]],
        [[0, 1, 0], [0, 1, 1], [0, 0, 1]],
        [[0, 1, 1], [1, 1, 0], [0, 0, 0]],
        [[1, 0, 0], [1, 1, 0], [0, 1, 0]],
    ],
    'Z': [
        [[0, 0, 0], [1, 1, 0], [0, 1, 1]],
        [[0, 0, 1], [0, 1, 1], [0, 1, 0]],
        [[1, 1, 0], [0, 1, 1], [0, 0, 0]],
        [[0, 1, 0], [1, 1, 0], [1, 0, 0]],
    ],
}

PIECE_COLORS = {
    'I': (0, 240, 240),    # cyan
    'O': (240, 240, 0),    # yellow
    'T': (160, 0, 240),    # purple
    'L': (240, 160, 0),    # orange
    'J': (0, 90, 240),     # blue
    'S': (220, 20, 20),    # red
    'Z': (20, 200, 20),    # green
}

PIECE_KINDS = list(PIECE_SHAPES.keys())

# Scoring, leveling and fall speed, taken directly from the reference game's
# Grille/Jeu classes: 40/100/300/1200 points per 1/2/3/4 lines (times the
# current level), a new level every time score >= 800 * level^2, and the
# fall timer multiplied by 0.7 on every level up.
LINE_CLEAR_SCORES = {1: 40, 2: 100, 3: 300, 4: 1200}
INITIAL_FALL_MS = 600
LEVEL_SPEED_FACTOR = 0.7
MIN_FALL_MS = 50


def score_for_clear(n_lines: int, level: int) -> int:
    return LINE_CLEAR_SCORES.get(n_lines, 0) * level


def level_for_score(score: int, level: int = 1) -> int:
    while score >= 800 * level * level:
        level += 1
    return level


def fall_delay_ms(level: int) -> int:
    delay = INITIAL_FALL_MS
    for _ in range(1, level):
        delay = int(delay * LEVEL_SPEED_FACTOR)
    return max(delay, MIN_FALL_MS)


# A piece is a plain dict: {'kind': str, 'rot': int, 'top': int, 'left': int}
# 'top'/'left' is the top-left corner of its rotation-state bounding box.
# 'top' can be negative while the piece is still falling in from above the
# visible board.

# A board cell holds the piece kind letter that locked there, or None if
# empty - callers map kind -> color themselves via PIECE_COLORS (or their
# own palette, as the curses game does).
Board = list  # list[list[str | None]]


def new_board(rows: int = ROWS, cols: int = COLS) -> Board:
    return [[None] * cols for _ in range(rows)]


def shape_cells(kind: str, rot: int) -> list[tuple[int, int]]:
    grid = PIECE_SHAPES[kind][rot % len(PIECE_SHAPES[kind])]
    return [(i, j) for i, row in enumerate(grid) for j, v in enumerate(row) if v]


def absolute_cells(piece: dict) -> list[tuple[int, int]]:
    return [(piece['top'] + i, piece['left'] + j) for i, j in shape_cells(piece['kind'], piece['rot'])]


def collides(board: Board, cells: list[tuple[int, int]], rows: int = ROWS, cols: int = COLS) -> bool:
    for r, c in cells:
        if c < 0 or c >= cols or r >= rows:
            return True
        if r >= 0 and board[r][c] is not None:
            return True
    return False


def spawn(kind: str, cols: int = COLS) -> dict:
    width = len(PIECE_SHAPES[kind][0][0])
    height = len(PIECE_SHAPES[kind][0])
    return {'kind': kind, 'rot': 0, 'top': -height, 'left': (cols - width) // 2}


def try_move(board: Board, piece: dict, dcol: int, rows: int = ROWS, cols: int = COLS) -> bool:
    """Attempt to translate the piece horizontally. Mutates piece and
    returns True on success, leaves it untouched and returns False if that
    would collide."""
    moved = dict(piece, left=piece['left'] + dcol)
    if collides(board, absolute_cells(moved), rows, cols):
        return False
    piece['left'] = moved['left']
    return True


def try_rotate(board: Board, piece: dict, rows: int = ROWS, cols: int = COLS) -> bool:
    """Attempt to rotate clockwise. Mutates piece and returns True on
    success. No wall kicks, matching the reference game: a rotation that
    would collide simply fails and the piece stays as it was."""
    rotated = dict(piece, rot=piece['rot'] + 1)
    if collides(board, absolute_cells(rotated), rows, cols):
        return False
    piece['rot'] = rotated['rot']
    return True


def step_down(board: Board, piece: dict, rows: int = ROWS, cols: int = COLS) -> bool:
    """Attempt to fall one row. Mutates piece and returns True on success,
    returns False (piece unchanged) if the row below is blocked."""
    moved = dict(piece, top=piece['top'] + 1)
    if collides(board, absolute_cells(moved), rows, cols):
        return False
    piece['top'] = moved['top']
    return True


def hard_drop(board: Board, piece: dict, rows: int = ROWS, cols: int = COLS) -> None:
    while step_down(board, piece, rows, cols):
        pass


def lock(board: Board, piece: dict, rows: int = ROWS, cols: int = COLS) -> None:
    for r, c in absolute_cells(piece):
        if 0 <= r < rows and 0 <= c < cols:
            board[r][c] = piece['kind']


def full_rows(board: Board) -> list[int]:
    """Row indices that are completely filled. Does not mutate the board -
    callers can use this to run a "flash" effect before removing them."""
    return [r for r, row in enumerate(board) if all(cell is not None for cell in row)]


def remove_rows(board: Board, rows_to_remove: list[int], rows: int = ROWS, cols: int = COLS) -> None:
    """Remove the given (already-identified) full rows and insert blank
    rows at the top so the board keeps its size."""
    if not rows_to_remove:
        return
    to_remove = set(rows_to_remove)
    blank: list[list] = [[None] * cols for _ in rows_to_remove]
    remaining = [board[r] for r in range(rows) if r not in to_remove]
    board[:] = blank + remaining


def is_stuck_offscreen(piece: dict) -> bool:
    """True if any of the piece's cells are still above the visible board
    (row < 0). A freshly spawned piece always starts fully off-screen (see
    spawn()), so it can never collide until it starts entering the board -
    call this once the piece has come to rest (step_down returned False)
    to detect game over: the stack reached high enough that the piece got
    stuck before fully appearing."""
    return any(r < 0 for r, _ in absolute_cells(piece))
