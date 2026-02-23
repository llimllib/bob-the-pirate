#!/usr/bin/env python3
"""
Generate NES-style 8-bit sprite sheet for Captain Bob the Pirate.

Sprite size: 32x48 pixels
Animations:
  - Idle: 2 frames (row 0)
  - Run: 4 frames (row 1)
  - Jump: 1 frame (row 2, col 0)
  - Fall: 1 frame (row 2, col 1)
  - Attack: 3 frames (row 3)
  - Hurt: 1 frame (row 2, col 2)

Output: assets/sprites/player.png
"""

import pygame

# Initialize pygame
pygame.init()

# Sprite dimensions
SPRITE_WIDTH = 32
SPRITE_HEIGHT = 48

# Color palette (NES-inspired, 8-12 colors)
TRANSPARENT = (0, 0, 0, 0)
BLACK = (0, 0, 0, 255)  # Outlines
SKIN = (228, 180, 140, 255)  # Skin tone
SKIN_SHADOW = (180, 130, 100, 255)  # Skin shadow
BANDANA_RED = (220, 50, 50, 255)  # Red bandana
BANDANA_DARK = (170, 30, 30, 255)  # Bandana shadow
SHIRT_WHITE = (245, 240, 225, 255)  # Cream/white shirt
SHIRT_SHADOW = (200, 195, 180, 255)  # Shirt shadow
PANTS_BROWN = (139, 90, 43, 255)  # Brown pants
PANTS_DARK = (100, 65, 30, 255)  # Pants shadow
BOOTS_BLACK = (45, 45, 45, 255)  # Black boots
BOOTS_HIGHLIGHT = (75, 75, 75, 255)  # Boot highlight
SABER_SILVER = (220, 220, 230, 255)  # Saber blade
SABER_EDGE = (255, 255, 255, 255)  # Saber edge highlight
SABER_DARK = (150, 150, 165, 255)  # Saber shadow
SABER_HANDLE = (101, 67, 33, 255)  # Saber handle (brown)
GOATEE_BROWN = (70, 45, 25, 255)  # Goatee color
EYE_WHITE = (255, 255, 255, 255)
EYE_BLACK = (20, 20, 20, 255)
BELT_GOLD = (200, 160, 60, 255)  # Belt buckle


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


def draw_bob_base(surface, leg_offset=0, arm_offset=0, bob_y=0):
    """
    Draw Captain Bob's base sprite (facing right).

    Args:
        surface: pygame Surface to draw on
        leg_offset: offset for leg animation (alternating legs)
        arm_offset: offset for arm position
        bob_y: vertical offset for breathing/jumping
    """
    y_off = bob_y  # Vertical offset

    # === HEAD (y: 4-16) ===
    # Bandana (top of head)
    draw_rect(surface, 10, 4 + y_off, 12, 5, BANDANA_RED)
    draw_rect(surface, 12, 5 + y_off, 8, 2, BANDANA_DARK)  # Shadow fold
    # Bandana tail
    draw_rect(surface, 22, 6 + y_off, 4, 2, BANDANA_RED)
    draw_rect(surface, 24, 8 + y_off, 3, 2, BANDANA_DARK)

    # Face
    draw_rect(surface, 10, 9 + y_off, 12, 9, SKIN)
    draw_rect(surface, 10, 9 + y_off, 3, 7, SKIN_SHADOW)  # Left shadow

    # Eye (right side of face when facing right)
    draw_rect(surface, 17, 11 + y_off, 3, 3, EYE_WHITE)
    draw_rect(surface, 18, 12 + y_off, 2, 2, EYE_BLACK)

    # Nose
    draw_rect(surface, 21, 13 + y_off, 2, 2, SKIN_SHADOW)

    # Goatee
    draw_rect(surface, 13, 15 + y_off, 6, 3, GOATEE_BROWN)
    draw_rect(surface, 14, 18 + y_off, 4, 1, GOATEE_BROWN)

    # === BODY (y: 18-30) ===
    # Shirt (torso) - burly/wide
    draw_rect(surface, 6, 19 + y_off, 20, 10, SHIRT_WHITE)
    draw_rect(surface, 6, 19 + y_off, 5, 8, SHIRT_SHADOW)  # Left shadow

    # V-neck / chest
    draw_rect(surface, 14, 19 + y_off, 4, 2, SKIN)

    # Belt
    draw_rect(surface, 6, 28 + y_off, 20, 3, PANTS_DARK)
    draw_rect(surface, 14, 28 + y_off, 4, 3, BELT_GOLD)  # Buckle

    # === ARMS ===
    arm_y = 20 + y_off + arm_offset

    # Back arm (left, partially hidden)
    draw_rect(surface, 4, arm_y, 4, 8, SHIRT_SHADOW)
    draw_rect(surface, 4, arm_y + 7, 4, 3, SKIN_SHADOW)  # Hand

    # Front arm (right)
    draw_rect(surface, 24, arm_y, 4, 8, SHIRT_WHITE)
    draw_rect(surface, 24, arm_y + 7, 4, 3, SKIN)  # Hand

    # === LEGS (y: 31-42) ===
    leg_base_y = 31 + y_off

    # Left leg
    left_y = leg_base_y + leg_offset
    draw_rect(surface, 8, left_y, 6, 8, PANTS_BROWN)
    draw_rect(surface, 8, left_y, 2, 7, PANTS_DARK)

    # Right leg
    right_y = leg_base_y - leg_offset
    draw_rect(surface, 18, right_y, 6, 8, PANTS_BROWN)
    draw_rect(surface, 18, right_y, 2, 7, PANTS_DARK)

    # === BOOTS (y: 39-47) ===
    # Left boot
    left_boot_y = 39 + y_off + leg_offset
    if left_boot_y < SPRITE_HEIGHT - 5:
        draw_rect(surface, 6, left_boot_y, 9, 6, BOOTS_BLACK)
        draw_rect(surface, 8, left_boot_y + 1, 4, 2, BOOTS_HIGHLIGHT)

    # Right boot
    right_boot_y = 39 + y_off - leg_offset
    if right_boot_y < SPRITE_HEIGHT - 5:
        draw_rect(surface, 17, right_boot_y, 9, 6, BOOTS_BLACK)
        draw_rect(surface, 19, right_boot_y + 1, 4, 2, BOOTS_HIGHLIGHT)


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


