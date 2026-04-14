"""Core game logic for the PyGame parking simulator."""

from __future__ import annotations

from dataclasses import dataclass
import math
import random

import pygame

from config import (
    BRAKE_DRAG,
    CAR_LENGTH,
    CAR_START_HEADING,
    CAR_START_X,
    CAR_START_Y,
    CAR_WIDTH,
    FORWARD_ACCELERATION,
    GARAGE_APPROACH_DEPTH,
    GARAGE_OUTER,
    GARAGE_WALL_THICKNESS,
    LEVEL_OBSTACLE_COUNT,
    MAX_FORWARD_SPEED,
    MAX_REVERSE_SPEED,
    MAX_STEERING_ANGLE,
    NATURAL_DRAG,
    OBSTACLE_MAX_SIZE,
    OBSTACLE_MIN_SIZE,
    OBSTACLES,
    PARKING_SPEED_THRESHOLD,
    PLAY_HEIGHT,
    PLAY_LEFT,
    PLAY_TOP,
    PLAY_WIDTH,
    REVERSE_ACCELERATION,
    STEERING_RESPONSE,
    STEERING_RETURN,
    WHEEL_BASE,
)


@dataclass
class CarState:
    """Mutable state of the player's car."""

    x: float = CAR_START_X
    y: float = CAR_START_Y
    heading: float = CAR_START_HEADING
    speed: float = 0.0
    steering_angle: float = 0.0


def _move_toward(current: float, target: float, delta: float) -> float:
    if current < target:
        return min(current + delta, target)
    return max(current - delta, target)


def _cross(v1: tuple[float, float], v2: tuple[float, float]) -> float:
    return v1[0] * v2[1] - v1[1] * v2[0]


def _point_in_polygon(point: tuple[float, float], polygon: list[tuple[float, float]]) -> bool:
    inside = False
    x, y = point
    for i, start in enumerate(polygon):
        end = polygon[(i + 1) % len(polygon)]
        x1, y1 = start
        x2, y2 = end
        intersects = ((y1 > y) != (y2 > y)) and (x < (x2 - x1) * (y - y1) / (y2 - y1 + 1e-9) + x1)
        if intersects:
            inside = not inside
    return inside


def _segments_intersect(
    a1: tuple[float, float],
    a2: tuple[float, float],
    b1: tuple[float, float],
    b2: tuple[float, float],
) -> bool:
    r = (a2[0] - a1[0], a2[1] - a1[1])
    s = (b2[0] - b1[0], b2[1] - b1[1])
    denominator = _cross(r, s)
    qp = (b1[0] - a1[0], b1[1] - a1[1])

    if abs(denominator) < 1e-9:
        return False

    t = _cross(qp, s) / denominator
    u = _cross(qp, r) / denominator
    return 0.0 <= t <= 1.0 and 0.0 <= u <= 1.0


def _polygon_intersects_rect(polygon: list[tuple[float, float]], rect: pygame.Rect) -> bool:
    rect_points = [
        (float(rect.left), float(rect.top)),
        (float(rect.right), float(rect.top)),
        (float(rect.right), float(rect.bottom)),
        (float(rect.left), float(rect.bottom)),
    ]

    if any(rect.collidepoint(point) for point in polygon):
        return True
    if any(_point_in_polygon(point, polygon) for point in rect_points):
        return True

    for i, poly_start in enumerate(polygon):
        poly_end = polygon[(i + 1) % len(polygon)]
        for j, rect_start in enumerate(rect_points):
            rect_end = rect_points[(j + 1) % len(rect_points)]
            if _segments_intersect(poly_start, poly_end, rect_start, rect_end):
                return True
    return False


