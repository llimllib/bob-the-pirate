# Bob the Pirate - Claude Development Guide

## Project Overview

A Megaman-style platformer built with Python and Pygame. Captain Bob the Pirate battles British naval forces to collect treasure chests.

## Quick Commands

```bash
# Run the game
uv run python main.py

# Run the game with debug output
uv run python main.py -v

# Run tests
uv run python -m pytest tests/ -v

# Run linter
uv run ruff check .

# Run type checker
uv run pyright

# Run all checks (do this before committing!)
uv run ruff check . && uv run pyright && uv run python -m pytest tests/ -v

# Rebuild WASM build after changes (do this before committing!)
./scripts/build_web.sh

# Install dependencies
uv sync

# Build for web (WASM)
./scripts/build_web.sh

# Test web build locally (opens http://localhost:8000)
uv run pygbag .
```

## Debugging

Run with `-v` or `--verbose` to enable debug output:

```bash
uv run python main.py -v
```

This outputs player state every 30 frames (0.5s) while playing:
```
[   30] pos=(100, 496) vel=(0, 0.0) on_ground=True | anim=idle[0/2] timer=15/45 | idle | powerups: none
```

Shows:
- **Frame count** - Game frame number
- **Position/velocity** - Player physics state
- **on_ground** - Whether player is standing on a surface
- **Animation** - Current animation, frame index, and timer progress
- **Combat state** - attacking, invincible, hurt timers
- **Power-ups** - Active power-ups with remaining timers

Useful for diagnosing:
- Animation issues (check if timer progresses, frames change)
- Physics bugs (velocity, on_ground oscillation)
- State machine problems (unexpected animation switches)

## Architecture

### Core Files

- **`main.py`** - Entry point, just calls `Game().run()`
- **`game/game.py`** - Main game loop, state machine (MENU, PLAYING, PAUSED, GAME_OVER, LEVEL_COMPLETE, BOSS_DEFEATED)
- **`game/settings.py`** - All constants (speeds, sizes, colors, timings)
- **`game/player.py`** - Player class with movement, combat, health, power-up states
- **`game/enemies.py`** - Enemy classes: Sailor, Musketeer, Officer, Cannon, Bosun (miniboss), Admiral (boss) + projectiles
- **`game/level.py`** - Level loading from JSON, tile collision (solid + one-way platforms), entity management
- **`game/collectibles.py`** - TreasureChest, Coin, RumBottle, PirateFlag, LootChest, ExitDoor
- **`game/powerups.py`** - Parrot companion, GhostShield power-up entities
- **`game/camera.py`** - Smooth-follow camera system
- **`game/ui.py`** - HUD rendering (health, lives, treasure counter, score, power-up indicators, boss health bar)
- **`game/audio.py`** - Audio manager for sound effects and music playback

### Game Flow

1. `Game.run()` → main loop at 60 FPS
2. `handle_events()` → keyboard input, state transitions
3. `update()` → physics, collision, enemy AI, power-ups
4. `draw()` → render based on current state

### Collision System

Collision is split into X and Y passes in `game.py`:
1. Move player X → check horizontal collision (solid tiles only)
2. Move player Y → check vertical collision + set `on_ground`
3. One-way platforms only collide when player is falling from above

Level boundaries prevent player from walking off left/right edges.

### Level Format

Levels are JSON files in `levels/`. See `levels/level1.json` for structure:
- `name` - Level display name
- `width`, `height` - Level dimensions in pixels
- `is_boss_level` - (optional) true for boss arenas (Admiral fight)
- `requires_miniboss_defeat` - (optional) true for miniboss levels (exit unlocks when miniboss defeated instead of treasure collected)
- `tiles[]` - x,y grid positions (multiplied by TILE_SIZE), type: "solid", "platform", "decoration"
- `enemies[]` - type (sailor/musketeer/officer/cannon/bosun/admiral), position, optional params (patrol_distance, faces_right, arena_left, arena_right)
- `collectibles[]` - type (treasure/coin/rum/flag/loot), position, optional powerup type for loot chests
- `player_start` - [x, y] spawn point
- `exit` - {x, y} level exit position (not needed for boss levels)

### Tile Types
- `solid` - Full collision from all directions (brown)
- `platform` - One-way, only blocks falling player (thin, can jump through from below)
- `decoration` - No collision, visual only (green)

## Development Plan

See `docs/plans/2026-02-23-bob-the-pirate-game-plan.md` for the 12-phase roadmap.

**Current Status**: Phases 1-11 complete (except 8G). Full gameplay with 6 levels, miniboss, final boss, full audio, and polished UI.

**Levels Available**:
1. Port Town (Tutorial) - Collect treasure to exit
2. HMS Revenge (Ship) - Collect treasure to exit
3. Cliff Fortress (Vertical) - Collect treasure to exit
4. The Armory (Miniboss) - Defeat the Bosun to exit
5. Governor's Mansion (Challenge) - Collect treasure to exit
6. Admiral's Quarters (Final Boss) - Defeat the Admiral to win

