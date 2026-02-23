#!/usr/bin/env python3
"""
Generate NES-style 8-bit collectible sprites for Bob the Pirate.

Sprites generated:
  - Treasure chest (32x24) - closed
  - Gold coin (16x16) - 4 frame spinning animation
  - Rum bottle (12x20)
  - Pirate flag (24x32)
  - Loot/golden chest (32x24)
  - Exit door locked (32x64)
  - Exit door unlocked (32x64)

Output: assets/collectibles/collectibles.png
"""

import os

import pygame

# Initialize pygame
pygame.init()

# Color palette (NES-inspired, pirate theme)
TRANSPARENT = (0, 0, 0, 0)
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)

# Treasure chest colors
CHEST_WOOD_DARK = (100, 60, 30, 255)
CHEST_WOOD_MID = (140, 90, 50, 255)
CHEST_WOOD_LIGHT = (180, 120, 70, 255)
CHEST_METAL = (70, 70, 80, 255)
CHEST_METAL_LIGHT = (100, 100, 110, 255)

# Golden chest colors (loot chest)
GOLD_DARK = (180, 140, 0, 255)
GOLD_MID = (220, 180, 0, 255)
GOLD_LIGHT = (255, 220, 80, 255)
GOLD_SHINE = (255, 255, 200, 255)

# Coin colors
COIN_DARK = (180, 140, 0, 255)
COIN_MID = (220, 180, 20, 255)
COIN_LIGHT = (255, 220, 80, 255)
COIN_SHINE = (255, 255, 180, 255)

# Rum bottle colors
BOTTLE_DARK = (80, 50, 30, 255)
BOTTLE_MID = (120, 75, 45, 255)
BOTTLE_LIGHT = (150, 100, 60, 255)
RUM_COLOR = (140, 80, 40, 255)
CORK_COLOR = (180, 160, 140, 255)
LABEL_COLOR = (220, 200, 160, 255)

# Pirate flag colors
FLAG_BLACK = (20, 20, 25, 255)
FLAG_DARK = (40, 40, 45, 255)
FLAG_BONE = (220, 210, 190, 255)
POLE_BROWN = (100, 70, 40, 255)
POLE_DARK = (70, 50, 30, 255)

# Exit door colors
DOOR_WOOD = (100, 70, 45, 255)
DOOR_DARK = (70, 50, 30, 255)
DOOR_FRAME = (60, 45, 30, 255)
DOOR_METAL = (80, 80, 90, 255)
DOOR_LOCK = (180, 160, 60, 255)  # Locked = brass
DOOR_UNLOCK_GLOW = (100, 220, 100, 255)  # Unlocked = green glow


def create_surface(width, height):
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
# TREASURE CHEST (32x24)
# =============================================================================

def create_treasure_chest():
    """Create a wooden treasure chest sprite."""
    surface = create_surface(32, 24)

    # Main body (wooden box)
    draw_rect(surface, 2, 8, 28, 14, CHEST_WOOD_MID)

    # Top darker for depth
    draw_rect(surface, 2, 8, 28, 3, CHEST_WOOD_LIGHT)

    # Bottom shadow
    draw_rect(surface, 2, 19, 28, 3, CHEST_WOOD_DARK)

    # Lid (curved top appearance)
    draw_rect(surface, 2, 2, 28, 6, CHEST_WOOD_MID)
    draw_rect(surface, 4, 0, 24, 2, CHEST_WOOD_MID)
    draw_rect(surface, 4, 0, 24, 1, CHEST_WOOD_LIGHT)

    # Wood grain lines
    for x in [8, 16, 24]:
        draw_line_v(surface, x, 8, 14, CHEST_WOOD_DARK)

    # Metal bands
    draw_rect(surface, 0, 6, 32, 3, CHEST_METAL)
    draw_line_h(surface, 0, 6, 32, CHEST_METAL_LIGHT)
    draw_rect(surface, 0, 16, 32, 2, CHEST_METAL)
    draw_line_h(surface, 0, 16, 32, CHEST_METAL_LIGHT)

    # Front lock/clasp
    draw_rect(surface, 13, 9, 6, 8, CHEST_METAL)
    draw_rect(surface, 14, 10, 4, 6, CHEST_METAL_LIGHT)
    draw_rect(surface, 15, 13, 2, 2, CHEST_WOOD_DARK)  # Keyhole

    # Corner rivets
    for corner_x in [4, 26]:
        draw_rect(surface, corner_x, 7, 2, 2, CHEST_METAL_LIGHT)
        draw_rect(surface, corner_x, 17, 2, 2, CHEST_METAL_LIGHT)

    # Black outline
    # Top curve
    draw_line_h(surface, 4, 0, 24, BLACK)
    draw_pixel(surface, 3, 1, BLACK)
    draw_pixel(surface, 28, 1, BLACK)
    draw_line_v(surface, 2, 2, 6, BLACK)
    draw_line_v(surface, 29, 2, 6, BLACK)
    # Main body outline
    draw_line_v(surface, 1, 8, 14, BLACK)
    draw_line_v(surface, 30, 8, 14, BLACK)
    draw_line_h(surface, 2, 22, 28, BLACK)

    return surface


