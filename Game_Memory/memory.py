"""Core game state and rendering logic for Memory mini game."""

from __future__ import annotations

from dataclasses import dataclass
import random

import pygame

from config import (
    ACCENT_COLOR,
    BACKGROUND_COLOR,
    CARD_BACK_COLOR,
    CARD_BORDER_COLOR,
    CARD_BORDER_RADIUS,
    CARD_FACE_COLOR,
    CARD_GAP,
    CARD_MATCHED_COLOR,
    CARD_SIZE,
    LEVEL_ADVANCE_DELAY_MS,
    MATCH_CHECK_DELAY_MS,
    PANEL_COLOR,
    SHAPE_COLORS,
    TEXT_COLOR,
    TOP_PANEL_HEIGHT,
    WINDOW_HEIGHT,
    WINDOW_WIDTH,
)
from levels import build_center_square_positions, get_level_card_count

PATTERN_POOL = [
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "11",
    "12",
    "shape:red:circle",
    "shape:blue:square",
    "shape:green:triangle",
    "shape:orange:diamond",
    "shape:purple:circle",
    "shape:red:triangle",
    "shape:blue:diamond",
    "shape:green:square",
]


@dataclass
class Card:
    """Single card in the memory board."""

    card_id: int
    pattern: str
    rect: pygame.Rect
    is_open: bool = False
    is_matched: bool = False


