#!/usr/bin/env python3
"""
Generate NES-style 8-bit tile sprites for Bob the Pirate.

Tile size: 32x32 pixels

Tiles generated:
  - Solid ground tiles (top, middle, left edge, right edge, corners, bottom, inner)
  - One-way platform tile
  - Decorations (crate, barrel, anchor, rope coil)

Output: assets/tiles/tileset.png
"""

import pygame

# Initialize pygame
pygame.init()

# Tile dimensions
TILE_SIZE = 32

# Color palette (NES-inspired, pirate theme)
TRANSPARENT = (0, 0, 0, 0)
BLACK = (0, 0, 0, 255)

# Wood/dock colors
WOOD_LIGHT = (180, 130, 80, 255)
WOOD_MID = (139, 90, 55, 255)
WOOD_DARK = (100, 65, 35, 255)
WOOD_GRAIN = (120, 75, 45, 255)

# Stone colors (for fortress/dock foundation)
STONE_LIGHT = (140, 140, 140, 255)
STONE_MID = (100, 100, 100, 255)
STONE_DARK = (70, 70, 70, 255)
STONE_HIGHLIGHT = (170, 170, 170, 255)

# Platform colors
PLATFORM_LIGHT = (160, 120, 70, 255)
PLATFORM_MID = (130, 95, 55, 255)
PLATFORM_DARK = (95, 70, 40, 255)

# Decoration colors
METAL_DARK = (60, 60, 70, 255)
METAL_MID = (90, 90, 100, 255)
METAL_LIGHT = (120, 120, 130, 255)
ROPE_TAN = (180, 155, 110, 255)
ROPE_DARK = (140, 115, 75, 255)
BARREL_BROWN = (120, 80, 45, 255)
BARREL_DARK = (85, 55, 30, 255)
BARREL_BAND = (70, 70, 80, 255)


def create_surface(width=TILE_SIZE, height=TILE_SIZE):
    """Create a transparent surface."""
    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    surface.fill(TRANSPARENT)
    return surface


def draw_pixel(surface, x, y, color):
    """Draw a single pixel."""
    w, h = surface.get_size()
    if 0 <= x < w and 0 <= y < h:
        surface.set_at((x, y), color)


def draw_rect(surface, x, y, w, h, color):
    """Draw a filled rectangle."""
    for py in range(y, y + h):
        for px in range(x, x + w):
            draw_pixel(surface, px, py, color)


def draw_line_h(surface, x, y, length, color):
    """Draw a horizontal line."""
    for i in range(length):
        draw_pixel(surface, x + i, y, color)


def draw_line_v(surface, x, y, length, color):
    """Draw a vertical line."""
    for i in range(length):
        draw_pixel(surface, x, y + i, color)


# =============================================================================
# SOLID GROUND TILES (wooden dock/ship deck style)
# =============================================================================

def create_solid_top():
    """Create solid tile with top edge (grass/surface)."""
    surface = create_surface()

    # Main wood fill
    draw_rect(surface, 0, 4, TILE_SIZE, TILE_SIZE - 4, WOOD_MID)

    # Top edge highlight (lighter plank edge)
    draw_rect(surface, 0, 0, TILE_SIZE, 4, WOOD_LIGHT)
    draw_line_h(surface, 0, 3, TILE_SIZE, WOOD_DARK)

    # Wood grain lines (horizontal planks)
    for y in [10, 18, 26]:
        draw_line_h(surface, 0, y, TILE_SIZE, WOOD_DARK)
        draw_line_h(surface, 2, y + 1, TILE_SIZE - 4, WOOD_GRAIN)

    # Nail heads
    for x, y in [(4, 6), (28, 6), (8, 14), (24, 14), (4, 22), (28, 22), (8, 30), (24, 30)]:
        draw_pixel(surface, x, y, WOOD_DARK)

    return surface


def create_solid_middle():
    """Create solid tile for middle/fill areas."""
    surface = create_surface()

    # Main wood fill
    draw_rect(surface, 0, 0, TILE_SIZE, TILE_SIZE, WOOD_MID)

    # Wood grain lines
    for y in [2, 10, 18, 26]:
        draw_line_h(surface, 0, y, TILE_SIZE, WOOD_DARK)
        draw_line_h(surface, 2, y + 1, TILE_SIZE - 4, WOOD_GRAIN)

    # Nail heads
    for x, y in [(4, 6), (28, 6), (8, 14), (24, 14), (4, 22), (28, 22), (8, 30), (24, 30)]:
        draw_pixel(surface, x, y, WOOD_DARK)

    return surface