# =============================================================================
# GOLD COIN (16x16) - 4 frame spinning animation
# =============================================================================

def create_coin_frame_1():
    """Coin face-on (widest)."""
    surface = create_surface(16, 16)

    # Circle shape with coin face
    # Outer edge
    draw_rect(surface, 4, 1, 8, 1, COIN_DARK)
    draw_rect(surface, 2, 2, 12, 1, COIN_DARK)
    draw_rect(surface, 1, 3, 14, 1, COIN_MID)
    draw_rect(surface, 1, 4, 14, 8, COIN_MID)
    draw_rect(surface, 1, 12, 14, 1, COIN_MID)
    draw_rect(surface, 2, 13, 12, 1, COIN_DARK)
    draw_rect(surface, 4, 14, 8, 1, COIN_DARK)

    # Highlight on top-left
    draw_line_h(surface, 4, 2, 5, COIN_LIGHT)
    draw_line_h(surface, 2, 3, 4, COIN_LIGHT)
    draw_line_v(surface, 2, 4, 3, COIN_LIGHT)
    draw_pixel(surface, 3, 3, COIN_SHINE)

    # Skull emblem (simplified)
    draw_rect(surface, 5, 5, 6, 4, COIN_LIGHT)  # Skull
    draw_rect(surface, 6, 4, 4, 1, COIN_LIGHT)  # Top of head
    draw_pixel(surface, 6, 6, COIN_DARK)  # Left eye
    draw_pixel(surface, 9, 6, COIN_DARK)  # Right eye
    draw_rect(surface, 7, 9, 2, 2, COIN_LIGHT)  # Jaw

    # Shadow on bottom-right
    draw_line_v(surface, 13, 5, 6, COIN_DARK)
    draw_line_h(surface, 5, 12, 7, COIN_DARK)

    return surface


def create_coin_frame_2():
    """Coin at 60 degree angle (narrower)."""
    surface = create_surface(16, 16)

    # Narrower ellipse
    draw_rect(surface, 5, 1, 6, 1, COIN_DARK)
    draw_rect(surface, 4, 2, 8, 1, COIN_DARK)
    draw_rect(surface, 3, 3, 10, 1, COIN_MID)
    draw_rect(surface, 3, 4, 10, 8, COIN_MID)
    draw_rect(surface, 3, 12, 10, 1, COIN_MID)
    draw_rect(surface, 4, 13, 8, 1, COIN_DARK)
    draw_rect(surface, 5, 14, 6, 1, COIN_DARK)

    # Highlight
    draw_line_h(surface, 5, 2, 4, COIN_LIGHT)
    draw_line_h(surface, 4, 3, 3, COIN_LIGHT)
    draw_pixel(surface, 4, 4, COIN_LIGHT)
    draw_pixel(surface, 5, 3, COIN_SHINE)

    # Simple skull marks
    draw_rect(surface, 6, 6, 4, 3, COIN_LIGHT)
    draw_pixel(surface, 6, 7, COIN_DARK)
    draw_pixel(surface, 9, 7, COIN_DARK)

    # Shadow
    draw_line_v(surface, 11, 5, 5, COIN_DARK)

    return surface


def create_coin_frame_3():
    """Coin edge-on (thinnest)."""
    surface = create_surface(16, 16)

    # Very thin edge view
    draw_rect(surface, 7, 1, 2, 1, COIN_DARK)
    draw_rect(surface, 6, 2, 4, 1, COIN_DARK)
    draw_rect(surface, 6, 3, 4, 10, COIN_MID)
    draw_rect(surface, 6, 13, 4, 1, COIN_DARK)
    draw_rect(surface, 7, 14, 2, 1, COIN_DARK)

    # Highlight on left edge
    draw_line_v(surface, 6, 3, 10, COIN_LIGHT)
    draw_pixel(surface, 6, 2, COIN_SHINE)

    # Shadow on right edge
    draw_line_v(surface, 9, 3, 10, COIN_DARK)

    return surface


