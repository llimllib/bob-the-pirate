#!/usr/bin/env python3
"""
Generate NES-style 8-bit background layers for Bob the Pirate.

Backgrounds:
  - Sky gradient (800x600)
  - Clouds layer (parallax, seamless tiling)
  - Distant scenery (mountains/ships, parallax)

Output: assets/backgrounds/
"""

import os

import pygame

# Initialize pygame
pygame.init()

# Screen dimensions
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

# Color palette (NES-inspired)
TRANSPARENT = (0, 0, 0, 0)

# Sky colors (gradient from top to bottom)
SKY_TOP = (100, 160, 220, 255)  # Lighter blue at top
SKY_MID = (135, 195, 235, 255)  # Mid sky
SKY_BOTTOM = (180, 220, 245, 255)  # Lighter near horizon

# Cloud colors
CLOUD_WHITE = (245, 245, 250, 255)
CLOUD_SHADOW = (210, 215, 230, 255)
CLOUD_HIGHLIGHT = (255, 255, 255, 255)

# Ocean/water colors
OCEAN_DARK = (30, 80, 120, 255)
OCEAN_MID = (50, 110, 160, 255)
OCEAN_LIGHT = (80, 140, 190, 255)
OCEAN_HIGHLIGHT = (120, 180, 220, 255)

# Distant scenery colors
MOUNTAIN_FAR = (120, 135, 155, 255)  # Very distant, faded
MOUNTAIN_MID = (90, 105, 125, 255)  # Medium distance
MOUNTAIN_NEAR = (70, 85, 105, 255)  # Closer
SHIP_HULL = (80, 60, 45, 255)
SHIP_SAIL = (230, 225, 215, 255)
SHIP_MAST = (90, 70, 50, 255)


def draw_pixel(surface, x, y, color):
    """Draw a single pixel."""
    w, h = surface.get_size()
    if 0 <= x < w and 0 <= y < h:
        surface.set_at((x, y), color)


def draw_rect(surface, x, y, w, h, color):
    """Draw a filled rectangle."""
    pygame.draw.rect(surface, color, (x, y, w, h))


def lerp_color(c1, c2, t):
    """Linearly interpolate between two colors."""
    return tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)) + (255,)


# =============================================================================
# SKY BACKGROUND
# =============================================================================

def create_sky_background():
    """Create sky gradient background (800x600)."""
    surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    # Draw gradient from top to bottom
    for y in range(SCREEN_HEIGHT):
        t = y / SCREEN_HEIGHT
        if t < 0.5:
            # Top to middle
            color = lerp_color(SKY_TOP, SKY_MID, t * 2)
        else:
            # Middle to bottom
            color = lerp_color(SKY_MID, SKY_BOTTOM, (t - 0.5) * 2)
        pygame.draw.line(surface, color, (0, y), (SCREEN_WIDTH, y))

    return surface


# =============================================================================
# CLOUDS LAYER (tileable)
# =============================================================================

def draw_cloud(surface, x, y, size="medium"):
    """Draw a single cloud at position."""
    if size == "small":
        # Small cloud
        draw_rect(surface, x + 4, y + 4, 16, 8, CLOUD_SHADOW)
        draw_rect(surface, x + 4, y, 16, 8, CLOUD_WHITE)
        draw_rect(surface, x, y + 2, 8, 6, CLOUD_WHITE)
        draw_rect(surface, x + 16, y + 2, 8, 6, CLOUD_WHITE)
        draw_rect(surface, x + 6, y - 2, 12, 4, CLOUD_HIGHLIGHT)
    elif size == "medium":
        # Medium cloud
        draw_rect(surface, x + 8, y + 10, 32, 12, CLOUD_SHADOW)
        draw_rect(surface, x + 8, y + 4, 32, 12, CLOUD_WHITE)
        draw_rect(surface, x, y + 6, 16, 10, CLOUD_WHITE)
        draw_rect(surface, x + 32, y + 6, 16, 10, CLOUD_WHITE)
        draw_rect(surface, x + 16, y, 20, 8, CLOUD_WHITE)
        draw_rect(surface, x + 12, y - 2, 24, 6, CLOUD_HIGHLIGHT)
    else:  # large
        # Large cloud
        draw_rect(surface, x + 12, y + 14, 48, 16, CLOUD_SHADOW)
        draw_rect(surface, x + 12, y + 6, 48, 14, CLOUD_WHITE)
        draw_rect(surface, x, y + 10, 20, 12, CLOUD_WHITE)
        draw_rect(surface, x + 52, y + 10, 20, 12, CLOUD_WHITE)
        draw_rect(surface, x + 20, y, 32, 10, CLOUD_WHITE)
        draw_rect(surface, x + 8, y + 2, 16, 8, CLOUD_WHITE)
        draw_rect(surface, x + 48, y + 2, 16, 8, CLOUD_WHITE)
        draw_rect(surface, x + 16, y - 4, 40, 8, CLOUD_HIGHLIGHT)


