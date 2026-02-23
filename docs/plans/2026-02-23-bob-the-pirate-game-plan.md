# Bob the Pirate - Game Development Plan

**Created**: February 23, 2026  
**Type**: Megaman-style Platformer  
**Tech Stack**: Python, Pygame, uv

---

## 🏴‍☠️ Game Overview

A side-scrolling platformer where Captain Bob the Pirate battles British naval forces to collect treasure chests. Tight, responsive controls inspired by Megaman. The player must collect all treasure chests in each level to unlock the exit.

---

## 🎮 Controls

| Key | Action |
|-----|--------|
| Arrow Keys / WASD | Move left/right |
| Space / W / Up | Jump |
| Q | Slash sword |
| ESC | Pause |

---

## 🏴‍☠️ Player: Captain Bob

- **Health**: 5 hearts
- **Attack**: Cutlass slash (short range, quick)
- **Movement**: Run, jump, double-jump (unlockable)
- **Invincibility frames**: Brief immunity after taking damage

---

## ⚔️ Enemies

| Enemy | Behavior | Health |
|-------|----------|--------|
| **Sailor** | Patrols back and forth | 1 hit |
| **Musketeer** | Stationary, shoots musket balls | 2 hits |
| **Officer** | Chases player, sword attacks | 3 hits |
| **Cannon** | Stationary, fires arcing cannonballs | 2 hits |
| **Boss: Admiral** | Pattern-based boss attacks | 10 hits |

---

## 💎 Collectibles & Power-ups

### Required
- **Treasure Chests** - Collect all to complete level

### Optional Pickups
- **Gold Coins** - Score/currency
- **Rum Bottles** - Restore 1 heart
- **Pirate Flag** - Extra life

### Power-ups (from Loot Chests)
- **Parrot Companion** - Follows Bob, attacks nearby enemies automatically
- **Grog Rage** - Temporary damage boost
- **Ghost Ship Shield** - Absorbs one hit

---

## 🗺️ Levels

### World 1: Port Town (Tutorial)
- Basic platforms, simple jumps
- Enemies: Sailors only
- 3 treasure chests

### World 2: HMS Revenge (Ship)
- Moving/swaying platforms
- Enemies: Sailors, Musketeers
- 4 treasure chests

### World 3: Cliff Fortress
- Vertical sections, cannons
- Enemies: All types
- 5 treasure chests

### World 4: Governor's Mansion (Final)
- All mechanics combined
- Boss: Admiral Blackwood
- 6 treasure chests

---

## 📁 Project Structure

```
bob-the-pirate/
├── pyproject.toml
├── main.py
├── game/
│   ├── __init__.py
│   ├── settings.py
│   ├── game.py
│   ├── player.py
│   ├── enemies.py
│   ├── level.py
│   ├── collectibles.py
│   ├── ui.py
│   └── camera.py
├── assets/
│   ├── sprites/
│   ├── tiles/
│   ├── sounds/
│   └── music/
├── levels/
│   └── level1.json
└── docs/
    └── plans/
```

---

# Development Phases

## Phase 1: Foundation & Player Movement
**Estimated Time**: 1 Claude session

### Goals
- [x] Set up project with uv and pygame
- [x] Create project skeleton
- [ ] Implement game window and main loop
- [ ] Player sprite (placeholder rectangle)
- [ ] Horizontal movement (left/right)
- [ ] Gravity and jumping
- [ ] Basic ground collision
- [ ] Camera following player

### Deliverable
A player character that can run and jump on a flat ground surface.

---

## Phase 2: Level System & Tiles
**Estimated Time**: 1 Claude session

### Goals
- [ ] Tile-based level loading from JSON
- [ ] Platform collision detection
- [ ] Multiple platform types (solid, one-way)
- [ ] Level boundaries
- [ ] Simple test level with varied platforms
- [ ] Death plane (falling off screen)

### Deliverable
A complete test level with platforms the player can navigate.

---

## Phase 3: Combat System
**Estimated Time**: 1 Claude session

### Goals
- [ ] Sword slash attack (Q key)
- [ ] Attack hitbox and timing
- [ ] Attack animation/visual feedback
- [ ] Player health system
- [ ] Damage and invincibility frames
- [ ] Health UI display
- [ ] Death and respawn

