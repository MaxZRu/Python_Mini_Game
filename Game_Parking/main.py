"""Entry point for the top-down PyGame parking simulator."""

from __future__ import annotations

import math

import pygame

from config import (
    BACKGROUND_COLOR,
    BORDER_COLOR,
    CAR_BODY_COLOR,
    CAR_FRONT_COLOR,
    CAR_ROOF_COLOR,
    FPS,
    GARAGE_WALL_COLOR,
    GARAGE_ZONE_COLOR,
    PLAY_AREA_COLOR,
    STATUS_ACTIVE_COLOR,
    STATUS_LOSE_COLOR,
    STATUS_WIN_COLOR,
    TEXT_COLOR,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from parking import ParkingGame


def draw_car(surface: pygame.Surface, game: ParkingGame) -> None:
    car_polygon = game.get_car_polygon()
    int_polygon = [(int(x), int(y)) for x, y in car_polygon]
    pygame.draw.polygon(surface, CAR_BODY_COLOR, int_polygon)

    heading_x = math.cos(game.car.heading)
    heading_y = math.sin(game.car.heading)
    front_center = (
        game.car.x + heading_x * 21.0,
        game.car.y + heading_y * 21.0,
    )
    nose_left = (
        front_center[0] - heading_y * 9.0,
        front_center[1] + heading_x * 9.0,
    )
    nose_right = (
        front_center[0] + heading_y * 9.0,
        front_center[1] - heading_x * 9.0,
    )
    nose_tip = (
        front_center[0] + heading_x * 13.0,
        front_center[1] + heading_y * 13.0,
    )
    pygame.draw.polygon(
        surface,
        CAR_FRONT_COLOR,
        [(int(nose_left[0]), int(nose_left[1])), (int(nose_tip[0]), int(nose_tip[1])), (int(nose_right[0]), int(nose_right[1]))],
    )

    roof_rect = pygame.Rect(0, 0, 26, 16)
    roof_surface = pygame.Surface(roof_rect.size, pygame.SRCALPHA)
    roof_surface.fill((*CAR_ROOF_COLOR, 220))
    rotated = pygame.transform.rotate(roof_surface, -math.degrees(game.car.heading))
    roof_pos = (int(game.car.x - rotated.get_width() / 2), int(game.car.y - rotated.get_height() / 2))
    surface.blit(rotated, roof_pos)

    def draw_wheel(offset_x: float, offset_y: float, wheel_heading: float) -> None:
        base_x = game.car.x + offset_x * heading_x - offset_y * heading_y
        base_y = game.car.y + offset_x * heading_y + offset_y * heading_x
        wheel_surface = pygame.Surface((14, 7), pygame.SRCALPHA)
        wheel_surface.fill((22, 22, 22, 230))
        wheel_rotated = pygame.transform.rotate(wheel_surface, -math.degrees(wheel_heading))
        wheel_pos = (int(base_x - wheel_rotated.get_width() / 2), int(base_y - wheel_rotated.get_height() / 2))
        surface.blit(wheel_rotated, wheel_pos)

    front_wheel_heading = game.car.heading + game.car.steering_angle
    draw_wheel(16.0, -12.0, front_wheel_heading)
    draw_wheel(16.0, 12.0, front_wheel_heading)
    draw_wheel(-16.0, -12.0, game.car.heading)
    draw_wheel(-16.0, 12.0, game.car.heading)


def draw_game(screen: pygame.Surface, game: ParkingGame, font: pygame.font.Font, title_font: pygame.font.Font) -> None:
    screen.fill(BACKGROUND_COLOR)
    pygame.draw.rect(screen, PLAY_AREA_COLOR, game.play_area)
    pygame.draw.rect(screen, BORDER_COLOR, game.play_area, 3)

    pygame.draw.rect(screen, GARAGE_ZONE_COLOR, game.garage_inner)
    pygame.draw.rect(screen, (100, 180, 110), game.garage_approach, 2)
    for wall in game.garage_walls:
        pygame.draw.rect(screen, GARAGE_WALL_COLOR, wall)

    for obstacle in game.obstacles:
        pygame.draw.rect(screen, (25, 25, 25), obstacle.inflate(6, 6), border_radius=6)
        pygame.draw.rect(screen, (165, 92, 75), obstacle, border_radius=4)

    draw_car(screen, game)

    status_text = "Паркуйтесь в гараж (П), не касаясь стен и препятствий."
    status_color = STATUS_ACTIVE_COLOR
    if game.win:
        status_text = "Победа! Автомобиль припаркован."
        status_color = STATUS_WIN_COLOR
    elif game.game_over:
        status_text = "Столкновение! Попробуйте снова."
        status_color = STATUS_LOSE_COLOR

    title = title_font.render("Parking Simulator", True, TEXT_COLOR)
    controls = font.render("Стрелки: газ/задний ход/руль | N: новый уровень", True, TEXT_COLOR)
    status = font.render(status_text, True, status_color)
    speed_kmh = abs(game.car.speed) * 0.26
    speed_text = font.render(f"Скорость: {speed_kmh:05.1f}", True, TEXT_COLOR)
    level_text = font.render(f"Уровень: {game.level_index}", True, TEXT_COLOR)

    screen.blit(title, (48, 8))
    screen.blit(controls, (48, 42))
    screen.blit(status, (48, WINDOW_HEIGHT - 34))
    screen.blit(speed_text, (WINDOW_WIDTH - 220, 14))
    screen.blit(level_text, (WINDOW_WIDTH - 220, 42))

    if game.win or game.game_over:
        restart_text = title_font.render("Нажмите R для рестарта", True, TEXT_COLOR)
        screen.blit(restart_text, (WINDOW_WIDTH // 2 - restart_text.get_width() // 2, WINDOW_HEIGHT // 2 - 25))

    pygame.display.flip()


def run() -> None:
    pygame.init()
    pygame.display.set_caption("Parking Simulator")
    screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    clock = pygame.time.Clock()
    font = pygame.font.SysFont("Arial", 24)
    title_font = pygame.font.SysFont("Arial", 34, bold=True)

    game = ParkingGame()
    running = True

    while running:
        delta_ms = clock.tick(FPS)
        keys = pygame.key.get_pressed()
        steer_input = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        accel_input = int(keys[pygame.K_UP]) - int(keys[pygame.K_DOWN])

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                if game.win or game.game_over:
                    game.reset()
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_n:
                game.reset(new_level=True)

        game.update(delta_ms, steer_input, accel_input)
        draw_game(screen, game, font, title_font)

    pygame.quit()


if __name__ == "__main__":
    run()