def create_solid_bottom():
    """Create solid tile with bottom edge."""
    surface = create_surface()

    # Main wood fill
    draw_rect(surface, 0, 0, TILE_SIZE, TILE_SIZE - 4, WOOD_MID)

    # Bottom edge (darker)
    draw_rect(surface, 0, TILE_SIZE - 4, TILE_SIZE, 4, WOOD_DARK)
    draw_line_h(surface, 0, TILE_SIZE - 4, TILE_SIZE, BLACK)

    # Wood grain lines
    for y in [2, 10, 18]:
        draw_line_h(surface, 0, y, TILE_SIZE, WOOD_DARK)
        draw_line_h(surface, 2, y + 1, TILE_SIZE - 4, WOOD_GRAIN)

    return surface


def create_solid_left():
    """Create solid tile with left edge."""
    surface = create_surface()

    # Main wood fill
    draw_rect(surface, 4, 0, TILE_SIZE - 4, TILE_SIZE, WOOD_MID)

    # Left edge
    draw_rect(surface, 0, 0, 4, TILE_SIZE, WOOD_DARK)
    draw_line_v(surface, 3, 0, TILE_SIZE, BLACK)

    # Wood grain
    for y in [2, 10, 18, 26]:
        draw_line_h(surface, 4, y, TILE_SIZE - 4, WOOD_DARK)

    return surface


def create_solid_right():
    """Create solid tile with right edge."""
    surface = create_surface()

    # Main wood fill
    draw_rect(surface, 0, 0, TILE_SIZE - 4, TILE_SIZE, WOOD_MID)

    # Right edge
    draw_rect(surface, TILE_SIZE - 4, 0, 4, TILE_SIZE, WOOD_DARK)
    draw_line_v(surface, TILE_SIZE - 4, 0, TILE_SIZE, BLACK)

    # Wood grain
    for y in [2, 10, 18, 26]:
        draw_line_h(surface, 0, y, TILE_SIZE - 4, WOOD_DARK)

    return surface


def create_solid_top_left():
    """Create corner tile (top-left)."""
    surface = create_surface()

    # Main fill
    draw_rect(surface, 4, 4, TILE_SIZE - 4, TILE_SIZE - 4, WOOD_MID)

    # Top edge
    draw_rect(surface, 4, 0, TILE_SIZE - 4, 4, WOOD_LIGHT)
    draw_line_h(surface, 4, 3, TILE_SIZE - 4, WOOD_DARK)

    # Left edge
    draw_rect(surface, 0, 4, 4, TILE_SIZE - 4, WOOD_DARK)
    draw_line_v(surface, 3, 4, TILE_SIZE - 4, BLACK)

    # Corner
    draw_rect(surface, 0, 0, 4, 4, WOOD_DARK)

    return surface


def create_solid_top_right():
    """Create corner tile (top-right)."""
    surface = create_surface()

    # Main fill
    draw_rect(surface, 0, 4, TILE_SIZE - 4, TILE_SIZE - 4, WOOD_MID)

    # Top edge
    draw_rect(surface, 0, 0, TILE_SIZE - 4, 4, WOOD_LIGHT)
    draw_line_h(surface, 0, 3, TILE_SIZE - 4, WOOD_DARK)

    # Right edge
    draw_rect(surface, TILE_SIZE - 4, 4, 4, TILE_SIZE - 4, WOOD_DARK)
    draw_line_v(surface, TILE_SIZE - 4, 4, TILE_SIZE - 4, BLACK)

    # Corner
    draw_rect(surface, TILE_SIZE - 4, 0, 4, 4, WOOD_DARK)

    return surface


