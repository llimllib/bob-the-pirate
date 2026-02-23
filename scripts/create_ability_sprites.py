#!/usr/bin/env python3
"""Create barrel roll, anchor slam, and bosun sprites."""

from PIL import Image, ImageDraw

# Colors
TRANSPARENT = (0, 0, 0, 0)
BLACK = (0, 0, 0, 255)
WHITE = (255, 255, 255, 255)

# Bob's colors (matching player.png)
SKIN = (222, 178, 135, 255)
SKIN_SHADOW = (189, 145, 107, 255)
RED_BANDANA = (180, 50, 50, 255)
RED_BANDANA_DARK = (140, 35, 35, 255)
SHIRT = (240, 230, 210, 255)
SHIRT_SHADOW = (200, 190, 175, 255)
PANTS = (100, 75, 55, 255)
PANTS_SHADOW = (75, 55, 40, 255)
BOOTS = (60, 45, 35, 255)

# Barrel colors
BARREL_LIGHT = (160, 110, 60, 255)
BARREL_MID = (130, 85, 45, 255)
BARREL_DARK = (100, 65, 35, 255)
BARREL_BAND = (80, 80, 90, 255)

# Anchor colors
ANCHOR_LIGHT = (120, 120, 130, 255)
ANCHOR_MID = (90, 90, 100, 255)
ANCHOR_DARK = (60, 60, 70, 255)

# Bosun colors
BOSUN_SKIN = (210, 165, 125, 255)
BOSUN_SKIN_SHADOW = (175, 135, 100, 255)
BLUE_BANDANA = (50, 80, 150, 255)
BLUE_BANDANA_DARK = (35, 55, 110, 255)
GRAY_SHIRT = (140, 140, 145, 255)
GRAY_SHIRT_SHADOW = (110, 110, 115, 255)
GRAY_PANTS = (100, 100, 105, 255)
GRAY_PANTS_SHADOW = (75, 75, 80, 255)
AXE_HANDLE = (100, 70, 45, 255)
AXE_BLADE = (160, 160, 170, 255)
AXE_BLADE_DARK = (120, 120, 130, 255)


