# Bob the Pirate - Claude Development Guide

## Project Overview

A Megaman-style platformer built with Python and Pygame. Captain Bob the Pirate battles British naval forces to collect treasure chests.

## Quick Commands

```bash
# Run the game
uv run python main.py

# Run tests
uv run python -m pytest tests/ -v

# Run linter
uv run ruff check .

# Run type checker
uv run pyright

# Run all checks (do this before committing!)
uv run ruff check . && uv run pyright && uv run python -m pytest tests/ -v

# Install dependencies
uv sync
```

## Architecture

### Core Files

- **`main.py`** - Entry point, just calls `Game().run()`
- **`game/game.py`** - Main game loop, state machine (MENU, PLAYING, PAUSED, GAME_OVER, LEVEL_COMPLETE, BOSS_DEFEATED)
- **`game/settings.py`** - All constants (speeds, sizes, colors, timings)
- **`game/player.py`** - Player class with movement, combat, health, power-up states
- **`game/enemies.py`** - Enemy classes: Sailor, Musketeer, Officer, Cannon, Admiral (boss) + projectiles
- **`game/level.py`** - Level loading from JSON, tile collision (solid + one-way platforms), entity management
- **`game/collectibles.py`** - TreasureChest, Coin, RumBottle, PirateFlag, LootChest, ExitDoor
- **`game/powerups.py`** - Parrot companion, GhostShield power-up entities
- **`game/camera.py`** - Smooth-follow camera system
- **`game/ui.py`** - HUD rendering (health, lives, treasure counter, score, power-up indicators, boss health bar)

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
- `is_boss_level` - (optional) true for boss arenas
- `tiles[]` - x,y grid positions (multiplied by TILE_SIZE), type: "solid", "platform", "decoration"
- `enemies[]` - type (sailor/musketeer/officer/cannon/admiral), position, optional params (patrol_distance, faces_right, arena_left, arena_right)
- `collectibles[]` - type (treasure/coin/rum/flag/loot), position, optional powerup type for loot chests
- `player_start` - [x, y] spawn point
- `exit` - {x, y} level exit position (not needed for boss levels)

### Tile Types
- `solid` - Full collision from all directions (brown)
- `platform` - One-way, only blocks falling player (thin, can jump through from below)
- `decoration` - No collision, visual only (green)

## Development Plan

See `docs/plans/2026-02-23-bob-the-pirate-game-plan.md` for the 12-phase roadmap.

**Current Status**: Phases 1-7 complete. Full gameplay loop with boss fight working.

**Next Up**: Phase 8 - Complete Levels (design 4 themed levels with progression)

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

### New Power-up
1. Add power-up entity class to `powerups.py` if needed (like Parrot)
2. Add to `LootChest.collect()` in `collectibles.py`
3. Add player state (e.g., `player.has_X`, `player.X_timer`)
4. Add logic in `game.py` update loop
5. Add UI indicator in `ui.py` `_draw_powerup()` or `_draw_powerup_static()`

### Current Power-ups
- **Parrot** - Follows player, auto-attacks nearby enemies (timed)
- **Grog Rage** - 2x damage multiplier (timed)
- **Ghost Shield** - Absorbs one hit (until used)