**Next Up**: Phase 8G (Effects) and Phase 12 (Polish & Release)

## Code Conventions

- Type hints on function signatures
- Docstrings on classes and public methods
- Constants in SCREAMING_SNAKE_CASE in `settings.py`
- Sprites inherit from `pygame.sprite.Sprite`
- All drawable objects have `draw(surface, camera_offset)` method
- **Always write tests for new behavior** - add tests to `tests/` directory
- **Run all checks before committing**: `uv run ruff check . && uv run pyright && uv run python -m pytest tests/ -v`
- All tests must pass, ruff must report no errors, pyright must report no errors

## Key Constants (settings.py)

| Constant | Value | Notes |
|----------|-------|-------|
| TILE_SIZE | 32 | Base unit for level grid |
| PLAYER_SPEED | 5 | Horizontal movement |
| PLAYER_JUMP_POWER | -15 | Negative = upward |
| GRAVITY | 0.8 | Applied per frame |
| ATTACK_DURATION | 15 | Frames sword is active |
| INVINCIBILITY_FRAMES | 60 | 1 second immunity after hit |
| PARROT_DURATION | 600 | 10 seconds at 60 FPS |
| SFX_VOLUME | 0.7 | Default sound effect volume |
| MUSIC_VOLUME | 0.5 | Default music volume |
| BARREL_ROLL_DURATION | 15 | 0.25 seconds |
| BARREL_ROLL_COOLDOWN | 45 | 0.75 seconds |
| ANCHOR_SLAM_DAMAGE | 2 | AoE damage on landing |
| ANCHOR_SLAM_RADIUS | 50 | Damage radius in pixels |

## Level Design Guidelines

When designing levels, keep Bob's physics in mind:
- **Max jump height**: ~4.4 tiles (140 pixels) - don't require jumps higher than 4 tiles
- **Max horizontal jump**: ~5.8 tiles (187 pixels) at same height - gaps should be ≤5 tiles
- **Player size**: 32x48 pixels (1x1.5 tiles) - passages need 2+ tiles vertical clearance
- **Ground level**: Usually y=17 for 600px levels, y=20 for 700px levels, y=24 for 1000px levels

For vertical platforming sections, use stepping stone platforms spaced 3-4 tiles apart vertically and within 4-5 tiles horizontally.

## Adding New Features

### New Enemy Type
1. Add constants to `settings.py`
2. Create class in `enemies.py` inheriting from `Enemy`
3. Override `update(player_rect)` for AI behavior
4. Add to level JSON and `load_from_file()` in `level.py`

### New Collectible
1. Create class in `collectibles.py` inheriting from `Collectible`
2. Override `collect(player)` returning effect dict
3. Add to `load_from_file()` in `level.py`
4. Handle effects in `game.py` (score, power-ups)

### Playing Audio
```python
from game.audio import play_sound, play_music, stop_music

play_sound("jump")           # Play sound effect
play_music("level1.ogg")     # Start background music (loops)
stop_music()                 # Stop music
```

**Available Sounds**: jump, land, slash, hit, hurt, death, coin, treasure, powerup, health, extra_life, enemy_death, shoot, cannon, parrot_attack, shield_hit, boss_hit, boss_death, door_unlock, menu_select, menu_confirm, level_complete, game_over

**Available Music**: menu.ogg, level1.ogg, level2.ogg, level3.ogg, level4.ogg, level5.ogg, boss.ogg, victory.ogg

**Note**: All audio files are OGG format for web compatibility.

### New Power-up
1. Add power-up entity class to `powerups.py` if needed (like Parrot)
2. Add to `LootChest.collect()` in `collectibles.py`
3. Add player state (e.g., `player.has_X`, `player.X_timer`)
4. Add logic in `game.py` update loop
5. Add UI indicator in `ui.py` `_draw_powerup()` or `_draw_powerup_static()`

### Innate Abilities
Bob has these abilities from the start:
- **Barrel Roll** - Double-tap Left/Right to roll with invincibility frames (0.25s roll, 0.75s cooldown)
- **Anchor Slam** - Press Down while in air to slam down and damage all enemies in radius (2 damage, 50px radius)

### Current Power-ups
- **Parrot** - Follows player, auto-attacks nearby enemies (timed, 10s)
- **Grog Rage** - 2x damage multiplier (timed, 5s)
- **Ghost Shield** - Absorbs one hit (until used)
- **Cannon Shot** - Press E to fire cannonballs (8 ammo, 2 damage each)
- **Double Jump** - Jump again in mid-air (timed, 20s)
- **Cutlass Fury** - Faster attacks, 50% wider hitbox (timed, 10s)
- **Treasure Magnet** - Pull collectibles toward you (timed, 30s)
- **Monkey Mate** - Throws coconuts at enemies, longer range than parrot (timed, 12s)
