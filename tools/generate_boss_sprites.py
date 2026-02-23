#!/usr/bin/env python3
"""
Generate NES-style 8-bit sprite sheet for Vice-Admiral Garp (Boss).

Sprite size: 48x64 pixels
Animations:
  - Idle: 2 frames (row 0)
  - Walk: 2 frames (row 0, cols 2-3)
  - Sword attack: 3 frames (row 1)
  - Pistol shot: 2 frames (row 2)
  - Charge: 1 frame (row 2, col 2)
  - Stunned: 1 frame (row 2, col 3)

Output: assets/sprites/admiral.png
"""

import pygame

# Initialize pygame
pygame.init()

# Sprite dimensions
SPRITE_WIDTH = 48
SPRITE_HEIGHT = 72  # Taller than player to be imposing

# Color palette (NES-inspired)
TRANSPARENT = (0, 0, 0, 0)
BLACK = (0, 0, 0, 255)  # Outlines
SKIN = (228, 180, 140, 255)  # Skin tone
SKIN_SHADOW = (180, 130, 100, 255)  # Skin shadow

# Naval uniform colors (fancy officer)
COAT_BLUE = (25, 50, 120, 255)  # Navy blue coat
COAT_DARK = (15, 30, 80, 255)  # Coat shadow
COAT_LIGHT = (45, 70, 150, 255)  # Coat highlight
GOLD_TRIM = (255, 215, 0, 255)  # Gold epaulettes/trim
GOLD_DARK = (180, 150, 0, 255)  # Gold shadow
WHITE_PANTS = (240, 240, 235, 255)  # White naval pants
PANTS_SHADOW = (200, 200, 195, 255)  # Pants shadow
BOOTS_BLACK = (30, 30, 35, 255)  # Black boots
BOOTS_HIGHLIGHT = (60, 60, 65, 255)  # Boot highlight

# Hat colors
HAT_BLUE = (20, 40, 100, 255)  # Hat body
HAT_DARK = (10, 25, 70, 255)  # Hat shadow
FEATHER_RED = (220, 40, 40, 255)  # Red feathers
FEATHER_DARK = (170, 25, 25, 255)  # Feather shadow

# Weapon colors
SABER_SILVER = (220, 220, 230, 255)
SABER_EDGE = (255, 255, 255, 255)
SABER_DARK = (150, 150, 165, 255)
SABER_HANDLE = (101, 67, 33, 255)
PISTOL_METAL = (80, 80, 85, 255)
PISTOL_WOOD = (120, 80, 40, 255)
PISTOL_FLASH = (255, 200, 100, 255)

# Face details
EYE_WHITE = (255, 255, 255, 255)
EYE_BLACK = (20, 20, 20, 255)
SCAR_PINK = (200, 150, 150, 255)  # Battle scar
HAIR_GRAY = (100, 100, 110, 255)  # Graying sideburns


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


