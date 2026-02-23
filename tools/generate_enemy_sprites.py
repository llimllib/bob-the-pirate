#!/usr/bin/env python3
"""
Generate NES-style 8-bit sprite sheets for British naval enemies.

Sprites (scaled up from original sizes):
  - Sailor (36x56): walk (2 frames), hurt (1 frame)
  - Musketeer (36x56): idle (1 frame), shooting (2 frames)
  - Officer (40x60): walk (2 frames), attack (2 frames)
  - Cannon (40x40): static (1 frame), firing (2 frames)
  - Projectiles: musket_ball (8x8), cannonball (12x12), admiral_bullet (10x10)

Output: assets/sprites/enemies.png (combined sheet)
        assets/sprites/projectiles.png
"""

import pygame

# Initialize pygame
pygame.init()

# Scale factor for larger enemies
SCALE_FACTOR = 1.3  # ~30% larger

# ============== COMMON COLORS ==============
TRANSPARENT = (0, 0, 0, 0)
BLACK = (0, 0, 0, 255)

# Skin tones
SKIN = (228, 180, 140, 255)
SKIN_SHADOW = (180, 130, 100, 255)

# British Navy uniform colors
NAVY_BLUE = (25, 50, 120, 255)
NAVY_DARK = (15, 30, 80, 255)
NAVY_LIGHT = (45, 70, 150, 255)
WHITE_TRIM = (240, 240, 235, 255)
WHITE_SHADOW = (200, 200, 195, 255)
GOLD_TRIM = (255, 215, 0, 255)
GOLD_DARK = (180, 150, 0, 255)

# Pants/boots
PANTS_WHITE = (235, 235, 230, 255)
PANTS_SHADOW = (190, 190, 185, 255)
BOOTS_BLACK = (35, 35, 40, 255)
BOOTS_HIGHLIGHT = (65, 65, 70, 255)

# Hat colors
HAT_BLUE = (20, 40, 100, 255)
HAT_DARK = (10, 25, 70, 255)

# Weapons
MUSKET_WOOD = (101, 67, 33, 255)
MUSKET_WOOD_DARK = (70, 45, 20, 255)
MUSKET_METAL = (80, 80, 90, 255)
MUSKET_METAL_LIGHT = (120, 120, 130, 255)
SWORD_SILVER = (220, 220, 230, 255)
SWORD_EDGE = (255, 255, 255, 255)
SWORD_DARK = (150, 150, 165, 255)
SWORD_HANDLE = (101, 67, 33, 255)

# Cannon
CANNON_METAL = (60, 60, 65, 255)
CANNON_DARK = (35, 35, 40, 255)
CANNON_HIGHLIGHT = (90, 90, 95, 255)
CANNON_WHEEL = (80, 50, 25, 255)
CANNON_WHEEL_DARK = (55, 35, 15, 255)
FIRE_ORANGE = (255, 150, 50, 255)
FIRE_YELLOW = (255, 220, 100, 255)
SMOKE_GRAY = (180, 180, 180, 255)

# Projectiles
MUSKET_BALL_GRAY = (200, 200, 200, 255)
CANNONBALL_DARK = (40, 40, 45, 255)
CANNONBALL_HIGHLIGHT = (70, 70, 75, 255)
ADMIRAL_BULLET_GOLD = (200, 150, 50, 255)

# Eyes
EYE_WHITE = (255, 255, 255, 255)
EYE_BLACK = (20, 20, 20, 255)


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


def scale_surface(surface, new_width, new_height):
    """Scale a surface to new dimensions using nearest-neighbor scaling."""
    return pygame.transform.scale(surface, (new_width, new_height))


# ============== SAILOR (36x56 final, drawn at 28x44 then scaled) ==============
SAILOR_DRAW_WIDTH = 28
SAILOR_DRAW_HEIGHT = 44
SAILOR_WIDTH = 36
SAILOR_HEIGHT = 56


