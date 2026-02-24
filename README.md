# Bob the Pirate 🏴‍☠️

A Megaman-style platformer where Captain Bob the Pirate battles British naval forces to collect treasure!

## 🎮 Play Online

Play the game directly in your browser: **[Play Bob the Pirate](https://YOUR_USERNAME.github.io/bob-the-pirate/)**

*(Update this link after deploying to GitHub Pages)*

## Requirements

- Python 3.11+
- uv (Python package manager)

## Installation

```bash
# Clone the repository
cd bob-the-pirate

# Install dependencies with uv
uv sync
```

## Running the Game

```bash
uv run python main.py

# With debug output
uv run python main.py -v
```

## Controls

| Key | Action |
|-----|--------|
| Arrow Keys / WASD | Move left/right |
| Space / W / Up | Jump |
| Q | Slash sword |
| E | Fire cannon (when powered up) |
| Double-tap Left/Right | Barrel roll (dodge) |
| Down (in air) | Anchor slam (AoE attack) |
| ESC | Pause / Menu |
| Enter | Select / Confirm |

## Gameplay

- **Objective**: Collect all treasure chests in each level to unlock the exit
- **Combat**: Use your cutlass (Q) to defeat British naval enemies
- **Health**: You have 5 hearts - collect rum bottles to heal
- **Lives**: Collect pirate flags for extra lives
- **Power-ups**: Find loot chests for special abilities!

### Power-ups

- 🦜 **Parrot** - Auto-attacks nearby enemies
- 🛡️ **Ghost Shield** - Absorbs one hit
- 🍺 **Grog Rage** - 2x damage
- 💣 **Cannon Shot** - Ranged attacks
- ⬆️ **Double Jump** - Jump again in mid-air
- ⚔️ **Cutlass Fury** - Faster, wider attacks
- 🧲 **Treasure Magnet** - Pull collectibles toward you
- 🐒 **Monkey Mate** - Throws coconuts at enemies

## Web Deployment

The game can be played in a web browser using [pygbag](https://pygame-web.github.io/pygbag/).

### Building for Web

```bash
# Install dev dependencies
uv sync --dev

# Build for web
./scripts/build_web.sh

# Test locally (opens http://localhost:8000)
uv run pygbag .
```

### Deploying

- **GitHub Pages**: Push to `main` branch - auto-deploys via GitHub Actions
- **itch.io**: Upload `build/web.zip` as an HTML game
- **Other hosts**: Upload contents of `build/web/` to any static hosting

## Development

See `docs/plans/2026-02-23-bob-the-pirate-game-plan.md` for the full development roadmap.

### Project Structure

```
bob-the-pirate/
├── main.py              # Entry point (native + web)
├── game/
│   ├── settings.py      # Game constants
│   ├── game.py          # Main game loop
│   ├── player.py        # Player class
│   ├── enemies.py       # Enemy classes
│   ├── level.py         # Level management
│   ├── collectibles.py  # Items and power-ups
│   ├── powerups.py      # Power-up entities
│   ├── camera.py        # Camera system
│   ├── audio.py         # Sound/music manager
│   └── ui.py            # HUD and menus
├── assets/              # Sprites, sounds, music
├── levels/              # Level data (JSON)
├── scripts/             # Build scripts
└── .github/workflows/   # CI/CD (GitHub Pages deploy)
```

### Running Tests

```bash
# Run all checks
uv run ruff check . && uv run pyright && uv run python -m pytest tests/ -v
```

## License

MIT
