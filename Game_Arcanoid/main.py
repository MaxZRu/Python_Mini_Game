import sys

import pygame

from game_state import GameState
import settings


def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((settings.WIDTH, settings.HEIGHT))
    pygame.display.set_caption(settings.WINDOW_TITLE)
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("arial", 28)
    title_font = pygame.font.SysFont("arial", 56, bold=True)

    game_state = GameState()
    running = True

    while running:
        dt = clock.tick(settings.FPS)
        _ = dt
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_state.start_play()
                elif event.key == pygame.K_r:
                    game_state.restart_full_game()

        keys = pygame.key.get_pressed()
        move_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
        move_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
        game_state.update(move_left, move_right)

        game_state.draw(screen, font, title_font)
        pygame.display.flip()

    pygame.quit()
    sys.exit(0)


if __name__ == "__main__":
    main()
