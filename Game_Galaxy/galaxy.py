"""Core game logic for a simple Galaxians-like PyGame shooter."""

from __future__ import annotations

import random
from dataclasses import dataclass

from config import (
    ENEMY_DROP_DISTANCE,
    ENEMY_FIRE_CHANCE_PER_SEC,
    ENEMY_HORIZONTAL_SPEED,
    ENEMY_BULLET_SPEED,
    MAX_ENEMY_BULLETS,
    MAX_PLAYER_BULLETS,
    PLAYER_BULLET_SPEED,
    PLAYER_COOLDOWN_MS,
    PLAYER_SPEED,
    WAVE_ENEMY_COLUMNS,
    WAVE_ENEMY_ROWS,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)


@dataclass
class Bullet:
    x: float
    y: float
    vy: float
    from_enemy: bool


@dataclass
class Enemy:
    x: float
    y: float
    alive: bool = True


class GalaxyGame:
    def __init__(self) -> None:
        self.score = 0
        self.wave = 1
        self.game_over = False
        self.win = False

        self.player_width = 42
        self.player_height = 20
        self.enemy_width = 30
        self.enemy_height = 20
        self.bullet_width = 4
        self.bullet_height = 12

        self.player_x = WINDOW_WIDTH / 2 - self.player_width / 2
        self.player_y = WINDOW_HEIGHT - 70
        self.player_shot_cooldown_ms = 0

        self.enemy_direction = 1
        self.enemies: list[Enemy] = []
        self.player_bullets: list[Bullet] = []
        self.enemy_bullets: list[Bullet] = []
        self._build_wave()

    def _build_wave(self) -> None:
        self.enemies.clear()
        start_x = 120
        start_y = 90
        spacing_x = 72
        spacing_y = 52

        for row in range(WAVE_ENEMY_ROWS):
            for col in range(WAVE_ENEMY_COLUMNS):
                enemy_x = start_x + col * spacing_x
                enemy_y = start_y + row * spacing_y
                self.enemies.append(Enemy(enemy_x, enemy_y))

        self.enemy_direction = 1
        self.player_bullets.clear()
        self.enemy_bullets.clear()

    def move_player(self, direction: int, delta_ms: int) -> None:
        if self.game_over:
            return
        delta_x = direction * PLAYER_SPEED * (delta_ms / 1000)
        self.player_x += delta_x
        self.player_x = max(12, min(WINDOW_WIDTH - self.player_width - 12, self.player_x))

    def player_shoot(self) -> None:
        if self.game_over:
            return
        if self.player_shot_cooldown_ms > 0 or len(self.player_bullets) >= MAX_PLAYER_BULLETS:
            return
        bullet_x = self.player_x + self.player_width / 2 - self.bullet_width / 2
        bullet_y = self.player_y - self.bullet_height
        self.player_bullets.append(Bullet(bullet_x, bullet_y, -PLAYER_BULLET_SPEED, from_enemy=False))
        self.player_shot_cooldown_ms = PLAYER_COOLDOWN_MS

    def update(self, delta_ms: int) -> None:
        if self.game_over:
            return

        if self.player_shot_cooldown_ms > 0:
            self.player_shot_cooldown_ms = max(0, self.player_shot_cooldown_ms - delta_ms)

        self._update_enemy_formation(delta_ms)
        self._update_bullets(delta_ms)
        self._enemy_random_shot(delta_ms)
        self._check_collisions()
        self._check_wave_clear()
        self._check_loss()

    def _update_enemy_formation(self, delta_ms: int) -> None:
        alive_enemies = [enemy for enemy in self.enemies if enemy.alive]
        if not alive_enemies:
            return

        shift_x = self.enemy_direction * ENEMY_HORIZONTAL_SPEED * (delta_ms / 1000)
        min_x = min(enemy.x for enemy in alive_enemies)
        max_x = max(enemy.x + self.enemy_width for enemy in alive_enemies)

        hit_left_wall = min_x + shift_x <= 10
        hit_right_wall = max_x + shift_x >= WINDOW_WIDTH - 10

        if hit_left_wall or hit_right_wall:
            self.enemy_direction *= -1
            for enemy in alive_enemies:
                enemy.y += ENEMY_DROP_DISTANCE
        else:
            for enemy in alive_enemies:
                enemy.x += shift_x

    def _update_bullets(self, delta_ms: int) -> None:
        dt = delta_ms / 1000
        for bullet in self.player_bullets:
            bullet.y += bullet.vy * dt
        for bullet in self.enemy_bullets:
            bullet.y += bullet.vy * dt

        self.player_bullets = [
            bullet for bullet in self.player_bullets if bullet.y + self.bullet_height > 0
        ]
        self.enemy_bullets = [
            bullet for bullet in self.enemy_bullets if bullet.y < WINDOW_HEIGHT
        ]

    def _enemy_random_shot(self, delta_ms: int) -> None:
        if len(self.enemy_bullets) >= MAX_ENEMY_BULLETS:
            return

        alive_enemies = [enemy for enemy in self.enemies if enemy.alive]
        if not alive_enemies:
            return

        chance = ENEMY_FIRE_CHANCE_PER_SEC * (delta_ms / 1000)
        if random.random() > chance:
            return

        shooter = random.choice(alive_enemies)
        bullet_x = shooter.x + self.enemy_width / 2 - self.bullet_width / 2
        bullet_y = shooter.y + self.enemy_height
        self.enemy_bullets.append(Bullet(bullet_x, bullet_y, ENEMY_BULLET_SPEED, from_enemy=True))

    def _check_collisions(self) -> None:
        enemies_alive = [enemy for enemy in self.enemies if enemy.alive]
        remaining_player_bullets: list[Bullet] = []

        for bullet in self.player_bullets:
            hit = False
            for enemy in enemies_alive:
                if self._rects_overlap(
                    bullet.x,
                    bullet.y,
                    self.bullet_width,
                    self.bullet_height,
                    enemy.x,
                    enemy.y,
                    self.enemy_width,
                    self.enemy_height,
                ):
                    enemy.alive = False
                    self.score += 10
                    hit = True
                    break
            if not hit:
                remaining_player_bullets.append(bullet)
        self.player_bullets = remaining_player_bullets

        remaining_enemy_bullets: list[Bullet] = []
        for bullet in self.enemy_bullets:
            if self._rects_overlap(
                bullet.x,
                bullet.y,
                self.bullet_width,
                self.bullet_height,
                self.player_x,
                self.player_y,
                self.player_width,
                self.player_height,
            ):
                self.game_over = True
                self.win = False
            else:
                remaining_enemy_bullets.append(bullet)
        self.enemy_bullets = remaining_enemy_bullets

    def _check_wave_clear(self) -> None:
        if any(enemy.alive for enemy in self.enemies):
            return
        self.wave += 1
        if self.wave > 3:
            self.game_over = True
            self.win = True
            return
        self._build_wave()
        for enemy in self.enemies:
            enemy.y += (self.wave - 1) * 10

    def _check_loss(self) -> None:
        if self.game_over:
            return
        for enemy in self.enemies:
            if enemy.alive and enemy.y + self.enemy_height >= self.player_y:
                self.game_over = True
                self.win = False
                return

    @staticmethod
    def _rects_overlap(
        x1: float,
        y1: float,
        w1: float,
        h1: float,
        x2: float,
        y2: float,
        w2: float,
        h2: float,
    ) -> bool:
        return not (x1 + w1 < x2 or x1 > x2 + w2 or y1 + h1 < y2 or y1 > y2 + h2)

    def reset(self) -> None:
        self.score = 0
        self.wave = 1
        self.game_over = False
        self.win = False
        self.player_x = WINDOW_WIDTH / 2 - self.player_width / 2
        self.player_shot_cooldown_ms = 0
        self.player_bullets.clear()
        self.enemy_bullets.clear()
        self._build_wave()