def draw_saber_swing(surface, frame):
    """Draw saber at different swing positions."""
    if frame == 0:
        # Wind up - saber raised behind
        # Handle near shoulder
        draw_rect(surface, 22, 14, 3, 4, SABER_HANDLE)
        # Blade going up-back
        for i in range(12):
            draw_rect(surface, 24 - i // 3, 8 - i, 2, 3, SABER_SILVER)
            draw_pixel(surface, 25 - i // 3, 8 - i, SABER_EDGE)
    elif frame == 1:
        # Mid swing - saber horizontal forward (extended!)
        draw_rect(surface, 26, 22, 3, 4, SABER_HANDLE)
        # Blade extending right - longer saber (24 pixels)
        draw_rect(surface, 29, 20, 24, 3, SABER_SILVER)
        draw_rect(surface, 29, 20, 24, 1, SABER_EDGE)
        draw_rect(surface, 29, 22, 24, 1, SABER_DARK)
        # Saber tip
        draw_rect(surface, 52, 19, 2, 4, SABER_EDGE)
    else:
        # Follow through - saber low
        draw_rect(surface, 26, 28, 3, 4, SABER_HANDLE)
        # Blade going down-forward - longer
        for i in range(14):
            draw_rect(surface, 29 + i, 30 + i // 2, 2, 3, SABER_SILVER)
            draw_pixel(surface, 29 + i, 30 + i // 2, SABER_EDGE)


def create_idle_frame(frame_num):
    """Create idle animation frame (breathing motion)."""
    surface = create_surface()
    # More noticeable breathing - bob up/down by 2 pixels
    bob = 2 if frame_num == 1 else 0
    arm_bob = 1 if frame_num == 1 else 0
    draw_bob_base(surface, leg_offset=0, arm_offset=arm_bob, bob_y=bob)
    add_outline(surface)
    return surface


def create_run_frame(frame_num):
    """Create run animation frame."""
    surface = create_surface()
    # More exaggerated leg offsets for run cycle
    leg_offsets = [0, 5, 0, -5]
    arm_offsets = [0, -3, 0, 3]
    bob_offsets = [0, -1, 0, -1]  # Slight vertical bob while running
    draw_bob_base(surface, leg_offset=leg_offsets[frame_num],
                  arm_offset=arm_offsets[frame_num], bob_y=bob_offsets[frame_num])
    add_outline(surface)
    return surface


def create_jump_frame():
    """Create jump (rising) frame - legs tucked, arms up."""
    surface = create_surface()
    draw_bob_base(surface, leg_offset=-2, arm_offset=-3, bob_y=-2)
    add_outline(surface)
    return surface


def create_fall_frame():
    """Create fall (descending) frame - limbs spread."""
    surface = create_surface()
    draw_bob_base(surface, leg_offset=2, arm_offset=2, bob_y=0)
    add_outline(surface)
    return surface


def create_attack_frame(frame_num):
    """Create attack animation frame (saber slash)."""
    # Use wider surface for attack to fit extended saber (56px wide)
    attack_width = 56
    surface = pygame.Surface((attack_width, SPRITE_HEIGHT), pygame.SRCALPHA)
    surface.fill(TRANSPARENT)

    # Draw Bob
    bob_surface = create_surface()
    draw_bob_base(bob_surface, leg_offset=0, arm_offset=-1 if frame_num == 0 else 1)
    surface.blit(bob_surface, (0, 0))

    # Draw saber
    draw_saber_swing(surface, frame_num)

    add_outline(surface)

    # Return full width for mid-swing, crop others to standard width
    if frame_num == 1:
        # Mid-swing: keep full width to show extended saber
        return surface
    else:
        # Wind-up and follow-through: crop to standard size
        final = create_surface()
        final.blit(surface, (0, 0), (0, 0, 32, 48))
        return final


def create_hurt_frame():
    """Create hurt/damage frame - recoiling."""
    surface = create_surface()
    draw_bob_base(surface, leg_offset=-1, arm_offset=3, bob_y=1)
    add_outline(surface)
    return surface


def generate_sprite_sheet():
    """Generate the complete sprite sheet.

    Layout:
    - Row 0: Idle (2 frames, 32px each)
    - Row 1: Run (4 frames, 32px each)
    - Row 2: Jump, Fall, Hurt (32px each)
    - Row 3: Attack frame 0 (32px), Attack frame 1 (56px), Attack frame 2 (32px)

    Note: Attack frame 1 (mid-swing) is wider (56px) to show extended saber.
    """
    # Standard rows use 4 cols of 32px
    # Attack row: 32 + 56 + 32 = 120px wide
    attack_widths = [32, 56, 32]  # Width of each attack frame
    attack_row_width = sum(attack_widths)

    cols = 4
    rows = 4
    sheet_width = max(SPRITE_WIDTH * cols, attack_row_width)
    sheet_height = SPRITE_HEIGHT * rows

    sheet = pygame.Surface((sheet_width, sheet_height), pygame.SRCALPHA)
    sheet.fill(TRANSPARENT)

    # Row 0: Idle (2 frames)
    for i in range(2):
        frame = create_idle_frame(i)
        sheet.blit(frame, (i * SPRITE_WIDTH, 0))

    # Row 1: Run (4 frames)
    for i in range(4):
        frame = create_run_frame(i)
        sheet.blit(frame, (i * SPRITE_WIDTH, SPRITE_HEIGHT))

    # Row 2: Jump, Fall, Hurt
    sheet.blit(create_jump_frame(), (0, SPRITE_HEIGHT * 2))
    sheet.blit(create_fall_frame(), (SPRITE_WIDTH, SPRITE_HEIGHT * 2))
    sheet.blit(create_hurt_frame(), (SPRITE_WIDTH * 2, SPRITE_HEIGHT * 2))

    # Row 3: Attack (3 frames with variable widths)
    x_offset = 0
    for i in range(3):
        frame = create_attack_frame(i)
        sheet.blit(frame, (x_offset, SPRITE_HEIGHT * 3))
        x_offset += attack_widths[i]

    return sheet


def main():
    """Generate and save the sprite sheet."""
    print("Generating Captain Bob sprite sheet...")

    sheet = generate_sprite_sheet()

    output_path = "assets/sprites/player.png"
    pygame.image.save(sheet, output_path)
    print(f"Saved sprite sheet to {output_path}")
    print(f"Size: {sheet.get_width()}x{sheet.get_height()} pixels")
    print("Layout:")
    print("  Row 0: Idle (2 frames)")
    print("  Row 1: Run (4 frames)")
    print("  Row 2: Jump, Fall, Hurt")
    print("  Row 3: Attack (3 frames)")

    pygame.quit()


if __name__ == "__main__":
    main()