def create_clouds_layer():
    """Create tileable clouds layer (wider than screen for seamless scroll)."""
    # Make it 1.5x screen width for seamless tiling
    width = int(SCREEN_WIDTH * 1.5)
    height = 200  # Clouds only in upper portion

    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    surface.fill(TRANSPARENT)

    # Scatter clouds at various positions
    cloud_positions = [
        (20, 30, "large"),
        (180, 80, "medium"),
        (350, 20, "small"),
        (450, 60, "medium"),
        (600, 40, "large"),
        (780, 90, "small"),
        (900, 50, "medium"),
        (1050, 70, "small"),
    ]

    for x, y, size in cloud_positions:
        draw_cloud(surface, x, y, size)

    return surface


# =============================================================================
# DISTANT SCENERY LAYER
# =============================================================================

def draw_distant_ship(surface, x, y, scale=1.0):
    """Draw a distant ship silhouette."""
    s = scale
    # Hull
    hull_w = int(40 * s)
    hull_h = int(12 * s)
    draw_rect(surface, x, y, hull_w, hull_h, SHIP_HULL)
    # Bow (front of ship)
    for i in range(int(8 * s)):
        draw_rect(surface, x + hull_w + i, y + int(4 * s), 1, int(8 * s) - i, SHIP_HULL)

    # Mast
    mast_h = int(30 * s)
    mast_x = x + int(20 * s)
    draw_rect(surface, mast_x, y - mast_h, int(2 * s), mast_h, SHIP_MAST)

    # Sail
    sail_w = int(16 * s)
    sail_h = int(20 * s)
    draw_rect(surface, mast_x - int(6 * s), y - mast_h + int(4 * s), sail_w, sail_h, SHIP_SAIL)


def draw_mountain_range(surface, y_base, color, height_variation):
    """Draw a jagged mountain range silhouette."""
    import random
    random.seed(42 + hash(color))  # Deterministic but different per color

    width = surface.get_width()
    points = []

    x = 0
    while x < width + 50:
        # Create peaks and valleys
        height = random.randint(height_variation[0], height_variation[1])
        points.append((x, y_base - height))
        x += random.randint(30, 80)

    # Close the polygon at the bottom
    points.append((width, y_base))
    points.append((0, y_base))

    if len(points) >= 3:
        pygame.draw.polygon(surface, color, points)


def create_distant_scenery_layer():
    """Create distant scenery layer (mountains and ships, parallax)."""
    width = int(SCREEN_WIDTH * 2)  # Wide for parallax scrolling
    height = 300

    surface = pygame.Surface((width, height), pygame.SRCALPHA)
    surface.fill(TRANSPARENT)

    y_base = height - 20

    # Far mountains (lightest, tallest peaks)
    draw_mountain_range(surface, y_base - 60, MOUNTAIN_FAR, (80, 140))

    # Mid mountains
    draw_mountain_range(surface, y_base - 30, MOUNTAIN_MID, (50, 100))

    # Near mountains (darkest, lower)
    draw_mountain_range(surface, y_base, MOUNTAIN_NEAR, (30, 70))

    # Add a few distant ships
    draw_distant_ship(surface, 200, y_base - 50, scale=0.6)
    draw_distant_ship(surface, 700, y_base - 40, scale=0.5)
    draw_distant_ship(surface, 1200, y_base - 55, scale=0.7)

    return surface


