"""Entry point for the simple keyboard-controlled PyGame Tetris."""

from __future__ import annotations

import pygame

from config import (
    BACKGROUND_COLOR,
    BORDER_COLOR,
    CELL_SIZE,
    FALL_INTERVAL_MS,
    FPS,
    GRID_HEIGHT,
    GRID_LINE_COLOR,
    GRID_WIDTH,
    PIECE_COLORS,
    PLAY_HEIGHT,
    PLAY_WIDTH,
    SOFT_DROP_INTERVAL_MS,
    TEXT_COLOR,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from tetris import TetrisGame


def draw_game(screen: pygame.Surface, game: TetrisGame, font: pygame.font.Font, title_font: pygame.font.Font) -> None:
    screen.fill(BACKGROUND_COLOR)
    grid = game.get_render_grid()

    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            value = grid[y][x]
            color = PIECE_COLORS[value]
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, GRID_LINE_COLOR, rect, 1)

    pygame.draw.rect(screen, BORDER_COLOR, pygame.Rect(0, 0, PLAY_WIDTH, PLAY_HEIGHT), 2)

    score_text = font.render(f"Score: {game.score}", True, TEXT_COLOR)
    controls_text = [
        "Controls:",
        "Left/Right: move",
        "Up: rotate",
        "Down: soft drop",
    ]

    screen.blit(score_text, (PLAY_WIDTH + 20, 30))
    for index, line in enumerate(controls_text):
        control_surface = font.render(line, True, TEXT_COLOR)
        screen.blit(control_surface, (PLAY_WIDTH + 20, 90 + index * 28))

    if game.game_over:
        game_over_text = title_font.render("GAME OVER", True, (255, 80, 80))
        restart_text = font.render("Press R to restart", True, TEXT_COLOR)
        screen.blit(game_over_text, (PLAY_WIDTH + 18, 240))
        screen.blit(restart_text, (PLAY_WIDTH + 20, 285))

    pygame.display.flip()


def run() -> None:
    pygame.init()
    pygame.display.set_caption("Simple Tetris")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)
    title_font = pygame.font.SysFont("Arial", 28, bold=True)

    game = TetrisGame()
    running = True
    fall_timer_ms = 0
    soft_drop_active = False

    while running:
        delta_ms = clock.tick(FPS)
        fall_timer_ms += delta_ms
        fall_interval = SOFT_DROP_INTERVAL_MS if soft_drop_active else FALL_INTERVAL_MS

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    game.move_left()
                elif event.key == pygame.K_RIGHT:
                    game.move_right()
                elif event.key == pygame.K_UP:
                    game.rotate()
                elif event.key == pygame.K_DOWN:
                    soft_drop_active = True
                elif event.key == pygame.K_r and game.game_over:
                    game.reset()
                    fall_timer_ms = 0
                    soft_drop_active = False
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_DOWN:
                    soft_drop_active = False

        if not game.game_over and fall_timer_ms >= fall_interval:
            game.step_down()
            fall_timer_ms = 0

        draw_game(screen, game, font, title_font)

    pygame.quit()


if __name__ == "__main__":
    run()
