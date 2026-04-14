"""Level helpers for Memory game progression and layout order."""

from __future__ import annotations

from config import CARDS_STEP, MAX_CARDS, START_CARDS


def get_level_card_count(level_index: int) -> int:
    """Return number of cards for a given level index (0-based)."""
    return min(MAX_CARDS, START_CARDS + level_index * CARDS_STEP)


def build_center_square_positions(count: int) -> list[tuple[int, int]]:
    """Build coordinates from center square to outer rings."""
    if count <= 0:
        return []

    core = [(0, 0), (1, 0), (0, 1), (1, 1)]
    positions: list[tuple[int, int]] = []
    seen: set[tuple[int, int]] = set()

    for pos in core:
        positions.append(pos)
        seen.add(pos)
        if len(positions) >= count:
            return positions[:count]

    ring = 1
    while len(positions) < count:
        min_x = -ring
        max_x = 1 + ring
        min_y = -ring
        max_y = 1 + ring

        # Top edge (left to right)
        for x in range(min_x, max_x + 1):
            pos = (x, min_y)
            if pos not in seen:
                positions.append(pos)
                seen.add(pos)
                if len(positions) >= count:
                    return positions[:count]

        # Right edge (top to bottom)
        for y in range(min_y + 1, max_y + 1):
            pos = (max_x, y)
            if pos not in seen:
                positions.append(pos)
                seen.add(pos)
                if len(positions) >= count:
                    return positions[:count]

        # Bottom edge (right to left)
        for x in range(max_x - 1, min_x - 1, -1):
            pos = (x, max_y)
            if pos not in seen:
                positions.append(pos)
                seen.add(pos)
                if len(positions) >= count:
                    return positions[:count]

        # Left edge (bottom to top)
        for y in range(max_y - 1, min_y, -1):
            pos = (min_x, y)
            if pos not in seen:
                positions.append(pos)
                seen.add(pos)
                if len(positions) >= count:
                    return positions[:count]

        ring += 1

    return positions[:count]
