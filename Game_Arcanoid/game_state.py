from __future__ import annotations

import pygame

from entities import Ball, Brick, Paddle
from levels import LEVEL_LAYOUTS
import settings


class GameState:
    def __init__(self) -> None:
        self.state = "start"
        self.level_index = 0
        self.score = 0
        self.lives = settings.START_LIVES
        self.hit_counter = 0

        self.paddle = Paddle()
        self.ball = Ball()
        self.bricks: list[Brick] = []
        self._load_level(self.level_index)

    def restart_full_game(self) -> None:
        self.state = "start"
        self.level_index = 0
        self.score = 0
        self.lives = settings.START_LIVES
        self.hit_counter = 0
        self.paddle.reset()
        self.ball.reset()
        self._load_level(self.level_index)

    def start_play(self) -> None:
        if self.state in {"start", "game_over", "win"}:
            if self.state != "start":
                self.restart_full_game()
            self.state = "play"

    def update(self, move_left: bool, move_right: bool) -> None:
        if self.state != "play":
            return

        self.paddle.update(move_left, move_right)
        self.ball.update()
        self.ball.bounce_from_walls()
        self.ball.bounce_from_paddle(self.paddle)
        self._process_brick_collisions()

        if self.ball.y - self.ball.radius > settings.HEIGHT:
            self.lives -= 1
            if self.lives <= 0:
                self.state = "game_over"
            else:
                self.paddle.reset()
                self.ball.reset()

        if self._all_bricks_cleared():
            self.level_index += 1
            if self.level_index >= len(LEVEL_LAYOUTS):
                self.state = "win"
            else:
                self._load_level(self.level_index)
                self.paddle.reset()
                self.ball.reset()

    def _all_bricks_cleared(self) -> bool:
        return not any(brick.alive for brick in self.bricks)

    def _load_level(self, level_idx: int) -> None:
        layout = LEVEL_LAYOUTS[level_idx]
        self.bricks.clear()
        for row_idx, row in enumerate(layout):
            for col_idx, cell in enumerate(row):
                if cell == "0":
                    continue
                hp = int(cell)
                x = settings.BRICK_SIDE_MARGIN + col_idx * (settings.BRICK_WIDTH + settings.BRICK_GAP_X)
                y = settings.BRICK_TOP_MARGIN + row_idx * (settings.BRICK_HEIGHT + settings.BRICK_GAP_Y)
                color = settings.BRICK_COLORS[row_idx % len(settings.BRICK_COLORS)]
                self.bricks.append(Brick(x, y, hp, color))

    def _process_brick_collisions(self) -> None:
        ball_rect = self.ball.rect
        for brick in self.bricks:
            if not brick.alive:
                continue
            if not ball_rect.colliderect(brick.rect):
                continue

            overlap_left = ball_rect.right - brick.rect.left
            overlap_right = brick.rect.right - ball_rect.left
            overlap_top = ball_rect.bottom - brick.rect.top
            overlap_bottom = brick.rect.bottom - ball_rect.top
            min_overlap_x = min(overlap_left, overlap_right)
            min_overlap_y = min(overlap_top, overlap_bottom)

            if min_overlap_x < min_overlap_y:
                self.ball.vx *= -1
            else:
                self.ball.vy *= -1

            destroyed = brick.hit()
            self.score += 100 if destroyed else 40
            self.hit_counter += 1
            if self.hit_counter % settings.BALL_HIT_SPEEDUP_EVERY == 0:
                self.ball.increase_speed(settings.BALL_SPEEDUP_FACTOR)
            break

    def draw(self, surface: pygame.Surface, font: pygame.font.Font, title_font: pygame.font.Font) -> None:
        surface.fill(settings.BACKGROUND_COLOR)

        if self.state == "start":
            self._draw_center_text(surface, title_font, "ARCANOID", -70, settings.ACCENT_COLOR)
            self._draw_center_text(surface, font, "SPACE - начать игру", 0, settings.TEXT_COLOR)
            self._draw_center_text(surface, font, "A/D или стрелки - движение платформы", 40, settings.TEXT_COLOR)
            self._draw_center_text(surface, font, "R - перезапуск после окончания", 80, settings.TEXT_COLOR)
            return

        for brick in self.bricks:
            brick.draw(surface)
        self.paddle.draw(surface)
        self.ball.draw(surface)

        hud = f"Счет: {self.score}   Жизни: {self.lives}   Уровень: {self.level_index + 1}/{len(LEVEL_LAYOUTS)}"
        hud_surface = font.render(hud, True, settings.TEXT_COLOR)
        surface.blit(hud_surface, (20, 20))

        if self.state == "game_over":
            self._draw_center_text(surface, title_font, "ПОРАЖЕНИЕ", -30, (255, 120, 120))
            self._draw_center_text(surface, font, "Нажмите R для новой игры", 30, settings.TEXT_COLOR)
        elif self.state == "win":
            self._draw_center_text(surface, title_font, "ПОБЕДА", -30, (130, 235, 155))
            self._draw_center_text(surface, font, "Нажмите R для новой игры", 30, settings.TEXT_COLOR)

    @staticmethod
    def _draw_center_text(
        surface: pygame.Surface,
        font: pygame.font.Font,
        text: str,
        y_offset: int,
        color: tuple[int, int, int],
    ) -> None:
        rendered = font.render(text, True, color)
        rect = rendered.get_rect(center=(settings.WIDTH // 2, settings.HEIGHT // 2 + y_offset))
        surface.blit(rendered, rect)
