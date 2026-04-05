#!/usr/bin/env python3
"""
Generate NES-style 8-bit sprite sheet for Ghost Captain Bob skin.

This is a spectral/ghostly version of Captain Bob with:
- Blue-green ghostly coloring
- Semi-transparent appearance
- Flame attack instead of sword swing (arm extends, flames shoot out)

Sprite size: 32x48 pixels (same as player.png)
Animations:
  - Idle: 2 frames (row 0)
  - Run: 4 frames (row 1)
  - Jump: 1 frame (row 2, col 0)
  - Fall: 1 frame (row 2, col 1)
  - Hurt: 1 frame (row 2, col 2)
  - Flame Attack: 3 frames (row 3) - arm out, flames grow, flames full
  - Roll: 4 frames (row 4)
  - Slam: 3 frames (row 5)

Output: assets/sprites/ghost_captain.png
"""

import random

import pygame

# Initialize pygame
pygame.init()

# Sprite dimensions
SPRITE_WIDTH = 32
SPRITE_HEIGHT = 48

# Attack frame dimensions (wider to fit flames)
ATTACK_FRAME_WIDTH = 56

# Color palette - Ghostly blue-green spectral colors
TRANSPARENT = (0, 0, 0, 0)
BLACK = (20, 40, 50, 255)  # Dark ghostly outline

# Ghost skin tones (spectral blue-green)
GHOST_SKIN = (140, 200, 210, 220)  # Pale ghostly blue
GHOST_SKIN_SHADOW = (100, 160, 175, 200)  # Darker ghostly shadow

# Ghost clothing (tattered, faded)
GHOST_BANDANA = (80, 150, 170, 200)  # Faded blue bandana
GHOST_BANDANA_DARK = (60, 120, 140, 180)
GHOST_SHIRT = (160, 200, 210, 200)  # Pale ghostly shirt
GHOST_SHIRT_SHADOW = (120, 170, 185, 180)
GHOST_PANTS = (70, 130, 150, 200)  # Darker ghostly pants
GHOST_PANTS_DARK = (50, 100, 120, 180)
GHOST_BOOTS = (40, 80, 100, 200)  # Dark ghostly boots
GHOST_BOOTS_HIGHLIGHT = (60, 110, 130, 180)

# Ghost features
GHOST_GOATEE = (60, 100, 120, 180)  # Ghostly goatee
GHOST_EYE_GLOW = (150, 230, 255, 255)  # Glowing eyes
GHOST_EYE_CENTER = (200, 255, 255, 255)  # Bright eye center
GHOST_BELT = (100, 160, 180, 200)  # Ghostly belt

# Flame colors (blue-green spectral flames)
FLAME_CORE = (200, 255, 255, 255)  # Bright white-cyan core
FLAME_MID = (100, 220, 240, 240)  # Bright cyan
FLAME_OUTER = (60, 180, 200, 200)  # Outer cyan
FLAME_EDGE = (40, 140, 160, 150)  # Faded edge


def create_surface(width=SPRITE_WIDTH, height=SPRITE_HEIGHT):
    """Create a transparent surface for one sprite frame."""
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