def create_solid_bottom_left():
    """Create corner tile (bottom-left)."""
    surface = create_surface()

    # Main fill
    draw_rect(surface, 4, 0, TILE_SIZE - 4, TILE_SIZE - 4, WOOD_MID)

    # Left edge
    draw_rect(surface, 0, 0, 4, TILE_SIZE - 4, WOOD_DARK)
    draw_line_v(surface, 3, 0, TILE_SIZE - 4, BLACK)

    # Bottom edge
    draw_rect(surface, 4, TILE_SIZE - 4, TILE_SIZE - 4, 4, WOOD_DARK)
    draw_line_h(surface, 4, TILE_SIZE - 4, TILE_SIZE - 4, BLACK)

    # Corner
    draw_rect(surface, 0, TILE_SIZE - 4, 4, 4, WOOD_DARK)

    return surface


def create_solid_bottom_right():
    """Create corner tile (bottom-right)."""
    surface = create_surface()

    # Main fill
    draw_rect(surface, 0, 0, TILE_SIZE - 4, TILE_SIZE - 4, WOOD_MID)

    # Right edge
    draw_rect(surface, TILE_SIZE - 4, 0, 4, TILE_SIZE - 4, WOOD_DARK)
    draw_line_v(surface, TILE_SIZE - 4, 0, TILE_SIZE - 4, BLACK)

    # Bottom edge
    draw_rect(surface, 0, TILE_SIZE - 4, TILE_SIZE - 4, 4, WOOD_DARK)
    draw_line_h(surface, 0, TILE_SIZE - 4, TILE_SIZE - 4, BLACK)

    # Corner
    draw_rect(surface, TILE_SIZE - 4, TILE_SIZE - 4, 4, 4, WOOD_DARK)

    return surface


# =============================================================================
# PLATFORM TILE (one-way)
# =============================================================================

def create_platform():
    """Create one-way platform tile (thin wooden plank)."""
    surface = create_surface()

    # Main platform (only top portion, thin)
    draw_rect(surface, 0, 0, TILE_SIZE, 8, PLATFORM_MID)

    # Top highlight
    draw_line_h(surface, 0, 0, TILE_SIZE, PLATFORM_LIGHT)
    draw_line_h(surface, 0, 1, TILE_SIZE, PLATFORM_LIGHT)

    # Bottom shadow
    draw_line_h(surface, 0, 6, TILE_SIZE, PLATFORM_DARK)
    draw_line_h(surface, 0, 7, TILE_SIZE, PLATFORM_DARK)

    # Wood grain
    draw_line_h(surface, 2, 3, 8, PLATFORM_DARK)
    draw_line_h(surface, 14, 4, 6, PLATFORM_DARK)
    draw_line_h(surface, 24, 3, 6, PLATFORM_DARK)

    # Support brackets on sides
    draw_rect(surface, 0, 8, 4, 4, METAL_DARK)
    draw_rect(surface, 1, 9, 2, 2, METAL_MID)
    draw_rect(surface, TILE_SIZE - 4, 8, 4, 4, METAL_DARK)
    draw_rect(surface, TILE_SIZE - 3, 9, 2, 2, METAL_MID)

    return surface


# =============================================================================
# DECORATION TILES
# =============================================================================

def create_crate():
    """Create wooden crate decoration (32x32)."""
    surface = create_surface()

    # Main crate body
    draw_rect(surface, 2, 2, 28, 28, WOOD_MID)

    # Edges/frame
    draw_rect(surface, 0, 0, TILE_SIZE, 2, WOOD_DARK)  # Top
    draw_rect(surface, 0, TILE_SIZE - 2, TILE_SIZE, 2, WOOD_DARK)  # Bottom
    draw_rect(surface, 0, 0, 2, TILE_SIZE, WOOD_DARK)  # Left
    draw_rect(surface, TILE_SIZE - 2, 0, 2, TILE_SIZE, WOOD_DARK)  # Right

    # Cross braces
    draw_rect(surface, 14, 2, 4, 28, WOOD_DARK)  # Vertical
    draw_rect(surface, 2, 14, 28, 4, WOOD_DARK)  # Horizontal

    # Highlights
    draw_line_h(surface, 4, 4, 9, WOOD_LIGHT)
    draw_line_h(surface, 19, 4, 9, WOOD_LIGHT)
    draw_line_h(surface, 4, 20, 9, WOOD_LIGHT)
    draw_line_h(surface, 19, 20, 9, WOOD_LIGHT)

    # Corner nails
    for x, y in [(4, 4), (26, 4), (4, 26), (26, 26)]:
        draw_rect(surface, x, y, 2, 2, METAL_DARK)

    return surface