def draw_sailor_base(surface, leg_offset=0, arm_offset=0, hurt=False):
    """Draw a basic sailor facing right."""
    # Head position
    head_x = 8
    head_y = 2

    # === SAILOR CAP ===
    draw_rect(surface, head_x + 2, head_y, 10, 4, NAVY_BLUE)
    draw_rect(surface, head_x, head_y + 3, 14, 2, NAVY_DARK)  # Cap brim

    # === FACE ===
    draw_rect(surface, head_x + 2, head_y + 5, 10, 8, SKIN)
    draw_rect(surface, head_x + 2, head_y + 5, 3, 6, SKIN_SHADOW)  # Shadow

    # Eye
    if not hurt:
        draw_rect(surface, head_x + 8, head_y + 7, 2, 2, EYE_WHITE)
        draw_pixel(surface, head_x + 9, head_y + 8, EYE_BLACK)
    else:
        # X eyes when hurt
        draw_pixel(surface, head_x + 8, head_y + 7, BLACK)
        draw_pixel(surface, head_x + 10, head_y + 9, BLACK)
        draw_pixel(surface, head_x + 8, head_y + 9, BLACK)
        draw_pixel(surface, head_x + 10, head_y + 7, BLACK)

    # === TORSO (simple navy shirt) ===
    torso_y = head_y + 13
    draw_rect(surface, 5, torso_y, 18, 10, NAVY_BLUE)
    draw_rect(surface, 5, torso_y, 4, 8, NAVY_DARK)  # Shadow
    # White collar
    draw_rect(surface, 11, torso_y, 6, 2, WHITE_TRIM)

    # === ARMS ===
    arm_y = torso_y + 1 + arm_offset
    # Back arm
    draw_rect(surface, 3, arm_y, 3, 7, NAVY_DARK)
    draw_rect(surface, 3, arm_y + 6, 3, 2, SKIN_SHADOW)
    # Front arm
    draw_rect(surface, 22, arm_y, 3, 7, NAVY_BLUE)
    draw_rect(surface, 22, arm_y + 6, 3, 2, SKIN)

    # === PANTS ===
    pants_y = torso_y + 10
    # Left leg
    draw_rect(surface, 7, pants_y + leg_offset, 5, 7, PANTS_WHITE)
    draw_rect(surface, 7, pants_y + leg_offset, 2, 6, PANTS_SHADOW)
    # Right leg
    draw_rect(surface, 16, pants_y - leg_offset, 5, 7, PANTS_WHITE)
    draw_rect(surface, 16, pants_y - leg_offset, 2, 6, PANTS_SHADOW)

    # === BOOTS ===
    boot_y = pants_y + 7
    # Left boot
    draw_rect(surface, 5, boot_y + leg_offset, 8, 5, BOOTS_BLACK)
    draw_rect(surface, 7, boot_y + leg_offset + 1, 3, 2, BOOTS_HIGHLIGHT)
    # Right boot
    draw_rect(surface, 15, boot_y - leg_offset, 8, 5, BOOTS_BLACK)
    draw_rect(surface, 17, boot_y - leg_offset + 1, 3, 2, BOOTS_HIGHLIGHT)


def create_sailor_walk_frame(frame_num):
    """Create sailor walk frame."""
    # Draw at original size
    surface = pygame.Surface((SAILOR_DRAW_WIDTH, SAILOR_DRAW_HEIGHT), pygame.SRCALPHA)
    surface.fill(TRANSPARENT)
    leg_offset = 3 if frame_num == 0 else -3
    arm_offset = -2 if frame_num == 0 else 2
    draw_sailor_base(surface, leg_offset=leg_offset, arm_offset=arm_offset)
    add_outline(surface)
    # Scale up to final size
    return scale_surface(surface, SAILOR_WIDTH, SAILOR_HEIGHT)


def create_sailor_hurt_frame():
    """Create sailor hurt frame."""
    # Draw at original size
    surface = pygame.Surface((SAILOR_DRAW_WIDTH, SAILOR_DRAW_HEIGHT), pygame.SRCALPHA)
    surface.fill(TRANSPARENT)
    draw_sailor_base(surface, leg_offset=0, arm_offset=2, hurt=True)
    add_outline(surface)
    # Scale up to final size
    return scale_surface(surface, SAILOR_WIDTH, SAILOR_HEIGHT)