def create_barrel_roll_frames():
    """Create 4 frames of Bob rolling in a barrel."""
    frames = []
    width, height = 32, 48

    for frame_num in range(4):
        img = Image.new('RGBA', (width, height), TRANSPARENT)
        draw = ImageDraw.Draw(img)

        # Barrel rotates - different orientations
        # Frame 0: upright barrel, Bob's head visible at top
        # Frame 1: barrel tilted, head at top-right
        # Frame 2: barrel sideways, Bob hidden
        # Frame 3: barrel tilted other way, head at top-left

        barrel_y = 8  # Barrel vertical position
        barrel_h = 36
        barrel_w = 28
        barrel_x = (width - barrel_w) // 2

        if frame_num == 0:
            # Upright barrel with Bob's head poking out
            # Barrel body
            draw.rectangle([barrel_x, barrel_y + 8, barrel_x + barrel_w, barrel_y + barrel_h], fill=BARREL_MID)
            # Barrel bands
            draw.rectangle([barrel_x, barrel_y + 12, barrel_x + barrel_w, barrel_y + 16], fill=BARREL_BAND)
            draw.rectangle([barrel_x, barrel_y + 28, barrel_x + barrel_w, barrel_y + 32], fill=BARREL_BAND)
            # Barrel highlights
            draw.rectangle([barrel_x + 2, barrel_y + 8, barrel_x + 6, barrel_y + barrel_h], fill=BARREL_LIGHT)
            draw.rectangle([barrel_x + barrel_w - 6, barrel_y + 8, barrel_x + barrel_w - 2, barrel_y + barrel_h], fill=BARREL_DARK)
            # Bob's head poking out
            draw.rectangle([12, barrel_y, 20, barrel_y + 10], fill=SKIN)
            draw.rectangle([10, barrel_y - 2, 22, barrel_y + 3], fill=RED_BANDANA)
            # Eyes
            draw.rectangle([13, barrel_y + 4, 15, barrel_y + 6], fill=BLACK)
            draw.rectangle([17, barrel_y + 4, 19, barrel_y + 6], fill=BLACK)

        elif frame_num == 1:
            # Barrel tilted right, rolling
            draw.ellipse([barrel_x - 2, barrel_y + 4, barrel_x + barrel_w + 2, barrel_y + barrel_h + 4], fill=BARREL_MID)
            # Bands (curved effect)
            draw.arc([barrel_x - 2, barrel_y + 4, barrel_x + barrel_w + 2, barrel_y + barrel_h + 4], 45, 135, fill=BARREL_BAND, width=3)
            draw.arc([barrel_x - 2, barrel_y + 4, barrel_x + barrel_w + 2, barrel_y + barrel_h + 4], 225, 315, fill=BARREL_BAND, width=3)
            # Highlight
            draw.ellipse([barrel_x, barrel_y + 6, barrel_x + 8, barrel_y + barrel_h], fill=BARREL_LIGHT)
            # Bob's hand waving
            draw.rectangle([22, barrel_y + 2, 28, barrel_y + 8], fill=SKIN)

        elif frame_num == 2:
            # Barrel fully sideways (Bob hidden inside)
            center_y = barrel_y + barrel_h // 2
            # Draw barrel as circle
            draw.ellipse([barrel_x - 4, center_y - 14, barrel_x + barrel_w + 4, center_y + 14], fill=BARREL_MID)
            # Bands as lines
            draw.line([barrel_x, center_y - 10, barrel_x + barrel_w, center_y - 10], fill=BARREL_BAND, width=3)
            draw.line([barrel_x, center_y + 10, barrel_x + barrel_w, center_y + 10], fill=BARREL_BAND, width=3)
            # Highlight
            draw.ellipse([barrel_x - 2, center_y - 12, barrel_x + 8, center_y + 12], fill=BARREL_LIGHT)
            draw.ellipse([barrel_x + barrel_w - 8, center_y - 12, barrel_x + barrel_w + 2, center_y + 12], fill=BARREL_DARK)

        elif frame_num == 3:
            # Barrel tilted left
            draw.ellipse([barrel_x - 2, barrel_y + 4, barrel_x + barrel_w + 2, barrel_y + barrel_h + 4], fill=BARREL_MID)
            # Bands
            draw.arc([barrel_x - 2, barrel_y + 4, barrel_x + barrel_w + 2, barrel_y + barrel_h + 4], 45, 135, fill=BARREL_BAND, width=3)
            draw.arc([barrel_x - 2, barrel_y + 4, barrel_x + barrel_w + 2, barrel_y + barrel_h + 4], 225, 315, fill=BARREL_BAND, width=3)
            # Highlight on other side
            draw.ellipse([barrel_x + barrel_w - 8, barrel_y + 6, barrel_x + barrel_w, barrel_y + barrel_h], fill=BARREL_LIGHT)
            # Bob's bandana visible
            draw.rectangle([4, barrel_y + 2, 12, barrel_y + 8], fill=RED_BANDANA)

        frames.append(img)

    return frames