def draw_feathers(surface, hat_x, hat_y):
    """Draw the five red feathers on the hat."""
    # Five feathers arranged in a fan pattern
    feather_base_x = hat_x + 18
    feather_base_y = hat_y + 2

    # Feather positions (x_offset, height, curve_direction)
    feathers = [
        (-6, 14, -2),   # Far left feather
        (-3, 16, -1),   # Left feather
        (0, 18, 0),     # Center feather (tallest)
        (3, 16, 1),     # Right feather
        (6, 14, 2),     # Far right feather
    ]

    for x_off, height, curve in feathers:
        fx = feather_base_x + x_off
        # Draw feather shaft
        for i in range(height):
            # Curve the feather
            curve_x = fx + (curve * i // 8)
            # Feather gets wider then narrower
            width = 2 if i < height - 4 else 1
            draw_rect(surface, curve_x - width // 2, feather_base_y - i, width, 1, FEATHER_RED)
            # Add some detail
            if i % 3 == 0:
                draw_pixel(surface, curve_x - 1, feather_base_y - i, FEATHER_DARK)


def draw_hat(surface, x, y, bob_y=0):
    """Draw Vice-Admiral Garp's fancy hat with 5 red feathers."""
    hat_y = y + bob_y

    # Hat brim (wide, flat)
    draw_rect(surface, x + 4, hat_y + 8, 28, 4, HAT_BLUE)
    draw_rect(surface, x + 4, hat_y + 10, 28, 2, HAT_DARK)

    # Hat body (tricorn style, raised front)
    draw_rect(surface, x + 10, hat_y + 2, 16, 8, HAT_BLUE)
    draw_rect(surface, x + 10, hat_y + 2, 4, 6, HAT_DARK)  # Shadow

    # Gold trim on hat
    draw_rect(surface, x + 10, hat_y + 7, 16, 2, GOLD_TRIM)
    draw_rect(surface, x + 10, hat_y + 7, 16, 1, GOLD_DARK)

    # Cockade (decorative rosette)
    draw_rect(surface, x + 16, hat_y + 4, 4, 4, GOLD_TRIM)

    # Draw the five red feathers!
    draw_feathers(surface, x, hat_y)


def draw_garp_face(surface, x, y, hurt=False, bob_y=0):
    """Draw Garp's face - stern, battle-scarred veteran."""
    face_y = y + bob_y

    # Face shape (large, square jaw)
    draw_rect(surface, x + 10, face_y + 12, 16, 14, SKIN)
    draw_rect(surface, x + 10, face_y + 12, 4, 12, SKIN_SHADOW)  # Shadow

    # Graying sideburns
    draw_rect(surface, x + 8, face_y + 14, 3, 6, HAIR_GRAY)
    draw_rect(surface, x + 25, face_y + 14, 3, 6, HAIR_GRAY)

    # Eyes (fierce, narrow)
    if not hurt:
        # Left eye
        draw_rect(surface, x + 13, face_y + 16, 4, 3, EYE_WHITE)
        draw_rect(surface, x + 14, face_y + 17, 2, 2, EYE_BLACK)
        # Right eye
        draw_rect(surface, x + 19, face_y + 16, 4, 3, EYE_WHITE)
        draw_rect(surface, x + 20, face_y + 17, 2, 2, EYE_BLACK)
        # Stern eyebrows
        draw_rect(surface, x + 12, face_y + 15, 5, 1, HAT_DARK)
        draw_rect(surface, x + 19, face_y + 15, 5, 1, HAT_DARK)
    else:
        # Squinting in pain
        draw_rect(surface, x + 13, face_y + 17, 4, 1, EYE_BLACK)
        draw_rect(surface, x + 19, face_y + 17, 4, 1, EYE_BLACK)

    # Battle scar (left cheek)
    draw_rect(surface, x + 12, face_y + 20, 1, 4, SCAR_PINK)

    # Nose (prominent)
    draw_rect(surface, x + 17, face_y + 18, 3, 4, SKIN_SHADOW)

    # Mouth (stern frown or grimace)
    if hurt:
        draw_rect(surface, x + 15, face_y + 24, 6, 1, (150, 100, 100, 255))
    else:
        draw_rect(surface, x + 15, face_y + 23, 6, 2, SKIN_SHADOW)


def draw_garp_body(surface, x, y, leg_offset=0, arm_offset=0, bob_y=0):
    """Draw Garp's body - large, imposing naval officer."""
    body_y = y + bob_y

    # === TORSO (large, barrel-chested) ===
    # Naval coat - taller torso
    draw_rect(surface, x + 4, body_y + 26, 28, 20, COAT_BLUE)
    draw_rect(surface, x + 4, body_y + 26, 6, 18, COAT_DARK)  # Shadow

    # Gold epaulettes (shoulder decorations)
    draw_rect(surface, x + 2, body_y + 26, 6, 4, GOLD_TRIM)
    draw_rect(surface, x + 28, body_y + 26, 6, 4, GOLD_TRIM)
    # Epaulette fringe
    draw_rect(surface, x + 1, body_y + 29, 2, 3, GOLD_DARK)
    draw_rect(surface, x + 33, body_y + 29, 2, 3, GOLD_DARK)

    # Gold buttons down front - more buttons for taller coat
    for i in range(4):
        draw_rect(surface, x + 17, body_y + 28 + i * 4, 2, 2, GOLD_TRIM)

    # Coat tails - longer
    draw_rect(surface, x + 6, body_y + 44, 8, 8, COAT_BLUE)
    draw_rect(surface, x + 22, body_y + 44, 8, 8, COAT_BLUE)
    draw_rect(surface, x + 6, body_y + 44, 2, 8, COAT_DARK)

    # White shirt/cravat visible at neck
    draw_rect(surface, x + 16, body_y + 26, 4, 3, WHITE_PANTS)

    # Belt
    draw_rect(surface, x + 6, body_y + 44, 24, 3, HAT_DARK)
    draw_rect(surface, x + 16, body_y + 44, 4, 3, GOLD_TRIM)  # Buckle

    # === ARMS ===
    arm_y = body_y + 28 + arm_offset

    # Left arm (back) - longer
    draw_rect(surface, x + 2, arm_y, 5, 14, COAT_DARK)
    draw_rect(surface, x + 2, arm_y + 12, 4, 4, SKIN_SHADOW)  # Hand

    # Right arm (front) - longer
    draw_rect(surface, x + 29, arm_y, 5, 14, COAT_BLUE)
    draw_rect(surface, x + 30, arm_y + 12, 4, 4, SKIN)  # Hand

    # Gold cuffs
    draw_rect(surface, x + 2, arm_y + 10, 5, 2, GOLD_TRIM)
    draw_rect(surface, x + 29, arm_y + 10, 5, 2, GOLD_TRIM)

    # === LEGS ===
    leg_y = body_y + 47  # Moved down for taller torso

    # Left leg - longer
    left_y = leg_y + leg_offset
    draw_rect(surface, x + 10, left_y, 8, 12, WHITE_PANTS)
    draw_rect(surface, x + 10, left_y, 2, 11, PANTS_SHADOW)

    # Right leg - longer
    right_y = leg_y - leg_offset
    draw_rect(surface, x + 20, right_y, 8, 12, WHITE_PANTS)
    draw_rect(surface, x + 20, right_y, 2, 11, PANTS_SHADOW)

    # === BOOTS ===
    # Left boot
    left_boot_y = leg_y + 10 + leg_offset
    if left_boot_y < SPRITE_HEIGHT - 4:
        draw_rect(surface, x + 8, left_boot_y, 11, 6, BOOTS_BLACK)
        draw_rect(surface, x + 10, left_boot_y + 1, 6, 2, BOOTS_HIGHLIGHT)

    # Right boot
    right_boot_y = leg_y + 10 - leg_offset
    if right_boot_y < SPRITE_HEIGHT - 4:
        draw_rect(surface, x + 19, right_boot_y, 11, 6, BOOTS_BLACK)
        draw_rect(surface, x + 21, right_boot_y + 1, 6, 2, BOOTS_HIGHLIGHT)


def draw_garp_base(surface, leg_offset=0, arm_offset=0, bob_y=0, hurt=False):
    """Draw Vice-Admiral Garp (facing right)."""
    x = 0
    y = 0

    draw_hat(surface, x, y, bob_y)
    draw_garp_face(surface, x, y, hurt, bob_y)
    draw_garp_body(surface, x, y, leg_offset, arm_offset, bob_y)


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


def draw_saber(surface, frame, x_offset=0):
    """Draw saber at different swing positions."""
    if frame == 0:
        # Wind up - saber raised behind
        draw_rect(surface, 30 + x_offset, 20, 4, 5, SABER_HANDLE)
        for i in range(14):
            draw_rect(surface, 32 + x_offset - i // 3, 14 - i, 3, 3, SABER_SILVER)
            draw_pixel(surface, 33 + x_offset - i // 3, 14 - i, SABER_EDGE)
    elif frame == 1:
        # Mid swing - saber horizontal forward (extended!)
        draw_rect(surface, 34 + x_offset, 30, 4, 5, SABER_HANDLE)
        # Long blade
        draw_rect(surface, 38 + x_offset, 28, 28, 4, SABER_SILVER)
        draw_rect(surface, 38 + x_offset, 28, 28, 1, SABER_EDGE)
        draw_rect(surface, 38 + x_offset, 31, 28, 1, SABER_DARK)
        # Tip
        draw_rect(surface, 65 + x_offset, 27, 3, 5, SABER_EDGE)
    else:
        # Follow through - saber low
        draw_rect(surface, 34 + x_offset, 38, 4, 5, SABER_HANDLE)
        for i in range(16):
            draw_rect(surface, 38 + x_offset + i, 40 + i // 2, 3, 3, SABER_SILVER)
            draw_pixel(surface, 38 + x_offset + i, 40 + i // 2, SABER_EDGE)


def draw_pistol(surface, firing=False):
    """Draw Garp holding a pistol."""
    # Pistol body
    draw_rect(surface, 34, 32, 12, 5, PISTOL_METAL)
    draw_rect(surface, 33, 36, 6, 8, PISTOL_WOOD)  # Handle

    # Barrel
    draw_rect(surface, 45, 33, 8, 3, PISTOL_METAL)

    if firing:
        # Muzzle flash
        draw_rect(surface, 52, 30, 6, 8, PISTOL_FLASH)
        draw_rect(surface, 56, 32, 4, 4, (255, 255, 200, 255))


def create_idle_frame(frame_num):
    """Create idle animation frame."""
    surface = create_surface()
    bob = 1 if frame_num == 1 else 0
    draw_garp_base(surface, leg_offset=0, arm_offset=0, bob_y=bob)
    add_outline(surface)
    return surface


def create_walk_frame(frame_num):
    """Create walk animation frame."""
    surface = create_surface()
    leg_offsets = [0, 3]
    arm_offsets = [0, -2]
    draw_garp_base(surface, leg_offset=leg_offsets[frame_num],
                   arm_offset=arm_offsets[frame_num])
    add_outline(surface)
    return surface


def create_sword_attack_frame(frame_num):
    """Create sword attack animation frame."""
    # Extended width for sword swing
    if frame_num == 1:
        # Mid-swing needs extra width
        attack_width = 70
        surface = pygame.Surface((attack_width, SPRITE_HEIGHT), pygame.SRCALPHA)
        surface.fill(TRANSPARENT)
    else:
        surface = create_surface()

    draw_garp_base(surface, leg_offset=0, arm_offset=-2 if frame_num == 0 else 2)
    draw_saber(surface, frame_num)
    add_outline(surface)

    # Crop non-extended frames
    if frame_num != 1:
        return surface

    return surface


def create_pistol_frame(frame_num):
    """Create pistol shot animation frame."""
    surface = create_surface()
    draw_garp_base(surface, leg_offset=0, arm_offset=1)
    draw_pistol(surface, firing=(frame_num == 1))
    add_outline(surface)
    return surface


def create_charge_frame():
    """Create charge attack frame - leaning forward aggressively."""
    surface = create_surface()
    # Leaning forward
    draw_garp_base(surface, leg_offset=4, arm_offset=-3)

    # Add motion lines
    for i in range(3):
        y = 30 + i * 10
        draw_rect(surface, 0, y, 8 - i * 2, 2, (200, 200, 255, 150))

    add_outline(surface)
    return surface


def create_stunned_frame():
    """Create stunned frame - dazed after phase change."""
    surface = create_surface()
    draw_garp_base(surface, leg_offset=-1, arm_offset=3, bob_y=2, hurt=True)
    add_outline(surface)
    return surface


def generate_sprite_sheet():
    """Generate the complete sprite sheet for Vice-Admiral Garp.

    Layout:
    - Row 0: Idle (2 frames), Walk (2 frames) - all 48px
    - Row 1: Sword attack (3 frames) - frame 1 is 70px wide
    - Row 2: Pistol (2 frames), Charge, Stunned - all 48px
    """
    # Calculate dimensions
    row_height = SPRITE_HEIGHT

    # Row widths
    row0_width = SPRITE_WIDTH * 4  # 192px
    row1_width = SPRITE_WIDTH + 70 + SPRITE_WIDTH  # 166px (sword attack with extended mid-frame)
    row2_width = SPRITE_WIDTH * 4  # 192px

    sheet_width = max(row0_width, row1_width, row2_width)
    sheet_height = row_height * 3

    sheet = pygame.Surface((sheet_width, sheet_height), pygame.SRCALPHA)
    sheet.fill(TRANSPARENT)

    # Row 0: Idle (2 frames) + Walk (2 frames)
    for i in range(2):
        frame = create_idle_frame(i)
        sheet.blit(frame, (i * SPRITE_WIDTH, 0))

    for i in range(2):
        frame = create_walk_frame(i)
        sheet.blit(frame, ((i + 2) * SPRITE_WIDTH, 0))

    # Row 1: Sword attack (3 frames with variable widths)
    attack_widths = [SPRITE_WIDTH, 70, SPRITE_WIDTH]
    x_offset = 0
    for i in range(3):
        frame = create_sword_attack_frame(i)
        sheet.blit(frame, (x_offset, row_height))
        x_offset += attack_widths[i]

    # Row 2: Pistol (2 frames) + Charge + Stunned
    for i in range(2):
        frame = create_pistol_frame(i)
        sheet.blit(frame, (i * SPRITE_WIDTH, row_height * 2))

    sheet.blit(create_charge_frame(), (SPRITE_WIDTH * 2, row_height * 2))
    sheet.blit(create_stunned_frame(), (SPRITE_WIDTH * 3, row_height * 2))

    return sheet


def main():
    """Generate and save the sprite sheet."""
    print("Generating Vice-Admiral Garp sprite sheet...")

    sheet = generate_sprite_sheet()

    output_path = "assets/sprites/admiral.png"
    pygame.image.save(sheet, output_path)
    print(f"Saved sprite sheet to {output_path}")
    print(f"Size: {sheet.get_width()}x{sheet.get_height()} pixels")
    print("Layout:")
    print("  Row 0: Idle (2 frames), Walk (2 frames)")
    print("  Row 1: Sword Attack (3 frames - mid-frame is 70px wide)")
    print("  Row 2: Pistol (2 frames), Charge, Stunned")

    pygame.quit()


if __name__ == "__main__":
    main()