def create_coin_frame_4():
    """Coin at -60 degree angle (back side)."""
    surface = create_surface(16, 16)

    # Same as frame 2 but mirrored highlight
    draw_rect(surface, 5, 1, 6, 1, COIN_DARK)
    draw_rect(surface, 4, 2, 8, 1, COIN_DARK)
    draw_rect(surface, 3, 3, 10, 1, COIN_MID)
    draw_rect(surface, 3, 4, 10, 8, COIN_MID)
    draw_rect(surface, 3, 12, 10, 1, COIN_MID)
    draw_rect(surface, 4, 13, 8, 1, COIN_DARK)
    draw_rect(surface, 5, 14, 6, 1, COIN_DARK)

    # Highlight on right side now (back of coin)
    draw_line_h(surface, 7, 2, 4, COIN_LIGHT)
    draw_line_h(surface, 9, 3, 3, COIN_LIGHT)
    draw_pixel(surface, 11, 4, COIN_LIGHT)
    draw_pixel(surface, 10, 3, COIN_SHINE)

    # Back design (simple cross pattern)
    draw_line_h(surface, 5, 7, 6, COIN_LIGHT)
    draw_line_v(surface, 7, 5, 6, COIN_LIGHT)

    # Shadow on left
    draw_line_v(surface, 4, 5, 5, COIN_DARK)

    return surface


# =============================================================================
# RUM BOTTLE (12x20)
# =============================================================================

def create_rum_bottle():
    """Create a rum bottle sprite."""
    surface = create_surface(12, 20)

    # Cork at top
    draw_rect(surface, 4, 0, 4, 3, CORK_COLOR)
    draw_line_v(surface, 4, 0, 3, BOTTLE_DARK)  # Shadow

    # Bottle neck
    draw_rect(surface, 4, 3, 4, 4, BOTTLE_MID)
    draw_line_v(surface, 4, 3, 4, BOTTLE_DARK)
    draw_line_v(surface, 7, 3, 4, BOTTLE_LIGHT)

    # Bottle body (wider)
    draw_rect(surface, 2, 7, 8, 11, BOTTLE_MID)

    # Rum liquid visible through glass
    draw_rect(surface, 3, 8, 6, 9, RUM_COLOR)

    # Glass highlights (left side shine)
    draw_line_v(surface, 2, 8, 9, BOTTLE_LIGHT)
    draw_line_v(surface, 3, 8, 2, (200, 200, 200, 255))

    # Glass shadow (right side)
    draw_line_v(surface, 9, 8, 9, BOTTLE_DARK)

    # Label
    draw_rect(surface, 3, 11, 6, 4, LABEL_COLOR)
    draw_rect(surface, 4, 12, 4, 2, BOTTLE_DARK)  # "XXX" simplified

    # Bottom of bottle
    draw_rect(surface, 2, 18, 8, 2, BOTTLE_DARK)
    draw_line_h(surface, 3, 19, 6, BOTTLE_MID)

    # Outline
    draw_pixel(surface, 3, 0, BLACK)
    draw_pixel(surface, 8, 0, BLACK)
    draw_line_v(surface, 3, 1, 2, BLACK)
    draw_line_v(surface, 8, 1, 2, BLACK)
    draw_line_v(surface, 3, 3, 4, BLACK)
    draw_line_v(surface, 8, 3, 4, BLACK)
    draw_pixel(surface, 2, 7, BLACK)
    draw_pixel(surface, 9, 7, BLACK)
    draw_line_v(surface, 1, 8, 10, BLACK)
    draw_line_v(surface, 10, 8, 10, BLACK)
    draw_line_h(surface, 2, 18, 8, BLACK)

    return surface


# =============================================================================
# PIRATE FLAG (24x32)
# =============================================================================

