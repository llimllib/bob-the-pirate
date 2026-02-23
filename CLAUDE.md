# Bob the Pirate - Claude Development Guide

## Project Overview

A Megaman-style platformer built with Python and Pygame. Captain Bob the Pirate battles British naval forces to collect treasure chests.

## Quick Commands

```bash
# Run the game
uv run python main.py

# Install dependencies
uv sync
```

## Architecture

### Core Files

- **`main.py`** - Entry point, just calls `Game().run()`
- **`game/game.py`** - Main game loop, state machine (MENU, PLAYING, PAUSED, GAME_OVER)
- **`game/settings.py`** - All constants (speeds, sizes, colors, timings)
- **`game/player.py`** - Player class with movement, combat, health
- **`game/enemies.py`** - Enemy classes: Sailor, Musketeer, Officer, Cannon + projectiles
- **`game/level.py`** - Level loading, tile collision, entity management
- **`game/collectibles.py`** - TreasureChest, Coin, RumBottle, PirateFlag, LootChest (parrot powerup)
- **`game/camera.py`** - Smooth-follow camera system
- **`game/ui.py`** - HUD rendering (health, lives, treasure counter)

### Game Flow

1. `Game.run()` → main loop at 60 FPS
2. `handle_events()` → keyboard input, state transitions
3. `update()` → physics, collision, enemy AI
4. `draw()` → render based on current state

### Collision System

Collision is split into X and Y passes in `game.py`:
1. Move player X → check horizontal collision
2. Move player Y → check vertical collision + set `on_ground`

### Level Format

Levels are JSON files in `levels/`. See `levels/level1.json` for structure:
- `tiles[]` - x,y grid positions (multiplied by TILE_SIZE)
- `enemies[]` - type and position
- `collectibles[]` - type and position
- `player_start` - spawn point
- `exit` - level exit position

## Development Plan

See `docs/plans/2026-02-23-bob-the-pirate-game-plan.md` for the 12-phase roadmap.

**Current Status**: Phase 1 skeleton complete. Player can move, jump, attack. Test level with platforms.

**Next Up**: Phase 2 - Level System & Tiles (proper level loading from JSON)

## Code Conventions

- Type hints on function signatures
- Docstrings on classes and public methods
- Constants in SCREAMING_SNAKE_CASE in `settings.py`
- Sprites inherit from `pygame.sprite.Sprite`
- All drawable objects have `draw(surface, camera_offset)` method

## Key Constants (settings.py)

| Constant | Value | Notes |
|----------|-------|-------|
| TILE_SIZE | 32 | Base unit for level grid |
| PLAYER_SPEED | 5 | Horizontal movement |
| PLAYER_JUMP_POWER | -15 | Negative = upward |
| GRAVITY | 0.8 | Applied per frame |
| ATTACK_DURATION | 15 | Frames sword is active |
| INVINCIBILITY_FRAMES | 60 | 1 second immunity after hit |

## Adding New Features

### New Enemy Type
1. Add constants to `settings.py`
2. Create class in `enemies.py` inheriting from `Enemy`
3. Override `update(player_rect)` for AI behavior
4. Add to level JSON and level loader

### New Collectible
1. Create class in `collectibles.py` inheriting from `Collectible`
2. Override `collect(player)` returning effect dict
3. Handle effect in `level.py` or `game.py`

### New Power-up
1. Add to `LootChest.collect()` in `collectibles.py`
2. Add player state (e.g., `player.has_X`, `player.X_timer`)
3. Add logic in `game.py` update loop
4. Add UI indicator in `ui.py`