def draw_ghost_bob_base(surface, leg_offset=0, arm_offset=0, bob_y=0, arm_extended=False):
    """
    Draw Ghost Captain Bob's base sprite (facing right).

    Args:
        surface: pygame Surface to draw on
        leg_offset: offset for leg animation (alternating legs)
        arm_offset: offset for arm position
        bob_y: vertical offset for breathing/jumping
        arm_extended: if True, draw arm extended forward for flame attack
    """
    y_off = bob_y

    # === HEAD (y: 4-16) ===
    # Bandana (top of head) - tattered ghostly
    draw_rect(surface, 10, 4 + y_off, 12, 5, GHOST_BANDANA)
    draw_rect(surface, 12, 5 + y_off, 8, 2, GHOST_BANDANA_DARK)
    # Bandana tail - tattered
    draw_rect(surface, 22, 6 + y_off, 4, 2, GHOST_BANDANA)
    draw_rect(surface, 24, 8 + y_off, 3, 2, GHOST_BANDANA_DARK)
    # Tattered edge effect
    draw_pixel(surface, 26, 9 + y_off, GHOST_BANDANA_DARK)

    # Face - ghostly
    draw_rect(surface, 10, 9 + y_off, 12, 9, GHOST_SKIN)
    draw_rect(surface, 10, 9 + y_off, 3, 7, GHOST_SKIN_SHADOW)

    # Glowing eyes
    draw_rect(surface, 17, 11 + y_off, 3, 3, GHOST_EYE_GLOW)
    draw_rect(surface, 18, 12 + y_off, 2, 2, GHOST_EYE_CENTER)

    # Nose shadow
    draw_rect(surface, 21, 13 + y_off, 2, 2, GHOST_SKIN_SHADOW)

    # Goatee - ghostly
    draw_rect(surface, 13, 15 + y_off, 6, 3, GHOST_GOATEE)
    draw_rect(surface, 14, 18 + y_off, 4, 1, GHOST_GOATEE)

    # === BODY (y: 18-30) ===
    # Shirt (torso) - ghostly, tattered
    draw_rect(surface, 6, 19 + y_off, 20, 10, GHOST_SHIRT)
    draw_rect(surface, 6, 19 + y_off, 5, 8, GHOST_SHIRT_SHADOW)

    # V-neck / chest
    draw_rect(surface, 14, 19 + y_off, 4, 2, GHOST_SKIN)

    # Belt
    draw_rect(surface, 6, 28 + y_off, 20, 3, GHOST_PANTS_DARK)
    draw_rect(surface, 14, 28 + y_off, 4, 3, GHOST_BELT)

    # === ARMS ===
    arm_y = 20 + y_off + arm_offset

    # Back arm (left, partially hidden)
    draw_rect(surface, 4, arm_y, 4, 8, GHOST_SHIRT_SHADOW)
    draw_rect(surface, 4, arm_y + 7, 4, 3, GHOST_SKIN_SHADOW)

    # Front arm (right) - extended for flame attack or normal
    if arm_extended:
        # Arm extended forward horizontally
        draw_rect(surface, 24, arm_y + 2, 8, 4, GHOST_SHIRT)
        draw_rect(surface, 30, arm_y + 2, 4, 4, GHOST_SKIN)  # Hand
    else:
        draw_rect(surface, 24, arm_y, 4, 8, GHOST_SHIRT)
        draw_rect(surface, 24, arm_y + 7, 4, 3, GHOST_SKIN)

    # === LEGS (y: 31-42) ===
    leg_base_y = 31 + y_off

    # Left leg
    left_y = leg_base_y + leg_offset
    draw_rect(surface, 8, left_y, 6, 8, GHOST_PANTS)
    draw_rect(surface, 8, left_y, 2, 7, GHOST_PANTS_DARK)

    # Right leg
    right_y = leg_base_y - leg_offset
    draw_rect(surface, 18, right_y, 6, 8, GHOST_PANTS)
    draw_rect(surface, 18, right_y, 2, 7, GHOST_PANTS_DARK)

    # === BOOTS (y: 39-47) ===
    left_boot_y = 39 + y_off + leg_offset
    if left_boot_y < SPRITE_HEIGHT - 5:
        draw_rect(surface, 6, left_boot_y, 9, 6, GHOST_BOOTS)
        draw_rect(surface, 8, left_boot_y + 1, 4, 2, GHOST_BOOTS_HIGHLIGHT)

    right_boot_y = 39 + y_off - leg_offset
    if right_boot_y < SPRITE_HEIGHT - 5:
        draw_rect(surface, 17, right_boot_y, 9, 6, GHOST_BOOTS)
        draw_rect(surface, 19, right_boot_y + 1, 4, 2, GHOST_BOOTS_HIGHLIGHT)


def add_ghost_outline(surface):
    """Add a ghostly outline around non-transparent pixels."""
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