# =============================================================================
# OCEAN/WATER LAYER
# =============================================================================

def create_ocean_layer():
    """Create animated ocean layer (tileable, multiple frames)."""
    width = SCREEN_WIDTH
    height = 80
    frames = []

    for frame_num in range(4):
        surface = pygame.Surface((width, height), pygame.SRCALPHA)

        # Base ocean color
        for y in range(height):
            t = y / height
            color = lerp_color(OCEAN_LIGHT, OCEAN_DARK, t)
            pygame.draw.line(surface, color, (0, y), (width, y))

        # Wave highlights (animated)
        wave_offset = frame_num * 8
        for x in range(0, width + 50, 40):
            wave_x = (x + wave_offset) % (width + 50)
            # Top wave crest
            draw_rect(surface, wave_x, 2, 20, 3, OCEAN_HIGHLIGHT)
            draw_rect(surface, wave_x + 5, 0, 10, 2, OCEAN_HIGHLIGHT)
            # Secondary waves
            draw_rect(surface, (wave_x + 20) % width, 15, 15, 2, OCEAN_MID)
            draw_rect(surface, (wave_x + 35) % width, 30, 12, 2, OCEAN_MID)

        frames.append(surface)

    return frames


# =============================================================================
# MAIN GENERATION
# =============================================================================

def ensure_dir(path):
    """Ensure directory exists."""
    os.makedirs(path, exist_ok=True)


# =============================================================================
# SHIP INTERIOR BACKGROUND (for boss arena)
# =============================================================================

# Ship interior colors
WOOD_WALL_LIGHT = (160, 120, 75, 255)
WOOD_WALL_MID = (130, 95, 60, 255)
WOOD_WALL_DARK = (100, 70, 45, 255)
WOOD_FLOOR_LIGHT = (140, 100, 60, 255)
WOOD_FLOOR_MID = (110, 80, 50, 255)
WOOD_FLOOR_DARK = (85, 60, 40, 255)
WINDOW_FRAME = (70, 50, 35, 255)
WINDOW_GLASS = (150, 180, 200, 200)
WINDOW_LIGHT = (180, 200, 220, 255)
LANTERN_GLOW = (255, 200, 100, 255)
LANTERN_BODY = (80, 60, 40, 255)
ROPE_COLOR = (160, 130, 90, 255)
CANNON_METAL = (60, 60, 70, 255)


