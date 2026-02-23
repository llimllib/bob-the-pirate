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

## Phase 1: Foundation & Player Movement ✅
**Estimated Time**: 1 Claude session

### Goals
- [x] Set up project with uv and pygame
- [x] Create project skeleton
- [x] Implement game window and main loop
- [x] Player sprite (placeholder rectangle)
- [x] Horizontal movement (left/right)
- [x] Gravity and jumping
- [x] Basic ground collision
- [x] Camera following player

### Deliverable
A player character that can run and jump on a flat ground surface.

---

## Phase 2: Level System & Tiles ✅
**Estimated Time**: 1 Claude session

### Goals
- [x] Tile-based level loading from JSON
- [x] Platform collision detection
- [x] Multiple platform types (solid, one-way)
- [x] Level boundaries
- [x] Simple test level with varied platforms
- [x] Death plane (falling off screen)

### Deliverable
A complete test level with platforms the player can navigate.

---

## Phase 3: Combat System ✅
**Estimated Time**: 1 Claude session

### Goals
- [x] Sword slash attack (Q key)
- [x] Attack hitbox and timing
- [x] Attack animation/visual feedback
- [x] Player health system
- [x] Damage and invincibility frames
- [x] Health UI display
- [x] Death and respawn

### Deliverable
Player can attack and take damage with visual feedback.

---

## Phase 4: Basic Enemies ✅
**Estimated Time**: 1 Claude session

### Goals
- [x] Enemy base class
- [x] Sailor enemy (patrol AI)
- [x] Enemy-player collision (damage)
- [x] Enemy takes damage from sword
- [x] Enemy death/removal
- [x] Musketeer enemy (shoots projectiles)
- [x] Projectile system

### Deliverable
Two enemy types that can hurt and be hurt by the player.

---

## Phase 5: Collectibles & Level Completion ✅
**Estimated Time**: 1 Claude session

### Goals
- [x] Treasure chest collectible
- [x] Chest collection counter UI
- [x] Level completion logic (all chests = exit unlocks)
- [x] Exit door/portal
- [x] Gold coins (score)
- [x] Rum bottles (health restore)
- [x] Pirate flags (extra life)

### Deliverable
Complete gameplay loop: collect all chests, exit level.

---

## Phase 6: Power-up System & Parrot ✅
**Estimated Time**: 1 Claude session

### Goals
- [x] Loot chest (special chest with power-ups)
- [x] Power-up base class
- [x] Parrot companion power-up
  - Follows player
  - Attacks nearby enemies
  - Duration-based or permanent per level
- [x] Visual indicator for active power-ups
- [x] Additional power-ups (Grog Rage, Shield)

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
