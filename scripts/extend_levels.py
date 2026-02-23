#!/usr/bin/env python3
"""Extend levels to make them longer with more content."""

import json

TILE_SIZE = 32


def extend_level1():
    """Extend Port Town from 2400 to 4000 pixels."""
    with open('levels/level1.json', 'r') as f:
        level = json.load(f)

    # Current width is 2400 (75 tiles), extend to 4000 (125 tiles)
    old_width = level['width']
    new_width = 4000
    level['width'] = new_width

    # Find the rightmost ground tile x position
    max_ground_x = max(t['x'] for t in level['tiles'] if t['y'] == 17)

    # Extend ground from tile 50 to tile 124
    for x in range(max_ground_x + 1, 125):
        level['tiles'].append({'x': x, 'y': 17, 'type': 'solid'})
        level['tiles'].append({'x': x, 'y': 18, 'type': 'solid'})

    # Add new platforming sections
    # Section 1: Stepping stones (tiles 52-60)
    for x in [52, 55, 58]:
        level['tiles'].append({'x': x, 'y': 14, 'type': 'solid'})
        level['tiles'].append({'x': x + 1, 'y': 14, 'type': 'solid'})

    # Section 2: High platform (tiles 65-72)
    for x in range(65, 73):
        level['tiles'].append({'x': x, 'y': 10, 'type': 'platform'})

    # Section 3: Staircase down (tiles 78-85)
    for i, x in enumerate(range(78, 86)):
        y = 12 + (i // 2)
        level['tiles'].append({'x': x, 'y': y, 'type': 'solid'})

    # Section 4: Gap with platforms (tiles 90-100)
    # Remove ground tiles for gap
    level['tiles'] = [t for t in level['tiles'] if not (92 <= t['x'] <= 97 and t['y'] in [17, 18])]
    # Add platforms over gap
    for x in [92, 95]:
        level['tiles'].append({'x': x, 'y': 14, 'type': 'platform'})
        level['tiles'].append({'x': x + 1, 'y': 14, 'type': 'platform'})

    # Section 5: Final area platforms (tiles 105-120)
    for x in range(108, 114):
        level['tiles'].append({'x': x, 'y': 13, 'type': 'solid'})
    for x in range(116, 122):
        level['tiles'].append({'x': x, 'y': 11, 'type': 'platform'})

    # Add new enemies
    new_enemies = [
        {'type': 'sailor', 'x': 1700, 'y': 496, 'patrol_distance': 100},
        {'type': 'sailor', 'x': 2100, 'y': 496, 'patrol_distance': 120},
        {'type': 'musketeer', 'x': 2200, 'y': 288},  # On high platform
        {'type': 'sailor', 'x': 2600, 'y': 496, 'patrol_distance': 80},
        {'type': 'sailor', 'x': 3100, 'y': 496, 'patrol_distance': 100},
        {'type': 'musketeer', 'x': 3500, 'y': 400},
    ]
    level['enemies'].extend(new_enemies)

    # Add new collectibles
    new_collectibles = [
        {'type': 'treasure', 'x': 1800, 'y': 424},
        {'type': 'treasure', 'x': 2240, 'y': 280},  # On high platform
        {'type': 'treasure', 'x': 3000, 'y': 424},
        {'type': 'coin', 'x': 1680, 'y': 420},
        {'type': 'coin', 'x': 1720, 'y': 420},
        {'type': 'coin', 'x': 1760, 'y': 420},
        {'type': 'coin', 'x': 2080, 'y': 290},  # Over platforms
        {'type': 'coin', 'x': 2120, 'y': 290},
        {'type': 'coin', 'x': 2160, 'y': 290},
        {'type': 'coin', 'x': 2950, 'y': 420},
        {'type': 'coin', 'x': 3000, 'y': 420},
        {'type': 'coin', 'x': 3050, 'y': 420},
        {'type': 'rum', 'x': 2500, 'y': 496},
        {'type': 'loot', 'x': 3600, 'y': 320, 'powerup': 'double_jump'},
    ]
    level['collectibles'].extend(new_collectibles)

    # Move exit to end
    level['exit'] = {'x': 3850, 'y': 480}

    with open('levels/level1.json', 'w') as f:
        json.dump(level, f, indent=2)
    print(f"Level 1: Extended from {old_width} to {new_width} pixels")


def extend_level2():
    """Extend HMS Revenge from 2800 to 4200 pixels."""
    with open('levels/level2.json', 'r') as f:
        level = json.load(f)

    old_width = level['width']
    new_width = 4200
    level['width'] = new_width

    # Find current max x for deck tiles
    max_x = max(t['x'] for t in level['tiles'])

    # Extend the ship deck
    deck_y = 17  # Main deck level
    for x in range(max_x + 1, 131):
        level['tiles'].append({'x': x, 'y': deck_y, 'type': 'solid'})
        level['tiles'].append({'x': x, 'y': deck_y + 1, 'type': 'solid'})

    # Add more ship interior structures
    # Cargo hold section (tiles 90-105)
    for x in range(92, 100):
        level['tiles'].append({'x': x, 'y': 14, 'type': 'solid'})
    for x in range(95, 103):
        level['tiles'].append({'x': x, 'y': 11, 'type': 'platform'})

    # Rigging platforms (tiles 108-120)
    for x in [108, 112, 116, 120]:
        level['tiles'].append({'x': x, 'y': 12, 'type': 'platform'})
        level['tiles'].append({'x': x + 1, 'y': 12, 'type': 'platform'})

    # Captain's quarters approach (tiles 122-130)
    for x in range(124, 130):
        level['tiles'].append({'x': x, 'y': 14, 'type': 'solid'})
        level['tiles'].append({'x': x, 'y': 15, 'type': 'solid'})

    # Add new enemies
    new_enemies = [
        {'type': 'sailor', 'x': 2900, 'y': 496, 'patrol_distance': 100},
        {'type': 'musketeer', 'x': 3100, 'y': 416},
        {'type': 'sailor', 'x': 3300, 'y': 496, 'patrol_distance': 80},
        {'type': 'cannon', 'x': 3500, 'y': 464, 'faces_right': False},
        {'type': 'officer', 'x': 3700, 'y': 496},
        {'type': 'musketeer', 'x': 3900, 'y': 350},
    ]
    level['enemies'].extend(new_enemies)

    # Add new collectibles
    new_collectibles = [
        {'type': 'treasure', 'x': 3000, 'y': 320},
        {'type': 'treasure', 'x': 3400, 'y': 424},
        {'type': 'treasure', 'x': 3800, 'y': 360},
        {'type': 'coin', 'x': 2950, 'y': 350},
        {'type': 'coin', 'x': 3000, 'y': 350},
        {'type': 'coin', 'x': 3050, 'y': 350},
        {'type': 'coin', 'x': 3450, 'y': 496},
        {'type': 'coin', 'x': 3500, 'y': 496},
        {'type': 'coin', 'x': 3550, 'y': 496},
        {'type': 'rum', 'x': 3200, 'y': 496},
        {'type': 'loot', 'x': 4000, 'y': 400, 'powerup': 'grog'},
    ]
    level['collectibles'].extend(new_collectibles)

    # Move exit
    level['exit'] = {'x': 4050, 'y': 480}

    with open('levels/level2.json', 'w') as f:
        json.dump(level, f, indent=2)
    print(f"Level 2: Extended from {old_width} to {new_width} pixels")


def extend_level3():
    """Extend Cliff Fortress from 2400 to 3600 pixels (vertical level, make wider)."""
    with open('levels/level3.json', 'r') as f:
        level = json.load(f)

    old_width = level['width']
    new_width = 3600
    old_height = level['height']
    new_height = 1000  # Make it taller too
    level['width'] = new_width
    level['height'] = new_height

    # Find max x from ground tiles (y=24 in this level)
    ground_tiles = [t for t in level['tiles'] if t['y'] == 24]
    max_x = max(t['x'] for t in ground_tiles) if ground_tiles else 20

    # Extend ground from current max to new area
    for x in range(max_x + 1, 75):
        level['tiles'].append({'x': x, 'y': 24, 'type': 'solid'})

    # Add ascending cliff sections continuing from existing level
    # More platforms going right and up
    new_platforms = [
        # Continue climb from existing (around x=50-70)
        (52, 20), (53, 20), (54, 20),
        (58, 17), (59, 17), (60, 17),
        (55, 14), (56, 14), (57, 14),
        (62, 11), (63, 11), (64, 11),
        (58, 8), (59, 8),
        (65, 6), (66, 6), (67, 6),
        # Extended section (x=70-100)
        (72, 22), (73, 22), (74, 22),
        (78, 19), (79, 19), (80, 19),
        (75, 16), (76, 16),
        (82, 13), (83, 13), (84, 13),
        (78, 10), (79, 10),
        (86, 7), (87, 7), (88, 7),
        (90, 5), (91, 5), (92, 5),
        # Final approach
        (95, 8), (96, 8), (97, 8),
        (100, 5), (101, 5), (102, 5),
    ]
    for x, y in new_platforms:
        level['tiles'].append({'x': x, 'y': y, 'type': 'platform'})

    # Final fortress platform
    for x in range(105, 112):
        level['tiles'].append({'x': x, 'y': 4, 'type': 'solid'})
        level['tiles'].append({'x': x, 'y': 5, 'type': 'solid'})

    # Add new enemies
    new_enemies = [
        {'type': 'sailor', 'x': 1800, 'y': 736, 'patrol_distance': 80},
        {'type': 'musketeer', 'x': 1900, 'y': 608},
        {'type': 'musketeer', 'x': 2100, 'y': 480},
        {'type': 'sailor', 'x': 2300, 'y': 704, 'patrol_distance': 60},
        {'type': 'cannon', 'x': 2500, 'y': 350, 'faces_right': False},
        {'type': 'officer', 'x': 2800, 'y': 250},
        {'type': 'musketeer', 'x': 3100, 'y': 200},
    ]
    level['enemies'].extend(new_enemies)

    # Add new collectibles
    new_collectibles = [
        {'type': 'treasure', 'x': 1750, 'y': 600},
        {'type': 'treasure', 'x': 2050, 'y': 450},
        {'type': 'treasure', 'x': 2400, 'y': 300},
        {'type': 'treasure', 'x': 3000, 'y': 180},
        {'type': 'coin', 'x': 1700, 'y': 640},
        {'type': 'coin', 'x': 1750, 'y': 640},
        {'type': 'coin', 'x': 2000, 'y': 500},
        {'type': 'coin', 'x': 2050, 'y': 500},
        {'type': 'coin', 'x': 2350, 'y': 350},
        {'type': 'coin', 'x': 2700, 'y': 280},
        {'type': 'rum', 'x': 2200, 'y': 400},
        {'type': 'loot', 'x': 3200, 'y': 150, 'powerup': 'cannon_shot'},
    ]
    level['collectibles'].extend(new_collectibles)

    # Move exit to top of fortress
    level['exit'] = {'x': 3400, 'y': 96}

    with open('levels/level3.json', 'w') as f:
        json.dump(level, f, indent=2)
    print(f"Level 3: Extended from {old_width}x{old_height} to {new_width}x{new_height} pixels")


def extend_level4():
    """Extend The Armory (Miniboss) from 1200 to 2000 pixels."""
    with open('levels/level4.json', 'r') as f:
        level = json.load(f)

    old_width = level['width']
    new_width = 2000
    level['width'] = new_width

    # Extend ground
    max_x = max(t['x'] for t in level['tiles'] if t['y'] == 17)
    for x in range(max_x + 1, 62):
        level['tiles'].append({'x': x, 'y': 17, 'type': 'solid'})
        level['tiles'].append({'x': x, 'y': 18, 'type': 'solid'})

    # Add pre-boss gauntlet area
    # Weapon racks (platforms)
    for x in [40, 44, 48]:
        level['tiles'].append({'x': x, 'y': 14, 'type': 'platform'})
        level['tiles'].append({'x': x + 1, 'y': 14, 'type': 'platform'})

    # High catwalks
    for x in range(42, 48):
        level['tiles'].append({'x': x, 'y': 10, 'type': 'platform'})

    # Add enemies before boss
    new_enemies = [
        {'type': 'sailor', 'x': 1300, 'y': 496, 'patrol_distance': 80},
        {'type': 'musketeer', 'x': 1450, 'y': 416},
        {'type': 'sailor', 'x': 1600, 'y': 496, 'patrol_distance': 60},
    ]
    level['enemies'].extend(new_enemies)

    # Update bosun arena bounds
    for enemy in level['enemies']:
        if enemy.get('type') == 'bosun':
            enemy['arena_left'] = 1700
            enemy['arena_right'] = 1950
            enemy['x'] = 1800

    # Add collectibles
    new_collectibles = [
        {'type': 'treasure', 'x': 1350, 'y': 424},
        {'type': 'coin', 'x': 1280, 'y': 496},
        {'type': 'coin', 'x': 1320, 'y': 496},
        {'type': 'coin', 'x': 1360, 'y': 496},
        {'type': 'rum', 'x': 1500, 'y': 300},
        {'type': 'loot', 'x': 1550, 'y': 416, 'powerup': 'cutlass_fury'},
    ]
    level['collectibles'].extend(new_collectibles)

    # Move exit
    level['exit'] = {'x': 1920, 'y': 480}

    with open('levels/level4.json', 'w') as f:
        json.dump(level, f, indent=2)
    print(f"Level 4: Extended from {old_width} to {new_width} pixels")


def extend_level5():
    """Extend Governor's Mansion from 3200 to 4800 pixels."""
    with open('levels/level5.json', 'r') as f:
        level = json.load(f)

    old_width = level['width']
    new_width = 4800
    level['width'] = new_width

    # Extend ground
    max_x = max(t['x'] for t in level['tiles'] if t['y'] == 17)
    for x in range(max_x + 1, 150):
        level['tiles'].append({'x': x, 'y': 17, 'type': 'solid'})
        level['tiles'].append({'x': x, 'y': 18, 'type': 'solid'})

    # Add mansion interior sections
    # Ballroom (tiles 105-120)
    for x in range(105, 121):
        level['tiles'].append({'x': x, 'y': 14, 'type': 'solid'})
    # Chandeliers (platforms)
    for x in [108, 114, 120]:
        level['tiles'].append({'x': x, 'y': 9, 'type': 'platform'})
        level['tiles'].append({'x': x + 1, 'y': 9, 'type': 'platform'})

    # Grand staircase (tiles 125-135)
    for i, x in enumerate(range(125, 136)):
        y = 17 - (i // 2)
        level['tiles'].append({'x': x, 'y': y, 'type': 'solid'})
        if i % 2 == 0:
            level['tiles'].append({'x': x, 'y': y + 1, 'type': 'solid'})

    # Upper gallery (tiles 138-148)
    for x in range(138, 149):
        level['tiles'].append({'x': x, 'y': 10, 'type': 'solid'})
        level['tiles'].append({'x': x, 'y': 11, 'type': 'solid'})

    # Add enemies
    new_enemies = [
        {'type': 'officer', 'x': 3400, 'y': 416},
        {'type': 'musketeer', 'x': 3600, 'y': 260},
        {'type': 'sailor', 'x': 3800, 'y': 496, 'patrol_distance': 100},
        {'type': 'officer', 'x': 4000, 'y': 496},
        {'type': 'cannon', 'x': 4200, 'y': 300, 'faces_right': False},
        {'type': 'musketeer', 'x': 4400, 'y': 288},
        {'type': 'officer', 'x': 4600, 'y': 288},
    ]
    level['enemies'].extend(new_enemies)

    # Add collectibles
    new_collectibles = [
        {'type': 'treasure', 'x': 3500, 'y': 424},
        {'type': 'treasure', 'x': 3900, 'y': 260},
        {'type': 'treasure', 'x': 4300, 'y': 288},
        {'type': 'treasure', 'x': 4550, 'y': 260},
        {'type': 'coin', 'x': 3450, 'y': 496},
        {'type': 'coin', 'x': 3500, 'y': 496},
        {'type': 'coin', 'x': 3550, 'y': 496},
        {'type': 'coin', 'x': 3850, 'y': 300},
        {'type': 'coin', 'x': 3900, 'y': 300},
        {'type': 'coin', 'x': 4100, 'y': 496},
        {'type': 'coin', 'x': 4150, 'y': 496},
        {'type': 'rum', 'x': 4050, 'y': 300},
        {'type': 'flag', 'x': 4500, 'y': 260},
        {'type': 'loot', 'x': 4650, 'y': 260, 'powerup': 'magnet'},
    ]
    level['collectibles'].extend(new_collectibles)

    # Move exit
    level['exit'] = {'x': 4700, 'y': 288}

    with open('levels/level5.json', 'w') as f:
        json.dump(level, f, indent=2)
    print(f"Level 5: Extended from {old_width} to {new_width} pixels")


def main():
    print("Extending levels...")
    extend_level1()
    extend_level2()
    extend_level3()
    extend_level4()
    extend_level5()
    print("Done! All levels extended.")


if __name__ == '__main__':
    main()
