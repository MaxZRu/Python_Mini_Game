"""Entry point for a primitive-only PyGame Flappy Bird clone."""

from __future__ import annotations

import pygame

from config import (
    BACKGROUND_COLOR,
    BIRD_COLOR,
    BIRD_RADIUS,
    BIRD_X,
    FPS,
    GAME_OVER_COLOR,
    GROUND_COLOR,
    GROUND_HEIGHT,
    GROUND_TOP,
    PIPE_COLOR,
    TEXT_COLOR,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from flappy import FlappyGame


def draw_game(
    screen: pygame.Surface,
    game: FlappyGame,
    font: pygame.font.Font,
    title_font: pygame.font.Font,
) -> None:
    screen.fill(BACKGROUND_COLOR)
    pygame.draw.rect(screen, GROUND_COLOR, pygame.Rect(0, GROUND_TOP, WINDOW_WIDTH, GROUND_HEIGHT))

    for pipe in game.pipes:
        pygame.draw.rect(screen, PIPE_COLOR, pipe.top_rect)
        pygame.draw.rect(screen, PIPE_COLOR, pipe.bottom_rect)

    pygame.draw.circle(screen, BIRD_COLOR, (BIRD_X, int(game.bird_y)), BIRD_RADIUS)

    score_text = title_font.render(str(game.score), True, TEXT_COLOR)
    screen.blit(score_text, (WINDOW_WIDTH // 2 - score_text.get_width() // 2, 20))

    if game.state == "start":
        text = font.render("Press SPACE to start", True, TEXT_COLOR)
        screen.blit(text, (WINDOW_WIDTH // 2 - text.get_width() // 2, WINDOW_HEIGHT // 2 - 10))
    elif game.state == "game_over":
        game_over_text = title_font.render("GAME OVER", True, GAME_OVER_COLOR)
        restart_text = font.render("Press R to restart", True, TEXT_COLOR)
        screen.blit(
            game_over_text,
            (WINDOW_WIDTH // 2 - game_over_text.get_width() // 2, WINDOW_HEIGHT // 2 - 45),
        )
        screen.blit(
            restart_text,
            (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, WINDOW_HEIGHT // 2 - 5),
        )

    pygame.display.flip()


def run() -> None:
    pygame.init()
    pygame.display.set_caption("Flappy Bird (No Assets)")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 30)
    title_font = pygame.font.SysFont("Arial", 40, bold=True)

    game = FlappyGame()
    running = True

    while running:
        delta_ms = clock.tick(FPS)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game.flap()
                elif event.key == pygame.K_r and game.game_over:
                    game.reset()

        game.update(delta_ms)
        draw_game(screen, game, font, title_font)

    pygame.quit()


if __name__ == "__main__":
    run()
