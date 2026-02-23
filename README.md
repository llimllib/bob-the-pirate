# Bob the Pirate 🏴‍☠️

A Megaman-style platformer where Captain Bob the Pirate battles British naval forces to collect treasure!

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
```

## Controls

| Key | Action |
|-----|--------|
| Arrow Keys / WASD | Move left/right |
| Space / W / Up | Jump |
| Q | Slash sword |
| ESC | Pause / Menu |
| Enter | Select / Confirm |

## Gameplay

- **Objective**: Collect all treasure chests in each level to unlock the exit
- **Combat**: Use your cutlass (Q) to defeat British naval enemies
- **Health**: You have 5 hearts - collect rum bottles to heal
- **Lives**: Collect pirate flags for extra lives
- **Power-ups**: Find loot chests for special abilities like the Parrot companion!

## Development

See `docs/plans/2026-02-23-bob-the-pirate-game-plan.md` for the full development roadmap.

### Project Structure

```
bob-the-pirate/
├── main.py              # Entry point
├── game/
│   ├── settings.py      # Game constants
│   ├── game.py          # Main game loop
│   ├── player.py        # Player class
│   ├── enemies.py       # Enemy classes
│   ├── level.py         # Level management
│   ├── collectibles.py  # Items and power-ups
│   ├── camera.py        # Camera system
│   └── ui.py            # HUD and menus
├── assets/              # Sprites, sounds, music
└── levels/              # Level data (JSON)
```

## License

MIT