class MemoryGame:
    """State container for level-based memory gameplay."""

    def __init__(self) -> None:
        self.level_index = 0
        self.cards: list[Card] = []
        self.open_ids: list[int] = []
        self.pending_check_at: int | None = None
        self.pending_next_level_at: int | None = None

        self.ui_font = pygame.font.SysFont("Arial", 30, bold=True)
        self.card_font = pygame.font.SysFont("Arial", 48, bold=True)
        self.message_font = pygame.font.SysFont("Arial", 40, bold=True)

        self._load_level(self.level_index)

    @property
    def level_number(self) -> int:
        return self.level_index + 1

    def handle_click(self, position: tuple[int, int], now_ms: int) -> None:
        """Open a hidden card if input is currently allowed."""
        if self.pending_check_at is not None or self.pending_next_level_at is not None:
            return

        if len(self.open_ids) >= 2:
            return

        for card in self.cards:
            if card.is_matched or card.is_open:
                continue
            if card.rect.collidepoint(position):
                card.is_open = True
                self.open_ids.append(card.card_id)
                if len(self.open_ids) == 2:
                    self.pending_check_at = now_ms + MATCH_CHECK_DELAY_MS
                break

    def update(self, now_ms: int) -> None:
        """Advance timers and resolve pair matching/level transition."""
        if self.pending_check_at is not None and now_ms >= self.pending_check_at:
            self._resolve_open_pair(now_ms)

        if self.pending_next_level_at is not None and now_ms >= self.pending_next_level_at:
            self.level_index += 1
            self._load_level(self.level_index)

    def draw(self, screen: pygame.Surface) -> None:
        """Render panel text and all active cards."""
        screen.fill(BACKGROUND_COLOR)
        pygame.draw.rect(screen, PANEL_COLOR, pygame.Rect(0, 0, WINDOW_WIDTH, TOP_PANEL_HEIGHT))

        remaining = self.get_remaining_pairs()
        level_label = self.ui_font.render(f"Level: {self.level_number}", True, TEXT_COLOR)
        pairs_label = self.ui_font.render(f"Pairs left: {remaining}", True, TEXT_COLOR)
        screen.blit(level_label, (24, 24))
        screen.blit(pairs_label, (260, 24))

        for card in self.cards:
            self._draw_card(screen, card)

        if self.pending_next_level_at is not None:
            message = self.message_font.render("Level complete!", True, ACCENT_COLOR)
            msg_rect = message.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 44))
            screen.blit(message, msg_rect)

    def get_remaining_pairs(self) -> int:
        unmatched = sum(1 for card in self.cards if not card.is_matched)
        return unmatched // 2

    def _load_level(self, level_index: int) -> None:
        card_count = get_level_card_count(level_index)
        selected_patterns = self._build_level_patterns(card_count)
        coords = build_center_square_positions(card_count)

        min_x = min(x for x, _ in coords)
        max_x = max(x for x, _ in coords)
        min_y = min(y for _, y in coords)
        max_y = max(y for _, y in coords)

        cols = max_x - min_x + 1
        rows = max_y - min_y + 1
        board_width = cols * CARD_SIZE + (cols - 1) * CARD_GAP
        board_height = rows * CARD_SIZE + (rows - 1) * CARD_GAP

        start_x = (WINDOW_WIDTH - board_width) // 2
        play_area_height = WINDOW_HEIGHT - TOP_PANEL_HEIGHT
        start_y = TOP_PANEL_HEIGHT + (play_area_height - board_height) // 2

        random.shuffle(selected_patterns)
        self.cards.clear()
        self.open_ids.clear()
        self.pending_check_at = None
        self.pending_next_level_at = None

        for index, ((grid_x, grid_y), pattern) in enumerate(zip(coords, selected_patterns)):
            px = start_x + (grid_x - min_x) * (CARD_SIZE + CARD_GAP)
            py = start_y + (grid_y - min_y) * (CARD_SIZE + CARD_GAP)
            rect = pygame.Rect(px, py, CARD_SIZE, CARD_SIZE)
            self.cards.append(Card(card_id=index, pattern=pattern, rect=rect))

    def _build_level_patterns(self, card_count: int) -> list[str]:
        pair_count = card_count // 2
        if pair_count > len(PATTERN_POOL):
            raise ValueError("Pattern pool is too small for current level.")
        picks = random.sample(PATTERN_POOL, pair_count)
        return picks + picks

    def _resolve_open_pair(self, now_ms: int) -> None:
        first_id, second_id = self.open_ids
        first = self.cards[first_id]
        second = self.cards[second_id]

        if first.pattern == second.pattern:
            first.is_matched = True
            second.is_matched = True
        else:
            first.is_open = False
            second.is_open = False

        self.open_ids.clear()
        self.pending_check_at = None

        if all(card.is_matched for card in self.cards):
            self.pending_next_level_at = now_ms + LEVEL_ADVANCE_DELAY_MS

    def _draw_card(self, screen: pygame.Surface, card: Card) -> None:
        if card.is_matched:
            pygame.draw.rect(
                screen,
                CARD_MATCHED_COLOR,
                card.rect,
                border_radius=CARD_BORDER_RADIUS,
            )
            return

        fill = CARD_FACE_COLOR if card.is_open else CARD_BACK_COLOR
        pygame.draw.rect(screen, fill, card.rect, border_radius=CARD_BORDER_RADIUS)
        pygame.draw.rect(screen, CARD_BORDER_COLOR, card.rect, width=2, border_radius=CARD_BORDER_RADIUS)

        if not card.is_open:
            return

        if card.pattern.startswith("shape:"):
            self._draw_shape_pattern(screen, card.rect, card.pattern)
            return

        text = self.card_font.render(card.pattern, True, CARD_BORDER_COLOR)
        text_rect = text.get_rect(center=card.rect.center)
        screen.blit(text, text_rect)

    def _draw_shape_pattern(self, screen: pygame.Surface, rect: pygame.Rect, pattern: str) -> None:
        _, color_name, shape = pattern.split(":")
        color = SHAPE_COLORS[color_name]
        cx, cy = rect.center
        half = rect.width // 3

        if shape == "circle":
            pygame.draw.circle(screen, color, (cx, cy), half)
        elif shape == "square":
            side = half * 2
            box = pygame.Rect(cx - half, cy - half, side, side)
            pygame.draw.rect(screen, color, box, border_radius=8)
        elif shape == "triangle":
            points = [(cx, cy - half), (cx - half, cy + half), (cx + half, cy + half)]
            pygame.draw.polygon(screen, color, points)
        elif shape == "diamond":
            points = [(cx, cy - half), (cx - half, cy), (cx, cy + half), (cx + half, cy)]
            pygame.draw.polygon(screen, color, points)
