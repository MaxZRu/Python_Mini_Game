"""Entry point for the level-based Memory mini game."""

from __future__ import annotations

import pygame

from config import FPS, WINDOW_HEIGHT, WINDOW_WIDTH
from memory import MemoryGame


def run() -> None:
    pygame.init()
    pygame.display.set_caption("Memory Game")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()

    game = MemoryGame()
    running = True

    while running:
        clock.tick(FPS)
        now_ms = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                game.handle_click(event.pos, now_ms)

        game.update(now_ms)
        game.draw(screen)
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    run()