class ParkingGame:
    """Stateful controller for parking gameplay rules and updates."""

    def __init__(self) -> None:
        self.play_area = pygame.Rect(PLAY_LEFT, PLAY_TOP, PLAY_WIDTH, PLAY_HEIGHT)
        self.garage_outer = pygame.Rect(*GARAGE_OUTER)
        self.garage_inner = pygame.Rect(0, 0, 0, 0)
        self.garage_approach = pygame.Rect(0, 0, 0, 0)
        self.garage_walls: list[pygame.Rect] = []
        self.obstacles = [pygame.Rect(*definition) for definition in OBSTACLES]

        self.car = CarState()
        self.game_over = False
        self.win = False
        self.level_index = 0
        self._apply_garage_geometry()
        self.generate_new_level()

    def reset(self, new_level: bool = False) -> None:
        if new_level:
            self.generate_new_level()
        self.car = CarState()
        self.game_over = False
        self.win = False

    def _apply_garage_geometry(self) -> None:
        wall = GARAGE_WALL_THICKNESS
        self.garage_inner = pygame.Rect(
            self.garage_outer.left + wall,
            self.garage_outer.top + wall,
            self.garage_outer.width - wall * 2,
            self.garage_outer.height - wall,
        )
        self.garage_walls = [
            pygame.Rect(self.garage_outer.left, self.garage_outer.top, wall, self.garage_outer.height),
            pygame.Rect(self.garage_outer.right - wall, self.garage_outer.top, wall, self.garage_outer.height),
            pygame.Rect(self.garage_outer.left + wall, self.garage_outer.top, self.garage_outer.width - wall * 2, wall),
        ]
        self.garage_approach = pygame.Rect(
            self.garage_inner.left,
            self.garage_outer.bottom,
            self.garage_inner.width,
            GARAGE_APPROACH_DEPTH,
        ).clip(self.play_area)

    def _garage_candidates(self) -> list[pygame.Rect]:
        width, height = GARAGE_OUTER[2], GARAGE_OUTER[3]
        candidates = []
        for x in (PLAY_LEFT + 520, PLAY_LEFT + 650, PLAY_LEFT + 760):
            for y in (PLAY_TOP + 120, PLAY_TOP + 260, PLAY_TOP + 380):
                rect = pygame.Rect(x, y, width, height)
                if self.play_area.contains(rect):
                    candidates.append(rect)
        random.shuffle(candidates)
        return candidates

    def _path_corridors(self, entrance_center: tuple[int, int]) -> list[pygame.Rect]:
        lane_width = int(CAR_WIDTH * 2.2)
        x0 = int(CAR_START_X)
        y0 = int(CAR_START_Y)
        x1, y1 = entrance_center

        horizontal = pygame.Rect(min(x0, x1), y0 - lane_width // 2, abs(x1 - x0), lane_width)
        vertical = pygame.Rect(x1 - lane_width // 2, min(y0, y1), lane_width, abs(y1 - y0))

        if horizontal.width <= 0:
            horizontal.width = lane_width
        if vertical.height <= 0:
            vertical.height = lane_width
        return [horizontal, vertical]

    def _generate_obstacles(self) -> list[pygame.Rect]:
        blockers: list[pygame.Rect] = []
        start_safe = pygame.Rect(int(CAR_START_X - 90), int(CAR_START_Y - 90), 180, 180)
        entrance_center = (self.garage_inner.centerx, self.garage_outer.bottom + GARAGE_APPROACH_DEPTH // 2)
        route_corridors = self._path_corridors(entrance_center)
        forbidden = [start_safe, self.garage_outer.inflate(14, 14), self.garage_approach.inflate(12, 12)] + route_corridors

        tries = 0
        while len(blockers) < LEVEL_OBSTACLE_COUNT and tries < 800:
            tries += 1
            width = random.randint(OBSTACLE_MIN_SIZE, OBSTACLE_MAX_SIZE)
            height = random.randint(OBSTACLE_MIN_SIZE, OBSTACLE_MAX_SIZE)
            x = random.randint(self.play_area.left + 10, self.play_area.right - width - 10)
            y = random.randint(self.play_area.top + 10, self.play_area.bottom - height - 10)
            candidate = pygame.Rect(x, y, width, height)

            if any(candidate.colliderect(area) for area in forbidden):
                continue
            if any(candidate.colliderect(existing.inflate(12, 12)) for existing in blockers):
                continue
            blockers.append(candidate)
        return blockers

    def generate_new_level(self) -> None:
        for _ in range(80):
            for garage in self._garage_candidates():
                self.garage_outer = garage
                self._apply_garage_geometry()
                # Перед воротами гаража должен быть свободный прямоугольник подхода.
                if self.garage_approach.height < GARAGE_APPROACH_DEPTH * 0.75:
                    continue

                obstacles = self._generate_obstacles()
                if len(obstacles) < LEVEL_OBSTACLE_COUNT:
                    continue

                self.obstacles = obstacles
                self.level_index += 1
                return

        self.garage_outer = pygame.Rect(*GARAGE_OUTER)
        self._apply_garage_geometry()
        self.obstacles = [pygame.Rect(*definition) for definition in OBSTACLES]
        self.level_index += 1

    def get_car_polygon(self) -> list[tuple[float, float]]:
        half_length = CAR_LENGTH / 2.0
        half_width = CAR_WIDTH / 2.0
        local_points = [
            (-half_length, -half_width),
            (half_length, -half_width),
            (half_length, half_width),
            (-half_length, half_width),
        ]

        cos_h = math.cos(self.car.heading)
        sin_h = math.sin(self.car.heading)
        points = []
        for local_x, local_y in local_points:
            world_x = self.car.x + local_x * cos_h - local_y * sin_h
            world_y = self.car.y + local_x * sin_h + local_y * cos_h
            points.append((world_x, world_y))
        return points

    def update(self, delta_ms: int, steer_input: int, accel_input: int) -> None:
        if self.game_over or self.win:
            return

        dt = delta_ms / 1000.0
        if dt <= 0:
            return

        target_steer = steer_input * MAX_STEERING_ANGLE
        steer_change_speed = STEERING_RESPONSE if steer_input != 0 else STEERING_RETURN
        self.car.steering_angle = _move_toward(
            self.car.steering_angle,
            target_steer,
            steer_change_speed * dt,
        )

        if accel_input > 0:
            self.car.speed += FORWARD_ACCELERATION * dt
        elif accel_input < 0:
            self.car.speed -= REVERSE_ACCELERATION * dt
        else:
            self.car.speed = _move_toward(self.car.speed, 0.0, NATURAL_DRAG * dt)

        if accel_input != 0 and self.car.speed * accel_input < 0:
            self.car.speed = _move_toward(self.car.speed, 0.0, BRAKE_DRAG * dt)

        self.car.speed = max(MAX_REVERSE_SPEED, min(MAX_FORWARD_SPEED, self.car.speed))

        if abs(self.car.speed) > 1.0 and abs(self.car.steering_angle) > 1e-3:
            turn_rate = (self.car.speed / WHEEL_BASE) * math.tan(self.car.steering_angle)
            self.car.heading += turn_rate * dt

        self.car.x += math.cos(self.car.heading) * self.car.speed * dt
        self.car.y += math.sin(self.car.heading) * self.car.speed * dt

        car_polygon = self.get_car_polygon()
        if self._is_collision(car_polygon):
            self.game_over = True
            self.car.speed = 0.0
            return

        parked = self._is_properly_parked(car_polygon)
        if parked:
            self.win = True
            self.car.speed = 0.0

    def _is_collision(self, car_polygon: list[tuple[float, float]]) -> bool:
        if any(not self.play_area.collidepoint(point) for point in car_polygon):
            return True

        barriers = self.obstacles + self.garage_walls
        return any(_polygon_intersects_rect(car_polygon, barrier) for barrier in barriers)

    def _is_properly_parked(self, car_polygon: list[tuple[float, float]]) -> bool:
        safe_zone = self.garage_inner.inflate(-8, -8)
        if safe_zone.width <= 0 or safe_zone.height <= 0:
            return False

        all_inside = all(safe_zone.collidepoint(point) for point in car_polygon)
        return all_inside and abs(self.car.speed) <= PARKING_SPEED_THRESHOLD