def create_anchor_slam_frames():
    """Create 3 frames: wind-up, slamming down, impact."""
    frames = []
    width, height = 32, 48

    for frame_num in range(3):
        img = Image.new('RGBA', (width, height), TRANSPARENT)
        draw = ImageDraw.Draw(img)

        if frame_num == 0:
            # Wind-up: Bob holding anchor above head
            # Body (compact, ready to slam)
            draw.rectangle([10, 20, 22, 36], fill=SHIRT)
            draw.rectangle([10, 20, 14, 36], fill=SHIRT_SHADOW)
            # Head
            draw.rectangle([11, 10, 21, 20], fill=SKIN)
            draw.rectangle([9, 8, 23, 12], fill=RED_BANDANA)
            # Eyes looking down
            draw.rectangle([13, 14, 15, 16], fill=BLACK)
            draw.rectangle([17, 14, 19, 16], fill=BLACK)
            # Legs tucked
            draw.rectangle([10, 36, 15, 44], fill=PANTS)
            draw.rectangle([17, 36, 22, 44], fill=PANTS)
            # Arms up holding anchor
            draw.rectangle([6, 12, 10, 20], fill=SKIN)  # Left arm
            draw.rectangle([22, 12, 26, 20], fill=SKIN)  # Right arm
            # Anchor above head
            # Anchor ring
            draw.ellipse([12, 0, 20, 8], outline=ANCHOR_MID, width=2)
            # Anchor shaft
            draw.rectangle([15, 6, 17, 14], fill=ANCHOR_MID)
            # Anchor flukes (pointing up in wind-up)
            draw.polygon([(10, 6), (16, 12), (16, 10), (12, 4)], fill=ANCHOR_DARK)
            draw.polygon([(22, 6), (16, 12), (16, 10), (20, 4)], fill=ANCHOR_LIGHT)

        elif frame_num == 1:
            # Slamming down: Bob diving with anchor below
            # Body stretched downward
            draw.rectangle([12, 8, 20, 22], fill=SHIRT)
            draw.rectangle([12, 8, 15, 22], fill=SHIRT_SHADOW)
            # Head
            draw.rectangle([12, 0, 20, 10], fill=SKIN)
            draw.rectangle([10, 0, 22, 4], fill=RED_BANDANA)
            # Eyes determined
            draw.rectangle([13, 4, 15, 6], fill=BLACK)
            draw.rectangle([17, 4, 19, 6], fill=BLACK)
            # Legs trailing up
            draw.rectangle([12, 22, 16, 30], fill=PANTS)
            draw.rectangle([16, 22, 20, 28], fill=PANTS)
            # Arms down gripping anchor
            draw.rectangle([10, 18, 14, 26], fill=SKIN)
            draw.rectangle([18, 18, 22, 26], fill=SKIN)
            # Anchor below, pointing down
            # Anchor shaft
            draw.rectangle([15, 26, 17, 40], fill=ANCHOR_MID)
            # Anchor ring (at grip point)
            draw.ellipse([13, 24, 19, 30], outline=ANCHOR_MID, width=2)
            # Anchor flukes (wide, pointing down)
            draw.polygon([(8, 42), (16, 36), (16, 40), (6, 48)], fill=ANCHOR_DARK)
            draw.polygon([(24, 42), (16, 36), (16, 40), (26, 48)], fill=ANCHOR_LIGHT)
            # Crown/cross piece
            draw.rectangle([10, 40, 22, 43], fill=ANCHOR_MID)

        elif frame_num == 2:
            # Impact: Bob crouched, anchor embedded, shockwave effect
            # Body crouched low
            draw.rectangle([8, 24, 24, 36], fill=SHIRT)
            draw.rectangle([8, 24, 14, 36], fill=SHIRT_SHADOW)
            # Head
            draw.rectangle([12, 14, 20, 24], fill=SKIN)
            draw.rectangle([10, 12, 22, 16], fill=RED_BANDANA)
            # Eyes
            draw.rectangle([13, 18, 15, 20], fill=BLACK)
            draw.rectangle([17, 18, 19, 20], fill=BLACK)
            # Legs spread for stability
            draw.rectangle([6, 36, 12, 46], fill=PANTS)
            draw.rectangle([20, 36, 26, 46], fill=PANTS)
            draw.rectangle([6, 44, 12, 48], fill=BOOTS)
            draw.rectangle([20, 44, 26, 48], fill=BOOTS)
            # Arms gripping anchor
            draw.rectangle([4, 28, 8, 36], fill=SKIN)
            draw.rectangle([24, 28, 28, 36], fill=SKIN)
            # Anchor embedded in ground
            draw.rectangle([15, 32, 17, 46], fill=ANCHOR_MID)
            draw.ellipse([13, 30, 19, 36], outline=ANCHOR_MID, width=2)
            # Flukes partly in ground
            draw.polygon([(10, 46), (16, 40), (16, 44)], fill=ANCHOR_DARK)
            draw.polygon([(22, 46), (16, 40), (16, 44)], fill=ANCHOR_LIGHT)
            # Impact lines
            draw.line([2, 46, 6, 42], fill=WHITE, width=1)
            draw.line([26, 42, 30, 46], fill=WHITE, width=1)
            draw.line([0, 44, 4, 44], fill=WHITE, width=1)
            draw.line([28, 44, 32, 44], fill=WHITE, width=1)

        frames.append(img)

    return frames


