import math
import random

import pygame

import settings


class Paddle:
    def __init__(self) -> None:
        self.rect = pygame.Rect(0, 0, settings.PADDLE_WIDTH, settings.PADDLE_HEIGHT)
        self.reset()

    def reset(self) -> None:
        self.rect.centerx = settings.WIDTH // 2
        self.rect.y = settings.HEIGHT - settings.PADDLE_Y_OFFSET

    def update(self, move_left: bool, move_right: bool) -> None:
        if move_left and not move_right:
            self.rect.x -= settings.PADDLE_SPEED
        elif move_right and not move_left:
            self.rect.x += settings.PADDLE_SPEED
        self.rect.x = max(0, min(self.rect.x, settings.WIDTH - self.rect.width))

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.rect(surface, settings.PADDLE_COLOR, self.rect, border_radius=8)


class Ball:
    def __init__(self) -> None:
        self.radius = settings.BALL_RADIUS
        self.x = settings.WIDTH // 2
        self.y = settings.HEIGHT // 2
        self.vx = 0.0
        self.vy = 0.0
        self.reset()

    @property
    def rect(self) -> pygame.Rect:
        return pygame.Rect(
            int(self.x - self.radius),
            int(self.y - self.radius),
            self.radius * 2,
            self.radius * 2,
        )

    @property
    def speed(self) -> float:
        return math.hypot(self.vx, self.vy)

    def reset(self) -> None:
        self.x = settings.WIDTH // 2
        self.y = settings.HEIGHT // 2 + 80
        angle = random.uniform(-0.8, 0.8)
        self.vx = settings.BALL_START_SPEED * math.sin(angle)
        self.vy = -settings.BALL_START_SPEED * math.cos(angle)

    def update(self) -> None:
        self.x += self.vx
        self.y += self.vy

    def increase_speed(self, factor: float) -> None:
        speed = min(self.speed * factor, settings.BALL_MAX_SPEED)
        angle = math.atan2(self.vy, self.vx)
        self.vx = speed * math.cos(angle)
        self.vy = speed * math.sin(angle)

    def bounce_from_walls(self) -> None:
        if self.x - self.radius <= 0:
            self.x = self.radius
            self.vx *= -1
        elif self.x + self.radius >= settings.WIDTH:
            self.x = settings.WIDTH - self.radius
            self.vx *= -1

        if self.y - self.radius <= 0:
            self.y = self.radius
            self.vy *= -1

    def bounce_from_paddle(self, paddle: Paddle) -> bool:
        if self.rect.colliderect(paddle.rect) and self.vy > 0:
            relative = (self.x - paddle.rect.centerx) / (paddle.rect.width / 2)
            relative = max(-1.0, min(1.0, relative))
            self.y = paddle.rect.top - self.radius - 1
            speed = max(self.speed, settings.BALL_START_SPEED)
            self.vx = speed * relative
            self.vy = -abs(speed * math.sqrt(max(0.2, 1 - relative * relative)))
            return True
        return False

    def draw(self, surface: pygame.Surface) -> None:
        pygame.draw.circle(surface, settings.BALL_COLOR, (int(self.x), int(self.y)), self.radius)


class Brick:
    def __init__(self, x: int, y: int, hp: int, color: tuple[int, int, int]) -> None:
        self.rect = pygame.Rect(x, y, settings.BRICK_WIDTH, settings.BRICK_HEIGHT)
        self.hp = hp
        self.color = color

    @property
    def alive(self) -> bool:
        return self.hp > 0

    def hit(self) -> bool:
        self.hp -= 1
        return self.hp <= 0

    def draw(self, surface: pygame.Surface) -> None:
        if not self.alive:
            return
        pygame.draw.rect(surface, self.color, self.rect, border_radius=6)
        pygame.draw.rect(surface, (30, 35, 65), self.rect, width=2, border_radius=6)
