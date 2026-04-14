"""Entry point for the simple keyboard-controlled PyGame Snake."""

from __future__ import annotations

import pygame

from config import (
    BACKGROUND_COLOR,
    CELL_SIZE,
    FOOD_COLOR,
    FPS,
    GAME_OVER_COLOR,
    GRID_COLOR,
    GRID_HEIGHT,
    GRID_WIDTH,
    MOVE_INTERVAL_MS,
    SNAKE_BODY_COLOR,
    SNAKE_HEAD_COLOR,
    TEXT_COLOR,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from snake import SnakeGame


def draw_game(
    screen: pygame.Surface,
    game: SnakeGame,
    font: pygame.font.Font,
    title_font: pygame.font.Font,
) -> None:
    screen.fill(BACKGROUND_COLOR)

    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            pygame.draw.rect(screen, GRID_COLOR, rect, 1)

    for index, (x, y) in enumerate(game.snake):
        rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
        color = SNAKE_HEAD_COLOR if index == 0 else SNAKE_BODY_COLOR
        pygame.draw.rect(screen, color, rect)

    food_x, food_y = game.food
    food_rect = pygame.Rect(food_x * CELL_SIZE, food_y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
    pygame.draw.rect(screen, FOOD_COLOR, food_rect)

    score_text = font.render(f"Score: {game.score}", True, TEXT_COLOR)
    screen.blit(score_text, (10, 10))

    controls_text = font.render("Arrows: move", True, TEXT_COLOR)
    screen.blit(controls_text, (10, 40))

    if game.game_over:
        game_over_text = title_font.render("GAME OVER", True, GAME_OVER_COLOR)
        restart_text = font.render("Press R to restart", True, TEXT_COLOR)
        screen.blit(
            game_over_text,
            (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2, WINDOW_HEIGHT // 2 - 40),
        )
        screen.blit(
            restart_text,
            (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, WINDOW_HEIGHT // 2 + 4),
        )

    pygame.display.flip()


def run() -> None:
    pygame.init()
    pygame.display.set_caption("Simple Snake")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)
    title_font = pygame.font.SysFont("Arial", 36, bold=True)

    game = SnakeGame()
    running = True
    move_timer_ms = 0

    while running:
        delta_ms = clock.tick(FPS)
        move_timer_ms += delta_ms

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    game.set_direction((-1, 0))
                elif event.key == pygame.K_RIGHT:
                    game.set_direction((1, 0))
                elif event.key == pygame.K_UP:
                    game.set_direction((0, -1))
                elif event.key == pygame.K_DOWN:
                    game.set_direction((0, 1))
                elif event.key == pygame.K_r and game.game_over:
                    game.reset()
                    move_timer_ms = 0

        while not game.game_over and move_timer_ms >= MOVE_INTERVAL_MS:
            game.update()
            move_timer_ms -= MOVE_INTERVAL_MS

        draw_game(screen, game, font, title_font)

    pygame.quit()


if __name__ == "__main__":
    run()