def create_bosun_sprite_sheet():
    """
    Create Bosun sprite sheet.
    Layout (44x64 per frame):
    Row 0: Idle (2 frames)
    Row 1: Walk (4 frames)
    Row 2: Charge (2 frames)
    Row 3: Axe Attack (3 frames)
    Row 4: Stomp (2 frames) - subtle
    Row 5: Hurt (1 frame)
    """
    frame_w, frame_h = 44, 64
    rows = 6
    max_cols = 4

    sheet = Image.new('RGBA', (frame_w * max_cols, frame_h * rows), TRANSPARENT)

    def draw_bosun_base(draw, x_off, y_off, leg_offset=0, arm_offset=0):
        """Draw the base Bosun figure."""
        # Big burly body
        # Torso (wide)
        draw.rectangle([x_off + 8, y_off + 20, x_off + 36, y_off + 44], fill=GRAY_SHIRT)
        draw.rectangle([x_off + 8, y_off + 20, x_off + 18, y_off + 44], fill=GRAY_SHIRT_SHADOW)

        # Tattered edges on shirt
        draw.rectangle([x_off + 6, y_off + 40, x_off + 10, y_off + 44], fill=GRAY_SHIRT)
        draw.rectangle([x_off + 34, y_off + 38, x_off + 38, y_off + 42], fill=GRAY_SHIRT)

        # Head (big, square jaw)
        draw.rectangle([x_off + 14, y_off + 6, x_off + 30, y_off + 22], fill=BOSUN_SKIN)
        draw.rectangle([x_off + 14, y_off + 6, x_off + 20, y_off + 22], fill=BOSUN_SKIN_SHADOW)

        # Blue bandana
        draw.rectangle([x_off + 12, y_off + 4, x_off + 32, y_off + 10], fill=BLUE_BANDANA)
        draw.rectangle([x_off + 12, y_off + 4, x_off + 20, y_off + 10], fill=BLUE_BANDANA_DARK)
        # Bandana tail
        draw.rectangle([x_off + 30, y_off + 8, x_off + 36, y_off + 14], fill=BLUE_BANDANA)

        # Eyes (mean look)
        draw.rectangle([x_off + 16, y_off + 12, x_off + 19, y_off + 15], fill=BLACK)
        draw.rectangle([x_off + 24, y_off + 12, x_off + 27, y_off + 15], fill=BLACK)

        # Stubble/beard shadow
        draw.rectangle([x_off + 16, y_off + 17, x_off + 28, y_off + 21], fill=BOSUN_SKIN_SHADOW)

        # Legs (thick)
        left_leg_x = x_off + 10 + leg_offset
        right_leg_x = x_off + 26 - leg_offset
        draw.rectangle([left_leg_x, y_off + 44, left_leg_x + 8, y_off + 58], fill=GRAY_PANTS)
        draw.rectangle([right_leg_x, y_off + 44, right_leg_x + 8, y_off + 58], fill=GRAY_PANTS)
        draw.rectangle([left_leg_x, y_off + 44, left_leg_x + 4, y_off + 58], fill=GRAY_PANTS_SHADOW)

        # Boots
        draw.rectangle([left_leg_x - 1, y_off + 56, left_leg_x + 9, y_off + 62], fill=BOOTS)
        draw.rectangle([right_leg_x - 1, y_off + 56, right_leg_x + 9, y_off + 62], fill=BOOTS)

        # Arms (muscular)
        left_arm_y = y_off + 22 + arm_offset
        right_arm_y = y_off + 22 - arm_offset
        # Left arm
        draw.rectangle([x_off + 2, left_arm_y, x_off + 10, left_arm_y + 16], fill=BOSUN_SKIN)
        draw.rectangle([x_off + 2, left_arm_y, x_off + 6, left_arm_y + 16], fill=BOSUN_SKIN_SHADOW)
        # Right arm
        draw.rectangle([x_off + 34, right_arm_y, x_off + 42, right_arm_y + 16], fill=BOSUN_SKIN)

        return right_arm_y  # Return for axe positioning

    def draw_axe(draw, x_off, y_off, raised=False, swinging=False):
        """Draw the boarding axe."""
        if raised:
            # Axe raised above head
            # Handle
            draw.rectangle([x_off + 36, y_off + 2, x_off + 40, y_off + 24], fill=AXE_HANDLE)
            # Blade
            draw.polygon([
                (x_off + 40, y_off + 4),
                (x_off + 52, y_off + 8),
                (x_off + 52, y_off + 16),
                (x_off + 40, y_off + 20)
            ], fill=AXE_BLADE)
            draw.polygon([
                (x_off + 40, y_off + 8),
                (x_off + 48, y_off + 10),
                (x_off + 48, y_off + 14),
                (x_off + 40, y_off + 16)
            ], fill=AXE_BLADE_DARK)
        elif swinging:
            # Axe swinging down
            # Handle (diagonal)
            draw.line([x_off + 38, y_off + 26, x_off + 50, y_off + 50], fill=AXE_HANDLE, width=4)
            # Blade at end
            draw.polygon([
                (x_off + 46, y_off + 46),
                (x_off + 58, y_off + 54),
                (x_off + 54, y_off + 62),
                (x_off + 42, y_off + 54)
            ], fill=AXE_BLADE)
        else:
            # Axe at rest (held down)
            # Handle
            draw.rectangle([x_off + 38, y_off + 28, x_off + 42, y_off + 52], fill=AXE_HANDLE)
            # Blade
            draw.polygon([
                (x_off + 42, y_off + 44),
                (x_off + 54, y_off + 48),
                (x_off + 54, y_off + 56),
                (x_off + 42, y_off + 52)
            ], fill=AXE_BLADE)
            draw.polygon([
                (x_off + 42, y_off + 46),
                (x_off + 50, y_off + 49),
                (x_off + 50, y_off + 53),
                (x_off + 42, y_off + 50)
            ], fill=AXE_BLADE_DARK)

    draw = ImageDraw.Draw(sheet)

    # Row 0: Idle (2 frames) - slight breathing motion
    for i in range(2):
        x = i * frame_w
        y = 0
        arm_off = 1 if i == 1 else 0
        draw_bosun_base(draw, x, y, arm_offset=arm_off)
        draw_axe(draw, x, y)

    # Row 1: Walk (4 frames)
    for i in range(4):
        x = i * frame_w
        y = frame_h
        leg_off = [0, 2, 0, -2][i]
        draw_bosun_base(draw, x, y, leg_offset=leg_off)
        draw_axe(draw, x, y)

    # Row 2: Charge (2 frames) - leaning forward
    for i in range(2):
        x = i * frame_w
        y = frame_h * 2
        # Draw leaning forward body
        # Torso tilted
        draw.polygon([
            (x + 12, y + 18),
            (x + 38, y + 22),
            (x + 36, y + 44),
            (x + 10, y + 42)
        ], fill=GRAY_SHIRT)
        # Head forward
        draw.rectangle([x + 18, y + 6, x + 34, y + 20], fill=BOSUN_SKIN)
        draw.rectangle([x + 14, y + 4, x + 36, y + 10], fill=BLUE_BANDANA)
        draw.rectangle([x + 34, y + 8, x + 40, y + 14], fill=BLUE_BANDANA)
        # Eyes
        draw.rectangle([x + 22, y + 12, x + 25, y + 15], fill=BLACK)
        draw.rectangle([x + 28, y + 12, x + 31, y + 15], fill=BLACK)
        # Legs running
        leg_off = 3 if i == 0 else -3
        draw.rectangle([x + 8 + leg_off, y + 42, x + 16 + leg_off, y + 58], fill=GRAY_PANTS)
        draw.rectangle([x + 24 - leg_off, y + 44, x + 32 - leg_off, y + 56], fill=GRAY_PANTS)
        draw.rectangle([x + 7 + leg_off, y + 56, x + 17 + leg_off, y + 62], fill=BOOTS)
        draw.rectangle([x + 23 - leg_off, y + 54, x + 33 - leg_off, y + 60], fill=BOOTS)
        # Arms pumping
        draw.rectangle([x + 4, y + 24 + (i * 4), x + 12, y + 38 + (i * 4)], fill=BOSUN_SKIN)
        draw.rectangle([x + 34, y + 20 - (i * 4), x + 42, y + 34 - (i * 4)], fill=BOSUN_SKIN)
        draw_axe(draw, x, y, raised=(i == 1))

    # Row 3: Axe Attack (3 frames) - wind up, swing, follow through
    for i in range(3):
        x = i * frame_w
        y = frame_h * 3
        if i == 0:
            # Wind up - axe raised
            draw_bosun_base(draw, x, y)
            draw_axe(draw, x, y, raised=True)
        elif i == 1:
            # Mid-swing
            draw_bosun_base(draw, x, y, arm_offset=-4)
            draw_axe(draw, x, y, swinging=True)
        else:
            # Follow through
            draw_bosun_base(draw, x, y, arm_offset=-2)
            draw_axe(draw, x, y)

    # Row 4: Stomp (2 frames) - subtle: one foot raised slightly, then down
    for i in range(2):
        x = i * frame_w
        y = frame_h * 4
        if i == 0:
            # One foot raised slightly
            draw_bosun_base(draw, x, y, leg_offset=0)
            # Redraw right leg raised
            draw.rectangle([x + 26, y + 42, x + 34, y + 54], fill=GRAY_PANTS)
            draw.rectangle([x + 25, y + 52, x + 35, y + 58], fill=BOOTS)
        else:
            # Both feet down, slight crouch
            # Body slightly lower
            draw.rectangle([x + 8, y + 22, x + 36, y + 46], fill=GRAY_SHIRT)
            draw.rectangle([x + 8, y + 22, x + 18, y + 46], fill=GRAY_SHIRT_SHADOW)
            draw.rectangle([x + 14, y + 8, x + 30, y + 24], fill=BOSUN_SKIN)
            draw.rectangle([x + 12, y + 6, x + 32, y + 12], fill=BLUE_BANDANA)
            draw.rectangle([x + 30, y + 10, x + 36, y + 16], fill=BLUE_BANDANA)
            draw.rectangle([x + 16, y + 14, x + 19, y + 17], fill=BLACK)
            draw.rectangle([x + 24, y + 14, x + 27, y + 17], fill=BLACK)
            # Legs spread wide
            draw.rectangle([x + 6, y + 46, x + 14, y + 58], fill=GRAY_PANTS)
            draw.rectangle([x + 28, y + 46, x + 36, y + 58], fill=GRAY_PANTS)
            draw.rectangle([x + 5, y + 56, x + 15, y + 62], fill=BOOTS)
            draw.rectangle([x + 27, y + 56, x + 37, y + 62], fill=BOOTS)
            # Arms
            draw.rectangle([x + 2, y + 26, x + 10, y + 42], fill=BOSUN_SKIN)
            draw.rectangle([x + 34, y + 26, x + 42, y + 42], fill=BOSUN_SKIN)
        draw_axe(draw, x, y)

    # Row 5: Hurt (1 frame)
    x = 0
    y = frame_h * 5
    # Recoiling pose
    draw.rectangle([x + 10, y + 22, x + 34, y + 44], fill=GRAY_SHIRT)
    draw.rectangle([x + 16, y + 8, x + 28, y + 24], fill=BOSUN_SKIN)
    draw.rectangle([x + 14, y + 6, x + 30, y + 12], fill=BLUE_BANDANA)
    # Eyes squinting in pain
    draw.line([x + 17, y + 14, x + 21, y + 14], fill=BLACK, width=2)
    draw.line([x + 23, y + 14, x + 27, y + 14], fill=BLACK, width=2)
    # Legs
    draw.rectangle([x + 12, y + 44, x + 20, y + 58], fill=GRAY_PANTS)
    draw.rectangle([x + 24, y + 44, x + 32, y + 58], fill=GRAY_PANTS)
    draw.rectangle([x + 11, y + 56, x + 21, y + 62], fill=BOOTS)
    draw.rectangle([x + 23, y + 56, x + 33, y + 62], fill=BOOTS)
    # Arms up defensively
    draw.rectangle([x + 4, y + 18, x + 12, y + 34], fill=BOSUN_SKIN)
    draw.rectangle([x + 32, y + 20, x + 40, y + 36], fill=BOSUN_SKIN)
    draw_axe(draw, x, y)

    return sheet


