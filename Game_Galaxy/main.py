"""Entry point for the simple Galaxians-like PyGame shooter."""

from __future__ import annotations

import random

import pygame

from config import (
    BACKGROUND_COLOR,
    ENEMY_BULLET_COLOR,
    ENEMY_COLOR,
    FPS,
    PLAYER_BULLET_COLOR,
    PLAYER_COLOR,
    STAR_COLOR,
    TEXT_COLOR,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from galaxy import GalaxyGame


def draw_player_ship(surface: pygame.Surface, x: float, y: float, color: tuple[int, int, int]) -> None:
    body = pygame.Rect(int(x), int(y), 42, 20)
    cockpit = pygame.Rect(int(x + 14), int(y - 10), 14, 12)
    pygame.draw.rect(surface, color, body)
    pygame.draw.rect(surface, color, cockpit)
    pygame.draw.polygon(
        surface,
        color,
        [(int(x), int(y + 20)), (int(x + 10), int(y + 6)), (int(x + 18), int(y + 20))],
    )
    pygame.draw.polygon(
        surface,
        color,
        [(int(x + 42), int(y + 20)), (int(x + 32), int(y + 6)), (int(x + 24), int(y + 20))],
    )


def draw_enemy_ship(surface: pygame.Surface, x: float, y: float, color: tuple[int, int, int]) -> None:
    base = pygame.Rect(int(x), int(y + 8), 30, 12)
    core = pygame.Rect(int(x + 8), int(y), 14, 10)
    pygame.draw.rect(surface, color, base)
    pygame.draw.rect(surface, color, core)
    pygame.draw.polygon(
        surface,
        color,
        [(int(x), int(y + 20)), (int(x + 6), int(y + 8)), (int(x + 12), int(y + 20))],
    )
    pygame.draw.polygon(
        surface,
        color,
        [(int(x + 30), int(y + 20)), (int(x + 24), int(y + 8)), (int(x + 18), int(y + 20))],
    )


def draw_game(
    screen: pygame.Surface,
    game: GalaxyGame,
    font: pygame.font.Font,
    title_font: pygame.font.Font,
    stars: list[tuple[int, int, int]],
) -> None:
    screen.fill(BACKGROUND_COLOR)

    for star_x, star_y, radius in stars:
        pygame.draw.circle(screen, STAR_COLOR, (star_x, star_y), radius)

    draw_player_ship(screen, game.player_x, game.player_y, PLAYER_COLOR)

    for enemy in game.enemies:
        if enemy.alive:
            draw_enemy_ship(screen, enemy.x, enemy.y, ENEMY_COLOR)

    for bullet in game.player_bullets:
        pygame.draw.rect(
            screen,
            PLAYER_BULLET_COLOR,
            pygame.Rect(int(bullet.x), int(bullet.y), game.bullet_width, game.bullet_height),
        )

    for bullet in game.enemy_bullets:
        pygame.draw.rect(
            screen,
            ENEMY_BULLET_COLOR,
            pygame.Rect(int(bullet.x), int(bullet.y), game.bullet_width, game.bullet_height),
        )

    score_text = font.render(f"Score: {game.score}", True, TEXT_COLOR)
    wave_text = font.render(f"Wave: {game.wave}", True, TEXT_COLOR)
    controls_text = font.render("Left/Right: Move | Space: Shoot", True, TEXT_COLOR)
    screen.blit(score_text, (16, 12))
    screen.blit(wave_text, (16, 42))
    screen.blit(controls_text, (16, WINDOW_HEIGHT - 34))

    if game.game_over:
        result_text = "YOU WIN" if game.win else "GAME OVER"
        result_color = (120, 255, 150) if game.win else (255, 100, 100)
        line1 = title_font.render(result_text, True, result_color)
        line2 = font.render("Press R to restart", True, TEXT_COLOR)
        screen.blit(line1, (WINDOW_WIDTH // 2 - line1.get_width() // 2, WINDOW_HEIGHT // 2 - 32))
        screen.blit(line2, (WINDOW_WIDTH // 2 - line2.get_width() // 2, WINDOW_HEIGHT // 2 + 16))

    pygame.display.flip()


def run() -> None:
    pygame.init()
    pygame.display.set_caption("Galaxy Assault")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)
    title_font = pygame.font.SysFont("Arial", 42, bold=True)
    stars = [(random.randint(0, WINDOW_WIDTH), random.randint(0, WINDOW_HEIGHT), random.randint(1, 2)) for _ in range(90)]

    game = GalaxyGame()
    running = True

    while running:
        delta_ms = clock.tick(FPS)
        keys = pygame.key.get_pressed()
        move_dir = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        if move_dir != 0:
            game.move_player(move_dir, delta_ms)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game.player_shoot()
                elif event.key == pygame.K_r and game.game_over:
                    game.reset()

        game.update(delta_ms)
        draw_game(screen, game, font, title_font, stars)

    pygame.quit()


if __name__ == "__main__":
    run()