# ============== MUSKETEER (36x56 final, drawn at 28x44 then scaled) ==============
MUSKETEER_DRAW_WIDTH = 28
MUSKETEER_DRAW_HEIGHT = 44
MUSKETEER_WIDTH = 36
MUSKETEER_HEIGHT = 56


def draw_musketeer_base(surface, shooting=False, shot_frame=0):
    """Draw a musketeer facing right."""
    head_x = 8
    head_y = 2

    # === TRICORN HAT ===
    # Main hat body
    draw_rect(surface, head_x, head_y, 14, 4, HAT_BLUE)
    draw_rect(surface, head_x - 2, head_y + 3, 18, 2, HAT_DARK)  # Brim
    # Upturned sides (tricorn style)
    draw_rect(surface, head_x - 2, head_y + 1, 3, 3, HAT_BLUE)
    draw_rect(surface, head_x + 13, head_y + 1, 3, 3, HAT_BLUE)

    # === FACE ===
    draw_rect(surface, head_x + 2, head_y + 5, 10, 8, SKIN)
    draw_rect(surface, head_x + 2, head_y + 5, 3, 6, SKIN_SHADOW)

    # Eye (squinting if shooting)
    if shooting:
        draw_rect(surface, head_x + 8, head_y + 8, 3, 1, EYE_BLACK)
    else:
        draw_rect(surface, head_x + 8, head_y + 7, 2, 2, EYE_WHITE)
        draw_pixel(surface, head_x + 9, head_y + 8, EYE_BLACK)

    # === COAT ===
    torso_y = head_y + 13
    draw_rect(surface, 4, torso_y, 20, 12, NAVY_BLUE)
    draw_rect(surface, 4, torso_y, 5, 10, NAVY_DARK)
    # White cross-belts
    draw_rect(surface, 10, torso_y, 2, 12, WHITE_TRIM)
    draw_rect(surface, 4, torso_y + 4, 20, 2, WHITE_TRIM)
    # Gold buttons
    for i in range(3):
        draw_pixel(surface, 12, torso_y + 2 + i * 3, GOLD_TRIM)

    # === ARMS & MUSKET ===
    if shooting:
        # Arms forward holding musket
        arm_y = torso_y + 2
        # Both arms forward
        draw_rect(surface, 22, arm_y, 4, 5, NAVY_BLUE)
        draw_rect(surface, 22, arm_y + 4, 4, 2, SKIN)

        # Musket (horizontal, pointing right)
        musket_y = arm_y + 2
        draw_rect(surface, 16, musket_y, 12, 3, MUSKET_WOOD)
        draw_rect(surface, 16, musket_y, 12, 1, MUSKET_WOOD_DARK)

        if shot_frame == 1:
            # Muzzle flash
            draw_rect(surface, 28, musket_y - 2, 4, 2, FIRE_YELLOW)
            draw_rect(surface, 28, musket_y, 5, 3, FIRE_ORANGE)
            draw_rect(surface, 28, musket_y + 3, 3, 2, SMOKE_GRAY)
    else:
        # Arms at rest, musket at side
        arm_y = torso_y + 1
        # Back arm
        draw_rect(surface, 2, arm_y, 3, 7, NAVY_DARK)
        draw_rect(surface, 2, arm_y + 6, 3, 2, SKIN_SHADOW)
        # Front arm
        draw_rect(surface, 23, arm_y, 3, 7, NAVY_BLUE)
        draw_rect(surface, 23, arm_y + 6, 3, 2, SKIN)

        # Musket at side (diagonal)
        draw_rect(surface, 24, torso_y, 2, 14, MUSKET_WOOD)
        draw_rect(surface, 24, torso_y, 1, 14, MUSKET_WOOD_DARK)
        draw_rect(surface, 24, torso_y - 2, 2, 3, MUSKET_METAL)

    # === PANTS ===
    pants_y = torso_y + 12
    draw_rect(surface, 7, pants_y, 5, 6, PANTS_WHITE)
    draw_rect(surface, 7, pants_y, 2, 5, PANTS_SHADOW)
    draw_rect(surface, 16, pants_y, 5, 6, PANTS_WHITE)
    draw_rect(surface, 16, pants_y, 2, 5, PANTS_SHADOW)

    # === BOOTS ===
    boot_y = pants_y + 6
    draw_rect(surface, 5, boot_y, 8, 5, BOOTS_BLACK)
    draw_rect(surface, 7, boot_y + 1, 3, 2, BOOTS_HIGHLIGHT)
    draw_rect(surface, 15, boot_y, 8, 5, BOOTS_BLACK)
    draw_rect(surface, 17, boot_y + 1, 3, 2, BOOTS_HIGHLIGHT)