def create_ship_interior_background():
    """Create ship interior background for boss arena (800x600)."""
    surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)

    # Wood wall planks (horizontal)
    for y in range(0, SCREEN_HEIGHT - 100, 24):
        # Alternate plank shades
        color = WOOD_WALL_MID if (y // 24) % 2 == 0 else WOOD_WALL_LIGHT
        draw_rect(surface, 0, y, SCREEN_WIDTH, 24, color)
        # Plank line
        draw_rect(surface, 0, y + 22, SCREEN_WIDTH, 2, WOOD_WALL_DARK)
        # Wood grain
        for x in range(20, SCREEN_WIDTH, 80):
            draw_rect(surface, x, y + 8, 30, 2, WOOD_WALL_DARK)
            draw_rect(surface, x + 40, y + 14, 25, 2, WOOD_WALL_DARK)

    # Add some vertical support beams
    for x in [0, 200, 400, 600, SCREEN_WIDTH - 32]:
        draw_rect(surface, x, 0, 32, SCREEN_HEIGHT - 100, WOOD_WALL_DARK)
        draw_rect(surface, x + 4, 0, 4, SCREEN_HEIGHT - 100, WOOD_WALL_LIGHT)

    # Windows (portholes)
    porthole_positions = [(100, 150), (300, 180), (500, 150), (700, 180)]
    for px, py in porthole_positions:
        # Window frame (circular porthole)
        draw_rect(surface, px - 25, py - 25, 50, 50, WINDOW_FRAME)
        draw_rect(surface, px - 20, py - 20, 40, 40, WINDOW_GLASS)
        # Light reflection
        draw_rect(surface, px - 15, py - 15, 15, 10, WINDOW_LIGHT)
        # Cross frame
        draw_rect(surface, px - 2, py - 20, 4, 40, WINDOW_FRAME)
        draw_rect(surface, px - 20, py - 2, 40, 4, WINDOW_FRAME)

    # Hanging lanterns
    lantern_positions = [(150, 80), (400, 60), (650, 80)]
    for lx, ly in lantern_positions:
        # Chain/rope
        draw_rect(surface, lx + 6, 0, 4, ly, ROPE_COLOR)
        # Lantern body
        draw_rect(surface, lx, ly, 16, 24, LANTERN_BODY)
        draw_rect(surface, lx + 2, ly + 4, 12, 16, LANTERN_GLOW)
        # Top/bottom caps
        draw_rect(surface, lx - 2, ly - 4, 20, 6, LANTERN_BODY)
        draw_rect(surface, lx - 2, ly + 22, 20, 6, LANTERN_BODY)

    # Cannons on sides (decorative, in background)
    for cy in [280, 380]:
        # Left cannon
        draw_rect(surface, 10, cy, 40, 20, CANNON_METAL)
        draw_rect(surface, 45, cy + 4, 20, 12, CANNON_METAL)
        # Right cannon
        draw_rect(surface, SCREEN_WIDTH - 50, cy, 40, 20, CANNON_METAL)
        draw_rect(surface, SCREEN_WIDTH - 65, cy + 4, 20, 12, CANNON_METAL)

    # Rope coils on walls
    for rx, ry in [(80, 350), (720, 320)]:
        draw_rect(surface, rx, ry, 30, 20, ROPE_COLOR)
        draw_rect(surface, rx + 5, ry + 5, 20, 10, WOOD_WALL_DARK)

    return surface


def main():
    """Generate and save all background assets."""
    output_dir = "assets/backgrounds"
    ensure_dir(output_dir)

    print("Generating background assets...")

    # Sky
    sky = create_sky_background()
    sky_path = os.path.join(output_dir, "sky.png")
    pygame.image.save(sky, sky_path)
    print(f"  Saved sky background to {sky_path} ({sky.get_width()}x{sky.get_height()})")

    # Clouds
    clouds = create_clouds_layer()
    clouds_path = os.path.join(output_dir, "clouds.png")
    pygame.image.save(clouds, clouds_path)
    print(f"  Saved clouds layer to {clouds_path} ({clouds.get_width()}x{clouds.get_height()})")

    # Distant scenery
    scenery = create_distant_scenery_layer()
    scenery_path = os.path.join(output_dir, "distant_scenery.png")
    pygame.image.save(scenery, scenery_path)
    print(f"  Saved distant scenery to {scenery_path} ({scenery.get_width()}x{scenery.get_height()})")

    # Ocean frames (for animation)
    ocean_frames = create_ocean_layer()
    for i, frame in enumerate(ocean_frames):
        frame_path = os.path.join(output_dir, f"ocean_{i}.png")
        pygame.image.save(frame, frame_path)
    print(f"  Saved {len(ocean_frames)} ocean animation frames")

    # Ship interior (for boss arena)
    ship_interior = create_ship_interior_background()
    ship_path = os.path.join(output_dir, "ship_interior.png")
    pygame.image.save(ship_interior, ship_path)
    print(f"  Saved ship interior to {ship_path} ({ship_interior.get_width()}x{ship_interior.get_height()})")

    print("\nBackground generation complete!")
    print("\nUsage:")
    print("  - sky.png: Static background for outdoor levels")
    print("  - distant_scenery.png: Parallax layer (0.2x scroll speed)")
    print("  - clouds.png: Parallax layer (0.5x scroll speed)")
    print("  - ocean_*.png: Animated water (optional, bottom of screen)")
    print("  - ship_interior.png: Static background for boss arena")

    pygame.quit()


if __name__ == "__main__":
    main()
