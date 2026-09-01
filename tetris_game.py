#!/usr/bin/env python3
"""Standalone, playable terminal Tetris used to record traces for the word
clock's tetris transition (clock.py: update_clock_tetris).

Reuses tetris_engine.py (piece shapes/colors/rotation, gravity, scoring and
level speed-up - lifted from github.com/samuelchassot/Tetris) for every
rule, so a trace recorded here obeys exactly the same physics the
transition will replay it with.

Controls:
    left / right   move
    up             rotate
    down           soft drop (not recorded - the transition has its own pace)
    space          hard drop
    q / Esc        quit without saving

On game over, the full trace - every piece played and, for each, the
(action, height) pairs of every left/right/rotate/drop the player made - is
written as JSON to res/tetris_traces/<name>.json. `moves` for a piece is a
list of [action, row] pairs where `row` is the piece's top row at the
moment the action fired, e.g.:

    {"kind": "T", "moves": [["left", 2], ["rotate", 4], ["drop", 6]]}

This is exactly update_clock_tetris's own GAME_SCRIPT shape (an entry per
piece, itself (piece_kind, moves)), converted straight from JSON with
`[(p["kind"], [(a, h) for a, h in p["moves"]]) for p in trace["pieces"]]`.
"""
import curses
import json
import os
import random
import sys
import time

import tetris_engine as te

TRACE_DIR = "res/tetris_traces"

INPUT_POLL_MS = 16  # ~60Hz input polling


def _build_color_pairs() -> dict:
    palette = {
        'I': curses.COLOR_CYAN,
        'O': curses.COLOR_YELLOW,
        'T': curses.COLOR_MAGENTA,
        'L': curses.COLOR_YELLOW,
        'J': curses.COLOR_BLUE,
        'S': curses.COLOR_RED,
        'Z': curses.COLOR_GREEN,
    }
    pairs = {}
    for i, (kind, color) in enumerate(palette.items(), start=1):
        curses.init_pair(i, curses.COLOR_BLACK, color)
        attr = curses.color_pair(i)
        if kind == 'L':
            attr |= curses.A_BOLD  # distinguish from 'O', both yellow on 8-color terminals
        pairs[kind] = attr
    flash_idx = len(palette) + 1
    curses.init_pair(flash_idx, curses.COLOR_BLACK, curses.COLOR_WHITE)
    pairs['FLASH'] = curses.color_pair(flash_idx)
    return pairs


def _draw(stdscr, board, piece, pairs, score: int, level: int, lines: int, flash_rows: set = frozenset()) -> None:
    rows, cols = te.ROWS, te.COLS
    ox, oy = 1, 1

    stdscr.erase()
    stdscr.addstr(0, 0, '+' + '-' * (cols * 2) + '+')
    stdscr.addstr(oy + rows, 0, '+' + '-' * (cols * 2) + '+')
    for r in range(rows):
        stdscr.addstr(oy + r, 0, '|')
        stdscr.addstr(oy + r, ox + cols * 2, '|')

    grid = [row[:] for row in board]
    if piece is not None:
        for r, c in te.absolute_cells(piece):
            if 0 <= r < rows and 0 <= c < cols:
                grid[r][c] = piece['kind']

    for r in range(rows):
        for c in range(cols):
            kind = grid[r][c]
            if r in flash_rows:
                attr = pairs['FLASH']
            elif kind:
                attr = pairs[kind]
            else:
                attr = curses.A_DIM
            stdscr.addstr(oy + r, ox + c * 2, '  ', attr)

    info_x = ox + cols * 2 + 3
    stdscr.addstr(1, info_x, f"Score {score}")
    stdscr.addstr(2, info_x, f"Level {level}")
    stdscr.addstr(3, info_x, f"Lines {lines}")
    stdscr.addstr(5, info_x, "left/right move")
    stdscr.addstr(6, info_x, "up      rotate")
    stdscr.addstr(7, info_x, "down    soft drop")
    stdscr.addstr(8, info_x, "space   hard drop")
    stdscr.addstr(9, info_x, "q       quit")
    stdscr.refresh()