def create_musketeer_idle_frame():
    """Create musketeer idle frame."""
    # Draw at original size
    surface = pygame.Surface((MUSKETEER_DRAW_WIDTH, MUSKETEER_DRAW_HEIGHT), pygame.SRCALPHA)
    surface.fill(TRANSPARENT)
    draw_musketeer_base(surface, shooting=False)
    add_outline(surface)
    # Scale up to final size
    return scale_surface(surface, MUSKETEER_WIDTH, MUSKETEER_HEIGHT)


def create_musketeer_shoot_frame(frame_num):
    """Create musketeer shooting frame."""
    # Slightly wider for shooting pose with flash
    draw_width = MUSKETEER_DRAW_WIDTH + 8 if frame_num == 1 else MUSKETEER_DRAW_WIDTH
    final_width = MUSKETEER_WIDTH + 10 if frame_num == 1 else MUSKETEER_WIDTH
    surface = pygame.Surface((draw_width, MUSKETEER_DRAW_HEIGHT), pygame.SRCALPHA)
    surface.fill(TRANSPARENT)
    draw_musketeer_base(surface, shooting=True, shot_frame=frame_num)
    add_outline(surface)
    # Scale up to final size
    return scale_surface(surface, final_width, MUSKETEER_HEIGHT)


# ============== OFFICER (40x60 final, drawn at 32x48 then scaled) ==============
OFFICER_DRAW_WIDTH = 32
OFFICER_DRAW_HEIGHT = 48
OFFICER_WIDTH = 40
OFFICER_HEIGHT = 60