def draw_flame(surface, x, y, size, intensity):
    """
    Draw a single flame wisp.

    Args:
        surface: Surface to draw on
        x, y: Base position of flame
        size: Size multiplier (1.0 = normal)
        intensity: 0.0 to 1.0, affects brightness and alpha
    """
    # Flame shape - wider at bottom, pointed at top
    flame_height = int(12 * size)
    flame_width = int(6 * size)

    for row in range(flame_height):
        # Width narrows as we go up
        progress = row / flame_height
        row_width = int(flame_width * (1.0 - progress * 0.7))

        for col in range(-row_width // 2, row_width // 2 + 1):
            px = x + col
            py = y - row

            # Color based on distance from center and height
            dist_from_center = abs(col) / (row_width / 2 + 0.1)

            if dist_from_center < 0.3 and progress < 0.6:
                color = FLAME_CORE
            elif dist_from_center < 0.5 and progress < 0.7:
                color = FLAME_MID
            elif dist_from_center < 0.8:
                color = FLAME_OUTER
            else:
                color = FLAME_EDGE

            # Adjust alpha based on intensity and position
            alpha = int(color[3] * intensity * (1.0 - progress * 0.5))
            final_color = (color[0], color[1], color[2], alpha)

            draw_pixel(surface, px, py, final_color)


def draw_flame_blast(surface, start_x, y, frame):
    """
    Draw the flame blast attack.

    All frames are full-size flames, just with slight variation for animation.

    Args:
        surface: Surface to draw on
        start_x: X position where flames start (from hand)
        y: Y center position
        frame: 0, 1, 2 - all full size, with slight position variation
    """
    random.seed(42 + frame)  # Consistent randomness per frame

    # All frames have full-size flames, just with different random offsets
    # for visual variation
    for i in range(7):
        # Offset positions slightly differently per frame for animation effect
        fx = start_x + i * 4 + random.randint(-2, 2)
        fy = y + random.randint(-4, 4)
        size = 0.8 + random.uniform(0, 0.4)
        draw_flame(surface, fx, fy, size, 0.9)

    # Extra bright core flames (positioned differently per frame)
    for i in range(3):
        offset = (frame * 2) % 4  # Shifts core flames slightly per frame
        fx = start_x + 4 + i * 6 + offset
        draw_flame(surface, fx, y, 1.0, 1.0)


def create_idle_frame(frame_num):
    """Create idle animation frame (breathing motion)."""
    surface = create_surface()
    bob = 2 if frame_num == 1 else 0
    arm_bob = 1 if frame_num == 1 else 0
    draw_ghost_bob_base(surface, leg_offset=0, arm_offset=arm_bob, bob_y=bob)
    add_ghost_outline(surface)
    return surface


def create_run_frame(frame_num):
    """Create run animation frame."""
    surface = create_surface()
    leg_offsets = [0, 5, 0, -5]
    arm_offsets = [0, -3, 0, 3]
    bob_offsets = [0, -1, 0, -1]
    draw_ghost_bob_base(surface, leg_offset=leg_offsets[frame_num],
                        arm_offset=arm_offsets[frame_num], bob_y=bob_offsets[frame_num])
    add_ghost_outline(surface)
    return surface


def create_jump_frame():
    """Create jump (rising) frame."""
    surface = create_surface()
    draw_ghost_bob_base(surface, leg_offset=-2, arm_offset=-3, bob_y=-2)
    add_ghost_outline(surface)
    return surface


def create_fall_frame():
    """Create fall (descending) frame."""
    surface = create_surface()
    draw_ghost_bob_base(surface, leg_offset=2, arm_offset=2, bob_y=0)
    add_ghost_outline(surface)
    return surface


def create_hurt_frame():
    """Create hurt/damage frame."""
    surface = create_surface()
    draw_ghost_bob_base(surface, leg_offset=-1, arm_offset=3, bob_y=1)
    add_ghost_outline(surface)
    return surface


def create_flame_attack_frame(frame_num):
    """
    Create flame attack animation frame.

    Frame 0: Arm extends, small flames appear
    Frame 1: Flames grow larger
    Frame 2: Full flame blast
    """
    # Use wider surface for attack to fit flames
    surface = create_surface(ATTACK_FRAME_WIDTH, SPRITE_HEIGHT)

    # Draw Ghost Bob with arm extended
    bob_surface = create_surface()
    draw_ghost_bob_base(bob_surface, leg_offset=0, arm_offset=0, arm_extended=True)
    surface.blit(bob_surface, (0, 0))

    # Draw flames starting from hand position
    flame_start_x = 34  # Just past the extended hand
    flame_y = 24  # Roughly arm height

    draw_flame_blast(surface, flame_start_x, flame_y, frame_num)

    add_ghost_outline(surface)

    # For frame 0, we can crop to standard width since flames are small
    # For frames 1 and 2, keep full width
    if frame_num == 0:
        final = create_surface()
        final.blit(surface, (0, 0), (0, 0, 32, 48))
        return final
    else:
        return surface


def create_roll_frame(frame_num):
    """Create roll animation frame (spinning)."""
    surface = create_surface()

    # Roll is a spinning motion - draw Bob at different rotation angles
    # Since we're doing pixel art, we approximate with different poses
    y_off = 4  # Lowered during roll

    if frame_num == 0:
        # Starting roll - crouched
        draw_rect(surface, 8, 20 + y_off, 16, 12, GHOST_SHIRT)
        draw_rect(surface, 10, 16 + y_off, 12, 6, GHOST_BANDANA)
        draw_rect(surface, 8, 32 + y_off, 16, 8, GHOST_PANTS)
    elif frame_num == 1:
        # Mid roll - ball shape
        draw_rect(surface, 6, 18 + y_off, 20, 16, GHOST_SHIRT)
        draw_rect(surface, 8, 14 + y_off, 16, 6, GHOST_BANDANA)
        draw_rect(surface, 8, 34 + y_off, 16, 6, GHOST_BOOTS)
    elif frame_num == 2:
        # Inverted - feet up
        draw_rect(surface, 8, 22 + y_off, 16, 12, GHOST_PANTS)
        draw_rect(surface, 6, 14 + y_off, 20, 10, GHOST_SHIRT)
        draw_rect(surface, 10, 10 + y_off, 12, 6, GHOST_BOOTS)
    else:
        # Coming out of roll
        draw_rect(surface, 8, 18 + y_off, 16, 14, GHOST_SHIRT)
        draw_rect(surface, 10, 14 + y_off, 12, 6, GHOST_BANDANA)
        draw_rect(surface, 8, 32 + y_off, 16, 8, GHOST_PANTS)

    add_ghost_outline(surface)
    return surface


def create_slam_frame(frame_num):
    """Create anchor slam animation frame."""
    surface = create_surface()

    if frame_num == 0:
        # Wind up - arms raised
        draw_ghost_bob_base(surface, leg_offset=0, arm_offset=-5, bob_y=-2)
    elif frame_num == 1:
        # Mid slam - diving down
        draw_ghost_bob_base(surface, leg_offset=-3, arm_offset=2, bob_y=2)
    else:
        # Impact - crouched, arms down
        draw_ghost_bob_base(surface, leg_offset=2, arm_offset=4, bob_y=4)

    add_ghost_outline(surface)
    return surface


def generate_sprite_sheet():
    """
    Generate the complete Ghost Captain sprite sheet.

    Layout (same as player.png):
    - Row 0: Idle (2 frames, 32px each)
    - Row 1: Run (4 frames, 32px each)
    - Row 2: Jump, Fall, Hurt (32px each)
    - Row 3: Flame Attack frame 0 (32px), frame 1 (56px), frame 2 (56px)
    - Row 4: Roll (4 frames, 32px each)
    - Row 5: Slam (3 frames, 32px each)
    """
    attack_widths = [32, 56, 56]  # Wider frames for flame attack
    attack_row_width = sum(attack_widths)

    cols = 4
    rows = 6
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

    # Row 3: Flame Attack (3 frames with variable widths)
    x_offset = 0
    for i in range(3):
        frame = create_flame_attack_frame(i)
        sheet.blit(frame, (x_offset, SPRITE_HEIGHT * 3))
        x_offset += attack_widths[i]

    # Row 4: Roll (4 frames)
    for i in range(4):
        frame = create_roll_frame(i)
        sheet.blit(frame, (i * SPRITE_WIDTH, SPRITE_HEIGHT * 4))

    # Row 5: Slam (3 frames)
    for i in range(3):
        frame = create_slam_frame(i)
        sheet.blit(frame, (i * SPRITE_WIDTH, SPRITE_HEIGHT * 5))

    return sheet


def main():
    """Generate and save the sprite sheet."""
    print("Generating Ghost Captain sprite sheet...")

    sheet = generate_sprite_sheet()

    output_path = "assets/sprites/ghost_captain.png"
    pygame.image.save(sheet, output_path)
    print(f"Saved sprite sheet to {output_path}")
    print(f"Size: {sheet.get_width()}x{sheet.get_height()} pixels")
    print("Layout:")
    print("  Row 0: Idle (2 frames)")
    print("  Row 1: Run (4 frames)")
    print("  Row 2: Jump, Fall, Hurt")
    print("  Row 3: Flame Attack (3 frames)")
    print("  Row 4: Roll (4 frames)")
    print("  Row 5: Slam (3 frames)")

    pygame.quit()


if __name__ == "__main__":
    main()