def create_pirate_flag():
    """Create a pirate flag (skull and crossbones) on a pole."""
    surface = create_surface(24, 32)

    # Flag pole (on the right side)
    draw_rect(surface, 20, 0, 3, 32, POLE_BROWN)
    draw_line_v(surface, 20, 0, 32, POLE_DARK)  # Shadow
    draw_line_v(surface, 22, 0, 32, POLE_BROWN)  # Highlight

    # Pole top ornament
    draw_rect(surface, 19, 0, 5, 3, POLE_DARK)
    draw_rect(surface, 20, 0, 3, 2, POLE_BROWN)

    # Flag (black with some wave)
    # Wave shape - slightly curved
    for y in range(4, 26):
        wave_offset = 0
        if y < 10:
            wave_offset = 0
        elif y < 15:
            wave_offset = -1
        elif y < 20:
            wave_offset = 0
        else:
            wave_offset = 1

        x_start = 1 + wave_offset
        width = 18 - abs(wave_offset)

        for x in range(x_start, x_start + width):
            draw_pixel(surface, x, y, FLAG_BLACK)

    # Flag edge highlight (to show fabric)
    draw_line_v(surface, 1, 4, 6, FLAG_DARK)
    draw_line_v(surface, 0, 10, 5, FLAG_DARK)
    draw_line_v(surface, 1, 20, 6, FLAG_DARK)

    # Skull
    draw_rect(surface, 6, 8, 8, 6, FLAG_BONE)
    draw_rect(surface, 7, 7, 6, 1, FLAG_BONE)  # Top of skull
    draw_rect(surface, 8, 14, 4, 2, FLAG_BONE)  # Jaw

    # Eye sockets
    draw_rect(surface, 7, 10, 2, 2, FLAG_BLACK)
    draw_rect(surface, 11, 10, 2, 2, FLAG_BLACK)

    # Nose
    draw_pixel(surface, 9, 12, FLAG_BLACK)
    draw_pixel(surface, 10, 12, FLAG_BLACK)

    # Crossbones behind skull
    # Left bone going down-right
    for i in range(8):
        draw_pixel(surface, 3 + i, 9 + i, FLAG_BONE)
        draw_pixel(surface, 4 + i, 9 + i, FLAG_BONE)

    # Right bone going down-left
    for i in range(8):
        draw_pixel(surface, 16 - i, 9 + i, FLAG_BONE)
        draw_pixel(surface, 15 - i, 9 + i, FLAG_BONE)

    # Bone ends (knobs)
    draw_rect(surface, 2, 8, 2, 2, FLAG_BONE)
    draw_rect(surface, 16, 8, 2, 2, FLAG_BONE)
    draw_rect(surface, 2, 16, 2, 2, FLAG_BONE)
    draw_rect(surface, 16, 16, 2, 2, FLAG_BONE)

    return surface


# =============================================================================
# LOOT CHEST / GOLDEN CHEST (32x24)
# =============================================================================

def create_loot_chest():
    """Create a golden loot chest (contains power-ups)."""
    surface = create_surface(32, 24)

    # Main body (golden box)
    draw_rect(surface, 2, 8, 28, 14, GOLD_MID)

    # Top brighter
    draw_rect(surface, 2, 8, 28, 3, GOLD_LIGHT)

    # Bottom shadow
    draw_rect(surface, 2, 19, 28, 3, GOLD_DARK)

    # Lid (curved top appearance)
    draw_rect(surface, 2, 2, 28, 6, GOLD_MID)
    draw_rect(surface, 4, 0, 24, 2, GOLD_MID)
    draw_rect(surface, 4, 0, 24, 1, GOLD_LIGHT)

    # Shine effect on lid
    draw_rect(surface, 6, 1, 4, 1, GOLD_SHINE)
    draw_rect(surface, 5, 2, 3, 1, GOLD_SHINE)

    # Decorative patterns
    for x in [8, 16, 24]:
        draw_line_v(surface, x, 8, 14, GOLD_DARK)

    # Ornate metal bands (whiter/shinier)
    draw_rect(surface, 0, 6, 32, 3, GOLD_LIGHT)
    draw_line_h(surface, 0, 6, 32, GOLD_SHINE)
    draw_rect(surface, 0, 16, 32, 2, GOLD_LIGHT)
    draw_line_h(surface, 0, 16, 32, GOLD_SHINE)

    # Front jeweled clasp
    draw_rect(surface, 12, 9, 8, 8, GOLD_LIGHT)
    draw_rect(surface, 13, 10, 6, 6, (200, 50, 50, 255))  # Ruby red gem
    draw_rect(surface, 14, 11, 2, 2, (255, 150, 150, 255))  # Gem highlight

    # Corner decorations
    for corner_x in [3, 26]:
        draw_rect(surface, corner_x, 7, 3, 3, GOLD_SHINE)
        draw_rect(surface, corner_x, 17, 3, 3, GOLD_SHINE)

    # Black outline
    draw_line_h(surface, 4, 0, 24, BLACK)
    draw_pixel(surface, 3, 1, BLACK)
    draw_pixel(surface, 28, 1, BLACK)
    draw_line_v(surface, 2, 2, 6, BLACK)
    draw_line_v(surface, 29, 2, 6, BLACK)
    draw_line_v(surface, 1, 8, 14, BLACK)
    draw_line_v(surface, 30, 8, 14, BLACK)
    draw_line_h(surface, 2, 22, 28, BLACK)

    return surface