def draw_officer_base(surface, leg_offset=0, arm_offset=0, attacking=False, attack_frame=0):
    """Draw an officer facing right."""
    head_x = 10
    head_y = 2

    # === FANCY BICORN HAT ===
    draw_rect(surface, head_x - 2, head_y, 18, 5, HAT_BLUE)
    draw_rect(surface, head_x - 4, head_y + 4, 22, 2, HAT_DARK)
    # Gold trim on hat
    draw_rect(surface, head_x, head_y + 1, 14, 1, GOLD_TRIM)

    # === FACE ===
    draw_rect(surface, head_x + 2, head_y + 6, 12, 9, SKIN)
    draw_rect(surface, head_x + 2, head_y + 6, 3, 7, SKIN_SHADOW)

    # Eye
    draw_rect(surface, head_x + 9, head_y + 9, 3, 2, EYE_WHITE)
    draw_rect(surface, head_x + 10, head_y + 9, 2, 2, EYE_BLACK)

    # Stern expression line
    draw_rect(surface, head_x + 6, head_y + 13, 6, 1, SKIN_SHADOW)

    # === FANCY COAT ===
    torso_y = head_y + 15
    draw_rect(surface, 5, torso_y, 22, 12, NAVY_BLUE)
    draw_rect(surface, 5, torso_y, 5, 10, NAVY_DARK)

    # Gold epaulettes
    draw_rect(surface, 4, torso_y, 4, 3, GOLD_TRIM)
    draw_rect(surface, 24, torso_y, 4, 3, GOLD_TRIM)
    # Gold fringe on epaulettes
    for i in range(3):
        draw_pixel(surface, 4 + i, torso_y + 3, GOLD_DARK)
        draw_pixel(surface, 25 + i, torso_y + 3, GOLD_DARK)

    # White lapels
    draw_rect(surface, 10, torso_y, 3, 10, WHITE_TRIM)
    draw_rect(surface, 19, torso_y, 3, 10, WHITE_TRIM)

    # Gold buttons
    for i in range(4):
        draw_pixel(surface, 14, torso_y + 2 + i * 2, GOLD_TRIM)
        draw_pixel(surface, 17, torso_y + 2 + i * 2, GOLD_TRIM)

    # Belt with gold buckle
    draw_rect(surface, 5, torso_y + 10, 22, 2, WHITE_SHADOW)
    draw_rect(surface, 13, torso_y + 10, 6, 2, GOLD_TRIM)

    # === ARMS & SWORD ===
    arm_y = torso_y + 1 + arm_offset

    if attacking:
        if attack_frame == 0:
            # Wind up - arm back, sword raised
            draw_rect(surface, 2, arm_y - 2, 4, 8, NAVY_DARK)
            draw_rect(surface, 2, arm_y + 5, 4, 2, SKIN_SHADOW)
            # Sword raised
            draw_rect(surface, 0, arm_y - 8, 2, 10, SWORD_SILVER)
            draw_pixel(surface, 0, arm_y - 8, SWORD_EDGE)
        else:
            # Slash - arm forward, sword extended
            draw_rect(surface, 26, arm_y, 4, 6, NAVY_BLUE)
            draw_rect(surface, 26, arm_y + 5, 4, 2, SKIN)
            # Sword horizontal
            draw_rect(surface, 30, arm_y + 2, 16, 2, SWORD_SILVER)
            draw_rect(surface, 30, arm_y + 2, 16, 1, SWORD_EDGE)
            draw_rect(surface, 28, arm_y + 1, 3, 4, SWORD_HANDLE)
    else:
        # Normal pose - sword at side
        # Back arm
        draw_rect(surface, 3, arm_y, 3, 8, NAVY_DARK)
        draw_rect(surface, 3, arm_y + 7, 3, 2, SKIN_SHADOW)
        # Front arm
        draw_rect(surface, 26, arm_y, 3, 8, NAVY_BLUE)
        draw_rect(surface, 26, arm_y + 7, 3, 2, SKIN)
        # Sword at side
        draw_rect(surface, 28, arm_y + 2, 2, 12, SWORD_SILVER)
        draw_rect(surface, 28, arm_y + 2, 1, 12, SWORD_DARK)

    # === PANTS ===
    pants_y = torso_y + 12
    # Left leg
    draw_rect(surface, 8, pants_y + leg_offset, 6, 7, PANTS_WHITE)
    draw_rect(surface, 8, pants_y + leg_offset, 2, 6, PANTS_SHADOW)
    # Right leg
    draw_rect(surface, 18, pants_y - leg_offset, 6, 7, PANTS_WHITE)
    draw_rect(surface, 18, pants_y - leg_offset, 2, 6, PANTS_SHADOW)

    # === BOOTS ===
    boot_y = pants_y + 7
    draw_rect(surface, 6, boot_y + leg_offset, 9, 5, BOOTS_BLACK)
    draw_rect(surface, 8, boot_y + leg_offset + 1, 4, 2, BOOTS_HIGHLIGHT)
    draw_rect(surface, 17, boot_y - leg_offset, 9, 5, BOOTS_BLACK)
    draw_rect(surface, 19, boot_y - leg_offset + 1, 4, 2, BOOTS_HIGHLIGHT)


def create_officer_walk_frame(frame_num):
    """Create officer walk frame."""
    # Draw at original size
    surface = pygame.Surface((OFFICER_DRAW_WIDTH, OFFICER_DRAW_HEIGHT), pygame.SRCALPHA)
    surface.fill(TRANSPARENT)
    leg_offset = 4 if frame_num == 0 else -4
    arm_offset = -2 if frame_num == 0 else 2
    draw_officer_base(surface, leg_offset=leg_offset, arm_offset=arm_offset)
    add_outline(surface)
    # Scale up to final size
    return scale_surface(surface, OFFICER_WIDTH, OFFICER_HEIGHT)


