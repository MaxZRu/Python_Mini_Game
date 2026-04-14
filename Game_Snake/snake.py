"""Core game logic for a simple grid-based Snake implementation."""

from __future__ import annotations

import random

from config import GRID_HEIGHT, GRID_WIDTH, START_LENGTH

Position = tuple[int, int]
Direction = tuple[int, int]


class SnakeGame:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        center_x = GRID_WIDTH // 2
        center_y = GRID_HEIGHT // 2
        self.snake: list[Position] = [
            (center_x - offset, center_y) for offset in range(START_LENGTH)
        ]
        self.direction: Direction = (1, 0)
        self.pending_direction: Direction = self.direction
        self.score = 0
        self.game_over = False
        self.food = self._spawn_food()

    def set_direction(self, new_direction: Direction) -> None:
        if self.game_over:
            return
        if new_direction == (0, 0):
            return
        if self._is_opposite(self.direction, new_direction):
            return
        self.pending_direction = new_direction

    def update(self) -> None:
        if self.game_over:
            return

        self.direction = self.pending_direction
        head_x, head_y = self.snake[0]
        delta_x, delta_y = self.direction
        new_head = (head_x + delta_x, head_y + delta_y)

        if not self._is_inside_grid(new_head):
            self.game_over = True
            return
        if new_head in self.snake:
            self.game_over = True
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            self.food = self._spawn_food()
        else:
            self.snake.pop()

    def _spawn_food(self) -> Position:
        free_cells = [
            (x, y)
            for y in range(GRID_HEIGHT)
            for x in range(GRID_WIDTH)
            if (x, y) not in self.snake
        ]
        return random.choice(free_cells)

    @staticmethod
    def _is_opposite(a: Direction, b: Direction) -> bool:
        return a[0] == -b[0] and a[1] == -b[1]

    @staticmethod
    def _is_inside_grid(position: Position) -> bool:
        x, y = position
        return 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT
