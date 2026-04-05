#!/usr/bin/env python3
"""
Generate spinning bone projectile sprite for Skeleton Pirate.

Sprite size: 16x16 pixels
Animation: 8 frames showing bone rotating 360 degrees

Output: assets/sprites/bone_projectile.png
"""

import math

import pygame

# Initialize pygame
pygame.init()

# Sprite dimensions
BONE_SIZE = 16
FRAME_COUNT = 8

# Colors
TRANSPARENT = (0, 0, 0, 0)
BONE_WHITE = (240, 235, 220, 255)  # Main bone color
BONE_SHADOW = (200, 190, 170, 255)  # Shadowed parts
BONE_DARK = (160, 150, 130, 255)  # Darkest shadow
BONE_HIGHLIGHT = (255, 255, 250, 255)  # Bright highlights
BLACK = (30, 30, 30, 255)  # Outline


def create_surface():
    """Create a transparent surface for one sprite frame."""
    surface = pygame.Surface((BONE_SIZE, BONE_SIZE), pygame.SRCALPHA)
    surface.fill(TRANSPARENT)
    return surface


def draw_pixel(surface, x, y, color):
    """Draw a single pixel."""
    if 0 <= x < BONE_SIZE and 0 <= y < BONE_SIZE:
        surface.set_at((int(x), int(y)), color)


def rotate_point(x, y, cx, cy, angle):
    """Rotate point (x,y) around center (cx,cy) by angle in radians."""
    cos_a = math.cos(angle)
    sin_a = math.sin(angle)
    dx = x - cx
    dy = y - cy
    return (
        cx + dx * cos_a - dy * sin_a,
        cy + dx * sin_a + dy * cos_a
    )


def draw_bone(surface, angle):
    """
    Draw a bone at the given rotation angle.

    The bone is a classic cartoon bone shape:
    - Two round ends (knobs)
    - A shaft connecting them

    Args:
        surface: Surface to draw on
        angle: Rotation angle in radians
    """
    cx, cy = BONE_SIZE // 2, BONE_SIZE // 2

    # Bone shape defined relative to center (horizontal bone)
    # Shaft: thin rectangle in the middle
    # Ends: two circles/knobs at each end

    # Draw by iterating over pixels and checking if they're part of the bone
    for py in range(BONE_SIZE):
        for px in range(BONE_SIZE):
            # Transform pixel position to bone's local coordinate system
            # (inverse rotation)
            lx, ly = rotate_point(px, py, cx, cy, -angle)

            # Check if point is part of the bone shape
            # Local coordinates: bone is horizontal, centered at (cx, cy)

            # Relative to center
            rx = lx - cx
            ry = ly - cy

            # Shaft: -4 to 4 in x, -1.5 to 1.5 in y
            in_shaft = (-4 <= rx <= 4) and (-1.5 <= ry <= 1.5)

            # Left knob: two small circles at x=-5
            left_knob_top = (rx + 5) ** 2 + (ry + 2) ** 2 <= 2.5 ** 2
            left_knob_bot = (rx + 5) ** 2 + (ry - 2) ** 2 <= 2.5 ** 2

            # Right knob: two small circles at x=5
            right_knob_top = (rx - 5) ** 2 + (ry + 2) ** 2 <= 2.5 ** 2
            right_knob_bot = (rx - 5) ** 2 + (ry - 2) ** 2 <= 2.5 ** 2

            in_bone = in_shaft or left_knob_top or left_knob_bot or right_knob_top or right_knob_bot

            if in_bone:
                # Determine color based on position for shading
                # Use rotated y for shading (top = light, bottom = dark)
                shade_y = ry * math.cos(angle) + rx * math.sin(angle)

                if shade_y < -1:
                    color = BONE_HIGHLIGHT
                elif shade_y < 0.5:
                    color = BONE_WHITE
                elif shade_y < 1.5:
                    color = BONE_SHADOW
                else:
                    color = BONE_DARK

                draw_pixel(surface, px, py, color)


def add_outline(surface):
    """Add a dark outline around the bone."""
    width, height = surface.get_size()
    outline_pixels = []

    for y in range(height):
        for x in range(width):
            color = surface.get_at((x, y))
            if color[3] > 0:  # Has content
                # Check neighbors
                for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < width and 0 <= ny < height:
                        neighbor = surface.get_at((nx, ny))
                        if neighbor[3] == 0:  # Neighbor is transparent
                            outline_pixels.append((nx, ny))

    for x, y in outline_pixels:
        surface.set_at((x, y), BLACK)


def create_spin_frame(frame_num):
    """Create one frame of the spinning animation."""
    surface = create_surface()

    # Calculate rotation angle (8 frames = 360 degrees)
    angle = (frame_num / FRAME_COUNT) * 2 * math.pi

    draw_bone(surface, angle)
    add_outline(surface)

    return surface


def generate_sprite_sheet():
    """Generate the complete bone sprite sheet (8 frames horizontal strip)."""
    sheet_width = BONE_SIZE * FRAME_COUNT
    sheet_height = BONE_SIZE

    sheet = pygame.Surface((sheet_width, sheet_height), pygame.SRCALPHA)
    sheet.fill(TRANSPARENT)

    for i in range(FRAME_COUNT):
        frame = create_spin_frame(i)
        sheet.blit(frame, (i * BONE_SIZE, 0))

    return sheet


def main():
    """Generate and save the bone sprite sheet."""
    print("Generating bone projectile sprite sheet...")

    sheet = generate_sprite_sheet()

    output_path = "assets/sprites/bone_projectile.png"
    pygame.image.save(sheet, output_path)
    print(f"Saved sprite sheet to {output_path}")
    print(f"Size: {sheet.get_width()}x{sheet.get_height()} pixels")
    print(f"Frames: {FRAME_COUNT} (spinning animation)")

    pygame.quit()


if __name__ == "__main__":
    main()