# =============================================================================
# EXIT DOOR LOCKED (32x64)
# =============================================================================

def create_exit_door_locked():
    """Create a locked exit door (tall wooden door)."""
    surface = create_surface(32, 64)

    # Door frame (dark outline)
    draw_rect(surface, 0, 0, 32, 64, DOOR_FRAME)

    # Main door (wooden)
    draw_rect(surface, 3, 3, 26, 58, DOOR_WOOD)

    # Wood grain / planks
    for y in [12, 24, 36, 48]:
        draw_line_h(surface, 3, y, 26, DOOR_DARK)

    # Vertical plank divisions
    draw_line_v(surface, 10, 3, 58, DOOR_DARK)
    draw_line_v(surface, 21, 3, 58, DOOR_DARK)

    # Metal reinforcement bands
    draw_rect(surface, 3, 8, 26, 3, DOOR_METAL)
    draw_rect(surface, 3, 30, 26, 3, DOOR_METAL)
    draw_rect(surface, 3, 52, 26, 3, DOOR_METAL)

    # Door handle
    draw_rect(surface, 22, 32, 4, 6, DOOR_METAL)
    draw_rect(surface, 23, 33, 2, 4, (100, 100, 110, 255))

    # Lock (prominent when locked)
    draw_rect(surface, 12, 28, 8, 10, DOOR_LOCK)
    draw_rect(surface, 13, 29, 6, 8, (150, 130, 50, 255))
    draw_rect(surface, 15, 32, 2, 3, DOOR_DARK)  # Keyhole

    # "X" chains over door to show locked
    for i in range(10):
        draw_pixel(surface, 5 + i * 2, 15 + i * 3, DOOR_METAL)
        draw_pixel(surface, 6 + i * 2, 15 + i * 3, DOOR_METAL)
        draw_pixel(surface, 25 - i * 2, 15 + i * 3, DOOR_METAL)
        draw_pixel(surface, 26 - i * 2, 15 + i * 3, DOOR_METAL)

    # Black outline
    draw_line_v(surface, 0, 0, 64, BLACK)
    draw_line_v(surface, 31, 0, 64, BLACK)
    draw_line_h(surface, 0, 0, 32, BLACK)
    draw_line_h(surface, 0, 63, 32, BLACK)

    return surface


# =============================================================================
# EXIT DOOR UNLOCKED (32x64)
# =============================================================================

def create_exit_door_unlocked():
    """Create an unlocked exit door (glowing green)."""
    surface = create_surface(32, 64)

    # Door frame (dark outline)
    draw_rect(surface, 0, 0, 32, 64, DOOR_FRAME)

    # Main door (wooden with green tint)
    draw_rect(surface, 3, 3, 26, 58, (80, 100, 70, 255))

    # Green glow overlay
    draw_rect(surface, 4, 4, 24, 56, (60, 120, 60, 255))

    # Wood grain visible through glow
    for y in [12, 24, 36, 48]:
        draw_line_h(surface, 4, y, 24, (40, 80, 40, 255))

    draw_line_v(surface, 10, 4, 56, (40, 80, 40, 255))
    draw_line_v(surface, 21, 4, 56, (40, 80, 40, 255))

    # Bright green glow in center (beckoning)
    draw_rect(surface, 10, 20, 12, 24, DOOR_UNLOCK_GLOW)
    draw_rect(surface, 12, 22, 8, 20, (150, 255, 150, 255))
    draw_rect(surface, 14, 26, 4, 12, (200, 255, 200, 255))

    # Arrow pointing in (enter!)
    draw_rect(surface, 14, 30, 4, 8, WHITE)
    draw_rect(surface, 12, 34, 8, 2, WHITE)
    draw_pixel(surface, 10, 35, WHITE)
    draw_pixel(surface, 21, 35, WHITE)

    # Open padlock at side (showing it's unlocked)
    draw_rect(surface, 23, 28, 5, 8, (180, 180, 80, 255))
    draw_rect(surface, 24, 24, 3, 4, (180, 180, 80, 255))  # Shackle open

    # Black outline
    draw_line_v(surface, 0, 0, 64, BLACK)
    draw_line_v(surface, 31, 0, 64, BLACK)
    draw_line_h(surface, 0, 0, 32, BLACK)
    draw_line_h(surface, 0, 63, 32, BLACK)

    return surface


