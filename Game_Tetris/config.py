"""Configuration constants for the simple PyGame Tetris game."""

CELL_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20

PLAY_WIDTH = GRID_WIDTH * CELL_SIZE
PLAY_HEIGHT = GRID_HEIGHT * CELL_SIZE

SIDE_PANEL_WIDTH = 180

WINDOW_WIDTH = PLAY_WIDTH + SIDE_PANEL_WIDTH
WINDOW_HEIGHT = PLAY_HEIGHT

FPS = 60
FALL_INTERVAL_MS = 500
SOFT_DROP_INTERVAL_MS = 50

BACKGROUND_COLOR = (18, 18, 18)
GRID_LINE_COLOR = (40, 40, 40)
BORDER_COLOR = (220, 220, 220)
TEXT_COLOR = (245, 245, 245)

# Index 0 is an empty cell.
PIECE_COLORS = {
    0: (0, 0, 0),
    1: (0, 255, 255),   # I
    2: (255, 255, 0),   # O
    3: (160, 32, 240),  # T
    4: (255, 165, 0),   # L
    5: (0, 102, 255),   # J
    6: (0, 204, 0),     # S
    7: (220, 20, 60),   # Z
}
