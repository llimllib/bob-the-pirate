#!/usr/bin/env python3
"""
Generate NES-style 8-bit sprite sheet for Parrot companion.

Sprite size: 16x12 pixels
Animations:
  - Flying: 2 frames (flapping wings)
  - Attack: 2 frames (swooping)

Output: assets/sprites/parrot.png
"""

import pygame

# Initialize pygame
pygame.init()

# Sprite dimensions
SPRITE_WIDTH = 16
SPRITE_HEIGHT = 12

# Color palette (NES-inspired tropical parrot)
TRANSPARENT = (0, 0, 0, 0)
BLACK = (0, 0, 0, 255)  # Outlines

# Parrot colors (vibrant tropical)
BODY_GREEN = (50, 180, 80, 255)  # Main body
BODY_DARK = (30, 130, 50, 255)  # Body shadow
WING_GREEN = (70, 200, 100, 255)  # Wing highlight
WING_DARK = (20, 100, 40, 255)  # Wing shadow

BEAK_YELLOW = (255, 220, 80, 255)  # Beak
BEAK_ORANGE = (255, 180, 50, 255)  # Beak shadow

EYE_WHITE = (255, 255, 255, 255)
EYE_BLACK = (20, 20, 20, 255)

TAIL_RED = (220, 60, 60, 255)  # Tail feathers
TAIL_DARK = (180, 40, 40, 255)

CREST_YELLOW = (255, 240, 100, 255)  # Head crest


def create_surface():
    """Create a transparent surface for one sprite frame."""
    surface = pygame.Surface((SPRITE_WIDTH, SPRITE_HEIGHT), pygame.SRCALPHA)
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


def add_outline(surface):
    """Add a 1-pixel black outline around non-transparent pixels."""
    width, height = surface.get_size()
    outline_pixels = []

    for y in range(height):
        for x in range(width):
            color = surface.get_at((x, y))
            if color[3] > 0 and color != BLACK:
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        neighbor = surface.get_at((nx, ny))
                        if neighbor[3] == 0:
                            outline_pixels.append((nx, ny))

    for x, y in outline_pixels:
        surface.set_at((x, y), BLACK)


def draw_parrot_body(surface, wing_up=False, attacking=False):
    """Draw the parrot's body (facing right)."""
    # Body (round, plump)
    draw_rect(surface, 5, 3, 6, 6, BODY_GREEN)
    draw_rect(surface, 5, 3, 2, 5, BODY_DARK)  # Shadow

    # Head
    draw_rect(surface, 9, 2, 4, 4, BODY_GREEN)

    # Crest (small feathers on top)
    draw_rect(surface, 10, 0, 2, 2, CREST_YELLOW)

    # Eye
    draw_pixel(surface, 11, 3, EYE_WHITE)
    draw_pixel(surface, 12, 3, EYE_BLACK)

    # Beak (curved, pointing right)
    draw_rect(surface, 13, 3, 3, 2, BEAK_YELLOW)
    draw_pixel(surface, 15, 4, BEAK_ORANGE)
    draw_pixel(surface, 14, 5, BEAK_ORANGE)  # Lower beak

    # Tail feathers (pointing left/back)
    draw_rect(surface, 1, 5, 4, 2, TAIL_RED)
    draw_rect(surface, 0, 6, 3, 2, TAIL_DARK)

    # Wings
    if attacking:
        # Wings swept back for attack dive
        draw_rect(surface, 3, 2, 4, 3, WING_DARK)
        draw_rect(surface, 2, 3, 3, 2, WING_GREEN)
    elif wing_up:
        # Wings up
        draw_rect(surface, 6, 0, 4, 4, WING_GREEN)
        draw_rect(surface, 6, 0, 2, 3, WING_DARK)
    else:
        # Wings down
        draw_rect(surface, 6, 6, 4, 4, WING_GREEN)
        draw_rect(surface, 6, 7, 2, 3, WING_DARK)

    # Feet (small, tucked under)
    if not attacking:
        draw_rect(surface, 7, 9, 2, 2, BEAK_ORANGE)
        draw_rect(surface, 10, 9, 2, 2, BEAK_ORANGE)


def create_flying_frame(frame_num):
    """Create flying animation frame."""
    surface = create_surface()
    wing_up = (frame_num == 0)
    draw_parrot_body(surface, wing_up=wing_up)
    add_outline(surface)
    return surface


def create_attack_frame(frame_num):
    """Create attack/swoop animation frame."""
    surface = create_surface()
    draw_parrot_body(surface, attacking=True)

    # Add motion lines for attack
    if frame_num == 1:
        # Swooping forward
        for i in range(3):
            draw_pixel(surface, 2 - i, 4 + i, (255, 255, 255, 128))

    add_outline(surface)
    return surface


def generate_sprite_sheet():
    """Generate the complete sprite sheet.

    Layout:
    - Row 0: Flying (2 frames), Attack (2 frames)
    """
    cols = 4
    sheet_width = SPRITE_WIDTH * cols
    sheet_height = SPRITE_HEIGHT

    sheet = pygame.Surface((sheet_width, sheet_height), pygame.SRCALPHA)
    sheet.fill(TRANSPARENT)

    # Flying frames
    for i in range(2):
        frame = create_flying_frame(i)
        sheet.blit(frame, (i * SPRITE_WIDTH, 0))

    # Attack frames
    for i in range(2):
        frame = create_attack_frame(i)
        sheet.blit(frame, ((i + 2) * SPRITE_WIDTH, 0))

    return sheet


def main():
    """Generate and save the sprite sheet."""
    print("Generating Parrot companion sprite sheet...")

    sheet = generate_sprite_sheet()

    output_path = "assets/sprites/parrot.png"
    pygame.image.save(sheet, output_path)
    print(f"Saved sprite sheet to {output_path}")
    print(f"Size: {sheet.get_width()}x{sheet.get_height()} pixels")
    print("Layout:")
    print("  Row 0: Flying (2 frames), Attack (2 frames)")

    pygame.quit()


if __name__ == "__main__":
    main()
