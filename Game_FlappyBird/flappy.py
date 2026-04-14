"""Core game logic for a simple Flappy Bird implementation."""

from __future__ import annotations

import random
from dataclasses import dataclass

import pygame

from config import (
    BIRD_GRAVITY,
    BIRD_JUMP_VELOCITY,
    BIRD_RADIUS,
    BIRD_X,
    GROUND_TOP,
    PIPE_GAP,
    PIPE_MARGIN,
    PIPE_SPEED,
    PIPE_SPAWN_INTERVAL_MS,
    PIPE_WIDTH,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)


@dataclass
class PipePair:
    x: float
    gap_y: int
    scored: bool = False

    @property
    def top_rect(self) -> pygame.Rect:
        top_height = self.gap_y - PIPE_GAP // 2
        return pygame.Rect(int(self.x), 0, PIPE_WIDTH, top_height)

    @property
    def bottom_rect(self) -> pygame.Rect:
        gap_bottom = self.gap_y + PIPE_GAP // 2
        bottom_height = WINDOW_HEIGHT - gap_bottom
        return pygame.Rect(int(self.x), gap_bottom, PIPE_WIDTH, bottom_height)


class FlappyGame:
    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.state = "start"
        self.score = 0
        self.bird_y = WINDOW_HEIGHT // 2
        self.bird_velocity = 0.0
        self.pipes: list[PipePair] = []
        self.spawn_timer_ms = 0

    @property
    def game_over(self) -> bool:
        return self.state == "game_over"

    def flap(self) -> None:
        if self.state == "game_over":
            return
        if self.state == "start":
            self.state = "playing"
        self.bird_velocity = BIRD_JUMP_VELOCITY

    def update(self, delta_ms: int) -> None:
        if self.state != "playing":
            return

        delta_seconds = delta_ms / 1000.0
        self.bird_velocity += BIRD_GRAVITY * delta_seconds
        self.bird_y += self.bird_velocity * delta_seconds

        self.spawn_timer_ms += delta_ms
        while self.spawn_timer_ms >= PIPE_SPAWN_INTERVAL_MS:
            self.spawn_timer_ms -= PIPE_SPAWN_INTERVAL_MS
            self._spawn_pipe()

        for pipe in self.pipes:
            pipe.x -= PIPE_SPEED * delta_seconds

        self.pipes = [pipe for pipe in self.pipes if pipe.x + PIPE_WIDTH > 0]

        self._update_score()
        self._check_collisions()

    def _spawn_pipe(self) -> None:
        min_gap_y = PIPE_MARGIN + PIPE_GAP // 2
        max_gap_y = GROUND_TOP - PIPE_MARGIN - PIPE_GAP // 2
        gap_y = random.randint(min_gap_y, max_gap_y)
        self.pipes.append(PipePair(x=float(WINDOW_WIDTH), gap_y=gap_y))

    def _update_score(self) -> None:
        for pipe in self.pipes:
            if not pipe.scored and pipe.x + PIPE_WIDTH < BIRD_X:
                pipe.scored = True
                self.score += 1

    def _check_collisions(self) -> None:
        bird_rect = pygame.Rect(
            BIRD_X - BIRD_RADIUS,
            int(self.bird_y) - BIRD_RADIUS,
            BIRD_RADIUS * 2,
            BIRD_RADIUS * 2,
        )

        if bird_rect.top <= 0 or bird_rect.bottom >= GROUND_TOP:
            self.state = "game_over"
            return

        for pipe in self.pipes:
            if bird_rect.colliderect(pipe.top_rect) or bird_rect.colliderect(pipe.bottom_rect):
                self.state = "game_over"
                return