def _flash_lines(stdscr, board, pairs, score: int, level: int, lines: int, full: list) -> None:
    for _ in range(3):
        _draw(stdscr, board, None, pairs, score, level, lines, flash_rows=set(full))
        time.sleep(0.08)
        _draw(stdscr, board, None, pairs, score, level, lines)
        time.sleep(0.08)


def _run(stdscr):
    curses.curs_set(0)
    curses.start_color()
    pairs = _build_color_pairs()
    stdscr.keypad(True)
    stdscr.nodelay(True)
    stdscr.timeout(INPUT_POLL_MS)

    board = te.new_board()
    score = 0
    lines_cleared_total = 0
    level = 1
    fall_delay = te.fall_delay_ms(level) / 1000.0

    trace: list[dict] = []

    def spawn_random():
        kind = random.choice(te.PIECE_KINDS)
        return kind, te.spawn(kind)

    kind, piece = spawn_random()
    moves_log: list[tuple[str, int]] = []
    last_fall = time.time()
    game_over = False

    def land_piece():
        """The current piece has come to rest. Locks it, clears any full
        lines and spawns the next one. Returns False (game over) if the
        piece was still partly off-screen when it landed - i.e. the stack
        reached the top."""
        nonlocal kind, piece, moves_log, score, level, lines_cleared_total, fall_delay

        if te.is_stuck_offscreen(piece):
            return False

        te.lock(board, piece)
        trace.append({'kind': kind, 'moves': [list(m) for m in moves_log]})

        full = te.full_rows(board)
        if full:
            _flash_lines(stdscr, board, pairs, score, level, lines_cleared_total, full)
            te.remove_rows(board, full)
            lines_cleared_total += len(full)
            score += te.score_for_clear(len(full), level)
            level = te.level_for_score(score, level)
            fall_delay = te.fall_delay_ms(level) / 1000.0

        kind, piece = spawn_random()
        moves_log = []
        return True

    while not game_over:
        ch = stdscr.getch()
        if ch in (ord('q'), ord('Q'), 27):
            return None

        if ch == curses.KEY_LEFT:
            if te.try_move(board, piece, -1):
                moves_log.append(('left', piece['top']))
        elif ch == curses.KEY_RIGHT:
            if te.try_move(board, piece, 1):
                moves_log.append(('right', piece['top']))
        elif ch == curses.KEY_UP:
            if te.try_rotate(board, piece):
                moves_log.append(('rotate', piece['top']))
        elif ch == curses.KEY_DOWN:
            te.step_down(board, piece)
            last_fall = time.time()
        elif ch == ord(' '):
            moves_log.append(('drop', piece['top']))
            te.hard_drop(board, piece)
            last_fall = time.time()
            if not land_piece():
                game_over = True

        if not game_over and time.time() - last_fall >= fall_delay:
            last_fall = time.time()
            if not te.step_down(board, piece):
                if not land_piece():
                    game_over = True

        _draw(stdscr, board, None if game_over else piece, pairs, score, level, lines_cleared_total)

    return trace, score, lines_cleared_total


def _next_trace_path() -> str:
    os.makedirs(TRACE_DIR, exist_ok=True)
    idx = 1
    while True:
        path = os.path.join(TRACE_DIR, f"trace_{idx:03d}.json")
        if not os.path.exists(path):
            return path
        idx += 1


def main() -> None:
    result = curses.wrapper(_run)
    if result is None:
        print("Quit - no trace saved.")
        return

    trace, score, lines_cleared_total = result
    path = _next_trace_path()
    with open(path, 'w') as f:
        json.dump({
            'rows': te.ROWS,
            'cols': te.COLS,
            'score': score,
            'lines_cleared': lines_cleared_total,
            'pieces': trace,
        }, f, indent=2)

    print(f"Game over! Score: {score}, lines cleared: {lines_cleared_total}, pieces played: {len(trace)}")
    print(f"Trace written to {path}")


if __name__ == '__main__':
    sys.exit(main())