def create_officer_attack_frame(frame_num):
    """Create officer attack frame."""
    # Wider for attack with sword extended
    draw_width = OFFICER_DRAW_WIDTH + 16 if frame_num == 1 else OFFICER_DRAW_WIDTH
    final_width = OFFICER_WIDTH + 20 if frame_num == 1 else OFFICER_WIDTH
    surface = pygame.Surface((draw_width, OFFICER_DRAW_HEIGHT), pygame.SRCALPHA)
    surface.fill(TRANSPARENT)
    draw_officer_base(surface, attacking=True, attack_frame=frame_num)
    add_outline(surface)
    # Scale up to final size
    return scale_surface(surface, final_width, OFFICER_HEIGHT)


# ============== CANNON (40x40 final, drawn at 32x32 then scaled) ==============
CANNON_DRAW_WIDTH = 32
CANNON_DRAW_HEIGHT = 32
CANNON_WIDTH = 40
CANNON_HEIGHT = 40


def draw_cannon_base(surface, firing=False, fire_frame=0):
    """Draw a cannon facing right."""
    # Wheels
    wheel_y = 22
    # Left wheel
    draw_rect(surface, 2, wheel_y, 10, 10, CANNON_WHEEL)
    draw_rect(surface, 4, wheel_y + 2, 6, 6, CANNON_WHEEL_DARK)
    draw_rect(surface, 6, wheel_y + 4, 2, 2, CANNON_WHEEL)  # Hub
    # Right wheel
    draw_rect(surface, 20, wheel_y, 10, 10, CANNON_WHEEL)
    draw_rect(surface, 22, wheel_y + 2, 6, 6, CANNON_WHEEL_DARK)
    draw_rect(surface, 24, wheel_y + 4, 2, 2, CANNON_WHEEL)  # Hub

    # Carriage
    draw_rect(surface, 6, 18, 20, 6, CANNON_WHEEL)
    draw_rect(surface, 6, 20, 20, 2, CANNON_WHEEL_DARK)

    # Cannon barrel
    draw_rect(surface, 8, 8, 18, 10, CANNON_METAL)
    draw_rect(surface, 8, 8, 18, 3, CANNON_HIGHLIGHT)  # Top highlight
    draw_rect(surface, 8, 15, 18, 3, CANNON_DARK)  # Bottom shadow

    # Muzzle
    draw_rect(surface, 24, 6, 6, 14, CANNON_METAL)
    draw_rect(surface, 26, 8, 4, 10, CANNON_DARK)  # Bore

    # Rear
    draw_rect(surface, 4, 10, 5, 6, CANNON_DARK)

    # Firing effects
    if firing:
        if fire_frame == 0:
            # Initial flash
            draw_rect(surface, 30, 4, 2, 4, FIRE_YELLOW)
            draw_rect(surface, 30, 8, 3, 10, FIRE_ORANGE)
            draw_rect(surface, 30, 18, 2, 4, FIRE_YELLOW)
        else:
            # Smoke
            draw_rect(surface, 30, 6, 4, 6, SMOKE_GRAY)
            draw_rect(surface, 32, 4, 3, 10, (200, 200, 200, 255))
            draw_rect(surface, 34, 8, 2, 6, (220, 220, 220, 255))


def create_cannon_static_frame():
    """Create cannon static frame."""
    # Draw at original size
    surface = pygame.Surface((CANNON_DRAW_WIDTH, CANNON_DRAW_HEIGHT), pygame.SRCALPHA)
    surface.fill(TRANSPARENT)
    draw_cannon_base(surface, firing=False)
    add_outline(surface)
    # Scale up to final size
    return scale_surface(surface, CANNON_WIDTH, CANNON_HEIGHT)