def create_barrel():
    """Create wooden barrel decoration (32x32)."""
    surface = create_surface()

    # Barrel body (slightly curved appearance via shading)
    # Center (lighter)
    draw_rect(surface, 8, 4, 16, 24, BARREL_BROWN)
    # Left side (darker for curve)
    draw_rect(surface, 4, 6, 4, 20, BARREL_DARK)
    # Right side (darker for curve)
    draw_rect(surface, 24, 6, 4, 20, BARREL_DARK)

    # Top/bottom curves
    draw_rect(surface, 6, 2, 20, 4, BARREL_DARK)
    draw_rect(surface, 8, 2, 16, 2, BARREL_BROWN)
    draw_rect(surface, 6, 26, 20, 4, BARREL_DARK)
    draw_rect(surface, 8, 28, 16, 2, BARREL_BROWN)

    # Metal bands
    draw_rect(surface, 4, 8, 24, 3, BARREL_BAND)
    draw_rect(surface, 6, 9, 20, 1, METAL_LIGHT)  # Highlight
    draw_rect(surface, 4, 21, 24, 3, BARREL_BAND)
    draw_rect(surface, 6, 22, 20, 1, METAL_LIGHT)  # Highlight

    # Wood grain lines
    for x in [10, 14, 18, 22]:
        draw_line_v(surface, x, 4, 5, BARREL_DARK)
        draw_line_v(surface, x, 11, 10, BARREL_DARK)
        draw_line_v(surface, x, 24, 4, BARREL_DARK)

    return surface


def create_anchor():
    """Create anchor decoration (32x32)."""
    surface = create_surface()

    # Ring at top
    draw_rect(surface, 12, 2, 8, 6, METAL_MID)
    draw_rect(surface, 14, 4, 4, 2, TRANSPARENT)  # Hole

    # Main shaft
    draw_rect(surface, 14, 8, 4, 16, METAL_DARK)
    draw_line_v(surface, 15, 8, 16, METAL_MID)  # Highlight

    # Cross bar (stock)
    draw_rect(surface, 6, 10, 20, 4, METAL_DARK)
    draw_line_h(surface, 6, 11, 20, METAL_MID)  # Highlight

    # Left fluke (curved arm)
    draw_rect(surface, 4, 22, 10, 4, METAL_DARK)
    draw_rect(surface, 2, 24, 4, 6, METAL_DARK)
    draw_pixel(surface, 2, 29, METAL_LIGHT)  # Point
    draw_line_h(surface, 4, 23, 10, METAL_MID)

    # Right fluke
    draw_rect(surface, 18, 22, 10, 4, METAL_DARK)
    draw_rect(surface, 26, 24, 4, 6, METAL_DARK)
    draw_pixel(surface, 29, 29, METAL_LIGHT)  # Point
    draw_line_h(surface, 18, 23, 10, METAL_MID)

    return surface


def create_rope_coil():
    """Create coiled rope decoration (32x32)."""
    surface = create_surface()

    # Draw concentric rope coil from outside in
    # Outer loop
    draw_rect(surface, 4, 8, 24, 4, ROPE_TAN)
    draw_rect(surface, 4, 8, 24, 2, ROPE_DARK)  # Shadow on top
    draw_rect(surface, 4, 20, 24, 4, ROPE_TAN)
    draw_rect(surface, 4, 22, 24, 2, ROPE_DARK)  # Shadow on bottom
    draw_rect(surface, 4, 12, 4, 8, ROPE_TAN)
    draw_rect(surface, 4, 12, 2, 8, ROPE_DARK)
    draw_rect(surface, 24, 12, 4, 8, ROPE_TAN)
    draw_rect(surface, 24, 12, 2, 8, ROPE_DARK)

    # Middle loop
    draw_rect(surface, 8, 12, 16, 3, ROPE_TAN)
    draw_rect(surface, 8, 12, 16, 1, ROPE_DARK)
    draw_rect(surface, 8, 17, 16, 3, ROPE_TAN)
    draw_rect(surface, 8, 19, 16, 1, ROPE_DARK)
    draw_rect(surface, 8, 15, 3, 2, ROPE_TAN)
    draw_rect(surface, 21, 15, 3, 2, ROPE_TAN)

    # Center coil
    draw_rect(surface, 12, 14, 8, 4, ROPE_TAN)
    draw_rect(surface, 14, 15, 4, 2, ROPE_DARK)

    # Rope end trailing off
    draw_rect(surface, 26, 22, 4, 3, ROPE_TAN)
    draw_rect(surface, 28, 25, 3, 4, ROPE_TAN)

    return surface


