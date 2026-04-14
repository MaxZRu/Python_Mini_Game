"""Core game logic for a simple Tetris implementation."""

from __future__ import annotations

import random
from dataclasses import dataclass

from config import GRID_HEIGHT, GRID_WIDTH


PIECES = {
    1: [  # I
        [[1, 1, 1, 1]],
        [[1], [1], [1], [1]],
    ],
    2: [  # O
        [[1, 1], [1, 1]],
    ],
    3: [  # T
        [[0, 1, 0], [1, 1, 1]],
        [[1, 0], [1, 1], [1, 0]],
        [[1, 1, 1], [0, 1, 0]],
        [[0, 1], [1, 1], [0, 1]],
    ],
    4: [  # L
        [[0, 0, 1], [1, 1, 1]],
        [[1, 0], [1, 0], [1, 1]],
        [[1, 1, 1], [1, 0, 0]],
        [[1, 1], [0, 1], [0, 1]],
    ],
    5: [  # J
        [[1, 0, 0], [1, 1, 1]],
        [[1, 1], [1, 0], [1, 0]],
        [[1, 1, 1], [0, 0, 1]],
        [[0, 1], [0, 1], [1, 1]],
    ],
    6: [  # S
        [[0, 1, 1], [1, 1, 0]],
        [[1, 0], [1, 1], [0, 1]],
    ],
    7: [  # Z
        [[1, 1, 0], [0, 1, 1]],
        [[0, 1], [1, 1], [1, 0]],
    ],
}


@dataclass
class Piece:
    kind: int
    rotation: int
    x: int
    y: int

    @property
    def shape(self) -> list[list[int]]:
        return PIECES[self.kind][self.rotation]


class TetrisGame:
    def __init__(self) -> None:
        self.grid: list[list[int]] = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.game_over = False
        self.current_piece = self._spawn_piece()

    def _spawn_piece(self) -> Piece:
        kind = random.randint(1, 7)
        shape = PIECES[kind][0]
        x = (GRID_WIDTH - len(shape[0])) // 2
        y = 0
        piece = Piece(kind=kind, rotation=0, x=x, y=y)
        if not self._valid_position(piece, piece.x, piece.y, piece.rotation):
            self.game_over = True
        return piece

    def _valid_position(self, piece: Piece, x: int, y: int, rotation: int) -> bool:
        shape = PIECES[piece.kind][rotation]
        for row_idx, row in enumerate(shape):
            for col_idx, value in enumerate(row):
                if value == 0:
                    continue
                new_x = x + col_idx
                new_y = y + row_idx
                if new_x < 0 or new_x >= GRID_WIDTH or new_y >= GRID_HEIGHT:
                    return False
                if new_y >= 0 and self.grid[new_y][new_x] != 0:
                    return False
        return True

    def move_left(self) -> None:
        if self.game_over:
            return
        if self._valid_position(self.current_piece, self.current_piece.x - 1, self.current_piece.y, self.current_piece.rotation):
            self.current_piece.x -= 1

    def move_right(self) -> None:
        if self.game_over:
            return
        if self._valid_position(self.current_piece, self.current_piece.x + 1, self.current_piece.y, self.current_piece.rotation):
            self.current_piece.x += 1

    def rotate(self) -> None:
        if self.game_over:
            return
        next_rotation = (self.current_piece.rotation + 1) % len(PIECES[self.current_piece.kind])
        if self._valid_position(self.current_piece, self.current_piece.x, self.current_piece.y, next_rotation):
            self.current_piece.rotation = next_rotation

    def step_down(self) -> bool:
        if self.game_over:
            return False
        if self._valid_position(self.current_piece, self.current_piece.x, self.current_piece.y + 1, self.current_piece.rotation):
            self.current_piece.y += 1
            return True
        self._lock_piece()
        return False

    def _lock_piece(self) -> None:
        shape = self.current_piece.shape
        for row_idx, row in enumerate(shape):
            for col_idx, value in enumerate(row):
                if value == 0:
                    continue
                grid_x = self.current_piece.x + col_idx
                grid_y = self.current_piece.y + row_idx
                if 0 <= grid_y < GRID_HEIGHT and 0 <= grid_x < GRID_WIDTH:
                    self.grid[grid_y][grid_x] = self.current_piece.kind
        cleared_lines = self._clear_lines()
        self.score += cleared_lines * 100
        self.current_piece = self._spawn_piece()

    def _clear_lines(self) -> int:
        new_grid = [row for row in self.grid if any(cell == 0 for cell in row)]
        cleared_count = GRID_HEIGHT - len(new_grid)
        for _ in range(cleared_count):
            new_grid.insert(0, [0 for _ in range(GRID_WIDTH)])
        self.grid = new_grid
        return cleared_count

    def get_render_grid(self) -> list[list[int]]:
        render_grid = [row[:] for row in self.grid]
        if self.game_over:
            return render_grid
        for row_idx, row in enumerate(self.current_piece.shape):
            for col_idx, value in enumerate(row):
                if value == 0:
                    continue
                grid_x = self.current_piece.x + col_idx
                grid_y = self.current_piece.y + row_idx
                if 0 <= grid_y < GRID_HEIGHT and 0 <= grid_x < GRID_WIDTH:
                    render_grid[grid_y][grid_x] = self.current_piece.kind
        return render_grid

    def reset(self) -> None:
        self.grid = [[0 for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
        self.score = 0
        self.game_over = False
        self.current_piece = self._spawn_piece()