def create_cannon_fire_frame(frame_num):
    """Create cannon firing frame."""
    # Wider for firing effects
    draw_width = CANNON_DRAW_WIDTH + 8
    final_width = CANNON_WIDTH + 10
    surface = pygame.Surface((draw_width, CANNON_DRAW_HEIGHT), pygame.SRCALPHA)
    surface.fill(TRANSPARENT)
    draw_cannon_base(surface, firing=True, fire_frame=frame_num)
    add_outline(surface)
    # Scale up to final size
    return scale_surface(surface, final_width, CANNON_HEIGHT)


# ============== PROJECTILES ==============


def create_musket_ball():
    """Create 8x8 musket ball sprite."""
    surface = pygame.Surface((8, 8), pygame.SRCALPHA)
    surface.fill(TRANSPARENT)

    # Simple round ball
    draw_rect(surface, 2, 1, 4, 6, MUSKET_BALL_GRAY)
    draw_rect(surface, 1, 2, 6, 4, MUSKET_BALL_GRAY)
    # Highlight
    draw_pixel(surface, 2, 2, (255, 255, 255, 255))
    # Shadow
    draw_pixel(surface, 5, 5, (150, 150, 150, 255))

    add_outline(surface)
    return surface


def create_cannonball():
    """Create 12x12 cannonball sprite."""
    surface = pygame.Surface((12, 12), pygame.SRCALPHA)
    surface.fill(TRANSPARENT)

    # Larger round ball
    draw_rect(surface, 3, 1, 6, 10, CANNONBALL_DARK)
    draw_rect(surface, 1, 3, 10, 6, CANNONBALL_DARK)
    draw_rect(surface, 2, 2, 8, 8, CANNONBALL_DARK)
    # Highlight
    draw_rect(surface, 3, 3, 3, 3, CANNONBALL_HIGHLIGHT)
    # Shadow
    draw_rect(surface, 7, 7, 2, 2, BLACK)

    add_outline(surface)
    return surface


def create_admiral_bullet():
    """Create 10x10 admiral bullet sprite (gold/fancy)."""
    surface = pygame.Surface((10, 10), pygame.SRCALPHA)
    surface.fill(TRANSPARENT)

    # Gold bullet with trail hint
    draw_rect(surface, 3, 2, 4, 6, ADMIRAL_BULLET_GOLD)
    draw_rect(surface, 2, 3, 6, 4, ADMIRAL_BULLET_GOLD)
    # Bright center
    draw_rect(surface, 4, 4, 2, 2, (255, 220, 120, 255))
    # Trail
    draw_rect(surface, 0, 4, 2, 2, (255, 200, 100, 180))

    add_outline(surface)
    return surface


# ============== SPRITE SHEET GENERATION ==============


def generate_enemy_sprite_sheet():
    """
    Generate combined enemy sprite sheet.

    Layout (scaled up sizes):
    - Row 0: Sailor - walk (2 frames @ 36px), hurt (1 frame @ 36px) = 108px wide
    - Row 1: Musketeer - idle (36px), shoot (36px), shoot+flash (46px) = 118px wide
    - Row 2: Officer - walk (2 frames @ 40px), attack wind-up (40px), attack slash (60px) = 180px wide
    - Row 3: Cannon - static (40px), fire1 (50px), fire2 (50px) = 140px wide

    Total width: 180px (max row width - officer attack)
    Total height: 56 + 56 + 60 + 40 = 212px
    """
    # Calculate dimensions dynamically based on actual frame sizes
    row_heights = [SAILOR_HEIGHT, MUSKETEER_HEIGHT, OFFICER_HEIGHT, CANNON_HEIGHT]
    total_height = sum(row_heights)
    # Officer attack row is widest: 2*40 + 40 + 60 = 180
    total_width = OFFICER_WIDTH * 2 + OFFICER_WIDTH + (OFFICER_WIDTH + 20)  # ~180

    sheet = pygame.Surface((total_width, total_height), pygame.SRCALPHA)
    sheet.fill(TRANSPARENT)

    y_offset = 0

    # Row 0: Sailor
    x = 0
    for i in range(2):
        frame = create_sailor_walk_frame(i)
        sheet.blit(frame, (x, y_offset))
        x += SAILOR_WIDTH
    sheet.blit(create_sailor_hurt_frame(), (x, y_offset))
    y_offset += SAILOR_HEIGHT

    # Row 1: Musketeer
    x = 0
    sheet.blit(create_musketeer_idle_frame(), (x, y_offset))
    x += MUSKETEER_WIDTH
    for i in range(2):
        frame = create_musketeer_shoot_frame(i)
        sheet.blit(frame, (x, y_offset))
        x += frame.get_width()
    y_offset += MUSKETEER_HEIGHT

    # Row 2: Officer
    x = 0
    for i in range(2):
        frame = create_officer_walk_frame(i)
        sheet.blit(frame, (x, y_offset))
        x += OFFICER_WIDTH
    for i in range(2):
        frame = create_officer_attack_frame(i)
        sheet.blit(frame, (x, y_offset))
        x += frame.get_width()
    y_offset += OFFICER_HEIGHT

    # Row 3: Cannon
    x = 0
    sheet.blit(create_cannon_static_frame(), (x, y_offset))
    x += CANNON_WIDTH
    for i in range(2):
        frame = create_cannon_fire_frame(i)
        sheet.blit(frame, (x, y_offset))
        x += frame.get_width()

    return sheet