def main():
    # Create barrel roll frames
    barrel_frames = create_barrel_roll_frames()

    # Create anchor slam frames
    slam_frames = create_anchor_slam_frames()

    # Load existing player sprite sheet
    player_sheet = Image.open('assets/sprites/player.png')

    # Current sheet is 120x192 (rows 0-3 used)
    # We need to add row 4 (roll) and row 5 (slam)
    # Row 4: 4 frames of roll (32x48 each) = 128 wide
    # Row 5: 3 frames of slam (32x48 each) = 96 wide

    # Create new sheet with extra rows
    new_width = max(player_sheet.width, 32 * 4)  # At least 128 for roll frames
    new_height = 48 * 6  # 6 rows total

    new_sheet = Image.new('RGBA', (new_width, new_height), TRANSPARENT)

    # Paste existing content
    new_sheet.paste(player_sheet, (0, 0))

    # Add barrel roll frames (row 4)
    for i, frame in enumerate(barrel_frames):
        new_sheet.paste(frame, (i * 32, 48 * 4))

    # Add anchor slam frames (row 5)
    for i, frame in enumerate(slam_frames):
        new_sheet.paste(frame, (i * 32, 48 * 5))

    # Save updated player sheet
    new_sheet.save('assets/sprites/player.png')
    print("Updated assets/sprites/player.png with roll and slam animations")

    # Create and save bosun sprite sheet
    bosun_sheet = create_bosun_sprite_sheet()
    bosun_sheet.save('assets/sprites/bosun.png')
    print("Created assets/sprites/bosun.png")


if __name__ == '__main__':
    main()