# =============================================================================
# SPRITE SHEET GENERATION
# =============================================================================

def generate_tileset():
    """
    Generate the complete tileset sprite sheet.

    Layout (32x32 tiles):
    Row 0: solid_top, solid_middle, solid_bottom, solid_left
    Row 1: solid_right, solid_top_left, solid_top_right, solid_bottom_left
    Row 2: solid_bottom_right, platform, (empty), (empty)
    Row 3: crate, barrel, anchor, rope_coil

    Total: 4 columns x 4 rows = 128x128 pixels
    """
    cols = 4
    rows = 4
    sheet_width = TILE_SIZE * cols
    sheet_height = TILE_SIZE * rows

    sheet = pygame.Surface((sheet_width, sheet_height), pygame.SRCALPHA)
    sheet.fill(TRANSPARENT)

    # Row 0: Basic solid tiles
    sheet.blit(create_solid_top(), (0 * TILE_SIZE, 0))
    sheet.blit(create_solid_middle(), (1 * TILE_SIZE, 0))
    sheet.blit(create_solid_bottom(), (2 * TILE_SIZE, 0))
    sheet.blit(create_solid_left(), (3 * TILE_SIZE, 0))

    # Row 1: More solid tiles
    sheet.blit(create_solid_right(), (0 * TILE_SIZE, TILE_SIZE))
    sheet.blit(create_solid_top_left(), (1 * TILE_SIZE, TILE_SIZE))
    sheet.blit(create_solid_top_right(), (2 * TILE_SIZE, TILE_SIZE))
    sheet.blit(create_solid_bottom_left(), (3 * TILE_SIZE, TILE_SIZE))

    # Row 2: Corner and platform
    sheet.blit(create_solid_bottom_right(), (0 * TILE_SIZE, 2 * TILE_SIZE))
    sheet.blit(create_platform(), (1 * TILE_SIZE, 2 * TILE_SIZE))
    # Slots 2-3 empty for future tiles

    # Row 3: Decorations
    sheet.blit(create_crate(), (0 * TILE_SIZE, 3 * TILE_SIZE))
    sheet.blit(create_barrel(), (1 * TILE_SIZE, 3 * TILE_SIZE))
    sheet.blit(create_anchor(), (2 * TILE_SIZE, 3 * TILE_SIZE))
    sheet.blit(create_rope_coil(), (3 * TILE_SIZE, 3 * TILE_SIZE))

    return sheet


# Tile indices for easy reference
TILE_INDEX = {
    "solid_top": (0, 0),
    "solid_middle": (1, 0),
    "solid_bottom": (2, 0),
    "solid_left": (3, 0),
    "solid_right": (0, 1),
    "solid_top_left": (1, 1),
    "solid_top_right": (2, 1),
    "solid_bottom_left": (3, 1),
    "solid_bottom_right": (0, 2),
    "platform": (1, 2),
    "crate": (0, 3),
    "barrel": (1, 3),
    "anchor": (2, 3),
    "rope_coil": (3, 3),
}


def main():
    """Generate and save the tileset."""
    print("Generating tileset sprite sheet...")

    sheet = generate_tileset()

    output_path = "assets/tiles/tileset.png"
    pygame.image.save(sheet, output_path)
    print(f"Saved tileset to {output_path}")
    print(f"Size: {sheet.get_width()}x{sheet.get_height()} pixels")
    print("\nTile layout:")
    print("  Row 0: solid_top, solid_middle, solid_bottom, solid_left")
    print("  Row 1: solid_right, solid_top_left, solid_top_right, solid_bottom_left")
    print("  Row 2: solid_bottom_right, platform, (empty), (empty)")
    print("  Row 3: crate, barrel, anchor, rope_coil")
    print("\nTile indices (col, row):")
    for name, (col, row) in TILE_INDEX.items():
        print(f"  {name}: ({col}, {row})")

    pygame.quit()


if __name__ == "__main__":
    main()