def generate_projectile_sheet():
    """
    Generate projectile sprite sheet.

    Layout: musket_ball (8x8), cannonball (12x12), admiral_bullet (10x10)
    All on one row with some padding.
    """
    # Max height is 12 (cannonball)
    height = 12
    width = 8 + 4 + 12 + 4 + 10  # sprites + padding

    sheet = pygame.Surface((width, height), pygame.SRCALPHA)
    sheet.fill(TRANSPARENT)

    x = 0

    # Musket ball (centered vertically)
    ball = create_musket_ball()
    sheet.blit(ball, (x, (height - 8) // 2))
    x += 8 + 4

    # Cannonball
    cannon = create_cannonball()
    sheet.blit(cannon, (x, 0))
    x += 12 + 4

    # Admiral bullet (centered vertically)
    bullet = create_admiral_bullet()
    sheet.blit(bullet, (x, (height - 10) // 2))

    return sheet


def main():
    """Generate and save the sprite sheets."""
    print("Generating enemy sprite sheets...")

    # Enemy sprites
    enemy_sheet = generate_enemy_sprite_sheet()
    enemy_path = "assets/sprites/enemies.png"
    pygame.image.save(enemy_sheet, enemy_path)
    print(f"Saved enemy sprites to {enemy_path}")
    print(f"  Size: {enemy_sheet.get_width()}x{enemy_sheet.get_height()} pixels")
    print("  Layout:")
    print(f"    Row 0 (y=0): Sailor ({SAILOR_WIDTH}x{SAILOR_HEIGHT}) - walk[0,1], hurt")
    print(f"    Row 1 (y={SAILOR_HEIGHT}): Musketeer ({MUSKETEER_WIDTH}x{MUSKETEER_HEIGHT}) - idle, shoot[0,1]")
    print(f"    Row 2 (y={SAILOR_HEIGHT + MUSKETEER_HEIGHT}): Officer ({OFFICER_WIDTH}x{OFFICER_HEIGHT}) - walk[0,1], attack[0,1]")
    print(f"    Row 3 (y={SAILOR_HEIGHT + MUSKETEER_HEIGHT + OFFICER_HEIGHT}): Cannon ({CANNON_WIDTH}x{CANNON_HEIGHT}) - static, fire[0,1]")

    # Projectile sprites
    proj_sheet = generate_projectile_sheet()
    proj_path = "assets/sprites/projectiles.png"
    pygame.image.save(proj_sheet, proj_path)
    print(f"\nSaved projectile sprites to {proj_path}")
    print(f"  Size: {proj_sheet.get_width()}x{proj_sheet.get_height()} pixels")
    print("  Layout: musket_ball(8x8), cannonball(12x12), admiral_bullet(10x10)")

    pygame.quit()


if __name__ == "__main__":
    main()