# =============================================================================
# SPRITE SHEET GENERATION
# =============================================================================

def generate_collectibles_sheet():
    """
    Generate the complete collectibles sprite sheet.

    Layout:
    Row 0 (y=0):   treasure_chest (32x24), coin_1 (16x16), coin_2 (16x16)
    Row 1 (y=24):  loot_chest (32x24), coin_3 (16x16), coin_4 (16x16)
    Row 2 (y=48):  rum_bottle (12x20), pirate_flag (24x32)
    Row 3 (y=80):  exit_door_locked (32x64) at x=0, exit_door_unlocked (32x64) at x=32

    Total size: 64x144 pixels
    """
    sheet_width = 64
    sheet_height = 144

    sheet = pygame.Surface((sheet_width, sheet_height), pygame.SRCALPHA)
    sheet.fill(TRANSPARENT)

    # Row 0: Treasure chest and coins 1-2
    sheet.blit(create_treasure_chest(), (0, 0))
    sheet.blit(create_coin_frame_1(), (32, 0))
    sheet.blit(create_coin_frame_2(), (48, 0))

    # Row 1: Loot chest and coins 3-4
    sheet.blit(create_loot_chest(), (0, 24))
    sheet.blit(create_coin_frame_3(), (32, 24))
    sheet.blit(create_coin_frame_4(), (48, 24))

    # Row 2: Rum bottle and pirate flag
    sheet.blit(create_rum_bottle(), (0, 48))
    sheet.blit(create_pirate_flag(), (12, 48))

    # Row 3: Exit doors
    sheet.blit(create_exit_door_locked(), (0, 80))
    sheet.blit(create_exit_door_unlocked(), (32, 80))

    return sheet


# Sprite index for easy reference
COLLECTIBLE_INDEX = {
    "treasure_chest": (0, 0, 32, 24),
    "coin_1": (32, 0, 16, 16),
    "coin_2": (48, 0, 16, 16),
    "loot_chest": (0, 24, 32, 24),
    "coin_3": (32, 24, 16, 16),
    "coin_4": (48, 24, 16, 16),
    "rum_bottle": (0, 48, 12, 20),
    "pirate_flag": (12, 48, 24, 32),
    "exit_door_locked": (0, 80, 32, 64),
    "exit_door_unlocked": (32, 80, 32, 64),
}


def main():
    """Generate and save the collectibles sprite sheet."""
    print("Generating collectibles sprite sheet...")

    # Ensure output directory exists
    output_dir = "assets/collectibles"
    os.makedirs(output_dir, exist_ok=True)

    sheet = generate_collectibles_sheet()

    output_path = os.path.join(output_dir, "collectibles.png")
    pygame.image.save(sheet, output_path)
    print(f"Saved collectibles to {output_path}")
    print(f"Size: {sheet.get_width()}x{sheet.get_height()} pixels")
    print("\nSprite layout:")
    print("  Row 0 (y=0):  treasure_chest (32x24), coin_1 (16x16), coin_2 (16x16)")
    print("  Row 1 (y=24): loot_chest (32x24), coin_3 (16x16), coin_4 (16x16)")
    print("  Row 2 (y=48): rum_bottle (12x20), pirate_flag (24x32)")
    print("  Row 3 (y=80): exit_door_locked (32x64), exit_door_unlocked (32x64)")
    print("\nSprite indices (x, y, width, height):")
    for name, bounds in COLLECTIBLE_INDEX.items():
        print(f"  {name}: {bounds}")

    pygame.quit()


if __name__ == "__main__":
    main()