### Deliverable
Player can attack and take damage with visual feedback.

---

## Phase 4: Basic Enemies
**Estimated Time**: 1 Claude session

### Goals
- [ ] Enemy base class
- [ ] Sailor enemy (patrol AI)
- [ ] Enemy-player collision (damage)
- [ ] Enemy takes damage from sword
- [ ] Enemy death/removal
- [ ] Musketeer enemy (shoots projectiles)
- [ ] Projectile system

### Deliverable
Two enemy types that can hurt and be hurt by the player.

---

## Phase 5: Collectibles & Level Completion
**Estimated Time**: 1 Claude session

### Goals
- [ ] Treasure chest collectible
- [ ] Chest collection counter UI
- [ ] Level completion logic (all chests = exit unlocks)
- [ ] Exit door/portal
- [ ] Gold coins (score)
- [ ] Rum bottles (health restore)
- [ ] Pirate flags (extra life)

### Deliverable
Complete gameplay loop: collect all chests, exit level.

---

## Phase 6: Power-up System & Parrot
**Estimated Time**: 1 Claude session

### Goals
- [ ] Loot chest (special chest with power-ups)
- [ ] Power-up base class
- [ ] Parrot companion power-up
  - Follows player
  - Attacks nearby enemies
  - Duration-based or permanent per level
- [ ] Visual indicator for active power-ups
- [ ] Additional power-ups (Grog Rage, Shield)

### Deliverable
Working parrot companion and power-up system.

---

## Phase 7: Advanced Enemies & Boss
**Estimated Time**: 1 Claude session

### Goals
- [ ] Officer enemy (chasing AI)
- [ ] Cannon enemy (arcing projectiles)
- [ ] Boss: Admiral Blackwood
  - Health bar
  - Multiple attack patterns
  - Phase changes
- [ ] Boss arena/room

### Deliverable
All enemy types including a functional boss fight.

---

## Phase 8: Complete Levels
**Estimated Time**: 1-2 Claude sessions

### Goals
- [ ] Design and build Level 1 (Port Town)
- [ ] Design and build Level 2 (HMS Revenge)
- [ ] Design and build Level 3 (Cliff Fortress)
- [ ] Design and build Level 4 (Governor's Mansion)
- [ ] Level progression system
- [ ] Level select screen

### Deliverable
Four complete, playable levels with increasing difficulty.

---

## Phase 9: Menus & UI Polish
**Estimated Time**: 1 Claude session

### Goals
- [ ] Title screen
- [ ] Pause menu
- [ ] Game over screen
- [ ] Victory screen
- [ ] Level intro cards
- [ ] Improved HUD design
- [ ] Screen transitions

### Deliverable
Complete menu system and polished UI.

---

## Phase 10: Art & Animation
**Estimated Time**: 1-2 Claude sessions

### Goals
- [ ] Player sprite sheet (idle, run, jump, attack)
- [ ] Enemy sprites
- [ ] Tile set (ground, platforms, decorations)
- [ ] Background art (parallax layers)
- [ ] Animation system
- [ ] Particle effects (sword slash, damage, coins)

### Deliverable
Cohesive pixel art visual style throughout.

---

## Phase 11: Audio
**Estimated Time**: 1 Claude session

### Goals
- [ ] Sound effects
  - Jump, land
  - Sword slash, hit
  - Collect item
  - Damage taken
  - Enemy death
- [ ] Background music (per level)
- [ ] Audio manager with volume control

### Deliverable
Full audio experience.

---

## Phase 12: Polish & Release
**Estimated Time**: 1 Claude session

### Goals
- [ ] Bug fixes
- [ ] Difficulty balancing
- [ ] Performance optimization
- [ ] Save system (optional)
- [ ] README with instructions
- [ ] Package for distribution

### Deliverable
Complete, polished game ready to share.

---

## Notes

- Each phase builds on previous phases
- Placeholder art (colored rectangles) is fine until Phase 10
- Test frequently to catch bugs early
- Prioritize game feel (controls should feel snappy like Megaman)
