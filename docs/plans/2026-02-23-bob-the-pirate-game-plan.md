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
| **Boss: Vice-Admiral Garp** | Pattern-based boss attacks | 10 hits |

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
- Boss: Vice-Admiral Garp
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

## Phase 7: Advanced Enemies & Boss ✅
**Estimated Time**: 1 Claude session

### Goals
- [x] Officer enemy (chasing AI with sword attacks)
- [x] Cannon enemy (arcing projectiles)
- [x] Boss: Vice-Admiral Garp
  - Health bar with phase indicator
  - Multiple attack patterns (sword, pistol, charge, summon)
  - 3 phase changes with increasing aggression
- [x] Boss arena/room (levels/boss_arena.json)
- [x] Test suite for enemies and boss (tests/)

### Deliverable
All enemy types including a functional boss fight.

---

## Phase 8: Art & Animation (NES-Style 8-bit)
**Estimated Time**: 1-2 Claude sessions

### Phase 8A: Animation System ✅
- [x] Create `game/animation.py` with Animation and SpriteSheet classes
- [x] Support for loading sprite sheets (horizontal strip or grid)
- [x] Frame timing, looping, one-shot animations
- [x] AnimatedSprite manager class with facing direction support
- [x] Placeholder frame generator for testing
- [x] Tests in `tests/test_animation.py`

### Phase 8B: Player Sprites - Captain Bob (32x48) ✅
- [x] Idle animation (2 frames)
- [x] Run animation (4 frames)
- [x] Jump frame (1 frame, rising)
- [x] Fall frame (1 frame, falling)
- [x] Attack/slash animation (3 frames)
- [x] Hurt frame (1 frame)
- [x] Integrate into Player class
- [x] Sprite generator tool: `tools/generate_player_sprites.py`
- [x] Comprehensive Player tests: `tests/test_player.py` (48 tests)

### Phase 8C: Tiles & Environment (32x32) ✅
- [x] Solid ground tiles (top, middle, edges, corners)
- [x] One-way platform tile
- [x] Decorations (crates, barrels, ropes, anchors)
- [x] Update Level class to use tile sprites
- [x] Background layers (sky, clouds, distant scenery)

### Phase 8D: Collectibles & Items ✅
- [x] Treasure chest (32x24)
- [x] Gold coin (16x16) - spinning animation (4 frames)
- [x] Rum bottle (12x20)
- [x] Pirate flag (24x32)
- [x] Loot chest/golden chest (32x24)
- [x] Exit door locked/unlocked (32x64)
- [x] Integrate into collectibles classes
- [x] Sprite generator tool: `tools/generate_collectible_sprites.py`
- [x] Sprite manager: `game/collectible_sprites.py`
- [x] Tests in `tests/test_collectibles.py` (25 tests)

### Phase 8E: Enemy Sprites ✅
- [x] Sailor (28x44) - walk cycle (2 frames), hurt
- [x] Musketeer (28x44) - idle, shooting (2 frames)
- [x] Officer (32x48) - walk cycle (2 frames), attack (2 frames)
- [x] Cannon (32x32) - static, firing (2 frames)
- [x] Projectiles: musket ball (8x8), cannonball (12x12), admiral bullet (10x10)
- [x] Integrate into enemy classes
- [x] Sprite generator tool: `tools/generate_enemy_sprites.py`
- [x] Tests for enemy animations in `tests/test_enemies.py` (41 tests)

### Phase 8F: Boss & Power-ups ✅
- [x] Vice-Admiral Garp (48x64) - idle, walk (2 frames), sword attack (3 frames), pistol shot (2 frames), charge, stunned
- [x] Hat with five red feathers
- [x] Parrot companion (16x12) - flying (2 frames), attack (2 frames)
- [x] Ghost shield effect (kept programmatic)
- [x] Integrate into Admiral and power-up classes
- [x] Sprite generator tools: `tools/generate_boss_sprites.py`, `tools/generate_parrot_sprites.py`

### Phase 8G: Effects & Polish
- [ ] Sword slash effect sprite/animation
- [ ] Damage particles
- [ ] Coin collect sparkle
- [ ] Death/poof effect for enemies
- [ ] Any remaining visual polish

### Art Style Guidelines
- **NES-style 8-bit aesthetic, cartoony/whimsical tone (like Shovel Knight)**
- Limited color palette (8-12 colors per sprite, NES-inspired)
- Small sprite sizes: 16x16, 16x24, or 16x32 pixels
- Crisp pixel edges, no anti-aliasing
- Bold outlines for readability
- Expressive animations with limited frames (2-4 frames per animation)

### Character Design Specs

**Captain Bob the Pirate (Player)**
- Classic pirate look: red bandana, white/cream shirt, brown pants, black boots
- Red bandana (no hat)
- Goatee
- Burly/stocky build
- Curved saber (default weapon)
- Future: Katana or straight sword as loot chest power-up

**British Naval Enemies**
- Traditional navy blue coats with white/gold trim
- Sailor: Simple blue uniform, cap
- Musketeer: Blue coat, tricorn hat, musket
- Officer: Fancier blue coat with gold trim, sword
- Cannon: Stationary artillery piece

**Vice-Admiral Garp (Boss)**
- Large, imposing figure
- Fancy naval hat with feathers
- Elaborate blue coat with gold epaulettes
- Intimidating presence

### Deliverable
Cohesive NES-style pixel art visual style throughout.

---

## Phase 9: Complete Levels ✅
**Estimated Time**: 1-2 Claude sessions

### Goals
- [x] Design and build Level 1 (Port Town) - Tutorial level with sailors
- [x] Design and build Level 2 (HMS Revenge) - Ship level with all enemy types
- [x] Design and build Level 3 (Cliff Fortress) - Vertical climbing with cannons
- [x] Design and build Level 4 (The Armory) - **Miniboss level with Bosun**
- [x] Design and build Level 5 (Governor's Mansion) - Challenging pre-boss level
- [x] Boss Arena (Admiral's Quarters) - Final boss fight
- [x] Level select screen (6 levels available)

### New: Bosun Miniboss
- Health: 6 (displayed with health bar)
- Attacks: Whip (long range), Ground Stomp (shockwave), Charge
- Stomp does 2 damage
- Brief stun when hit
- Placed in Level 4 as a mid-game challenge

### Deliverable
Six complete, playable levels with miniboss and final boss.

---

## Phase 10: Menus & UI Polish ✅
**Estimated Time**: 1 Claude session

### Goals
- [x] Title screen (animated ocean waves, pirate-themed level select)
- [x] Pause menu (styled overlay with resume/quit options)
- [x] Game over screen (animated, retry/quit options)
- [x] Victory screen (fireworks, score counting animation)
- [x] Level intro cards (fade in/out with level name)
- [x] Improved HUD design (styled hearts, powerup bars, animated coins)
- [x] Screen transitions (fade in/out between states)

### Implementation Details
- New `game/screens.py` module with reusable screen classes
- `TitleScreen` - Animated title, level selection with descriptions
- `PauseMenu` - Navigation with up/down, visual selection
- `GameOverScreen` - Score display, shake animation
- `LevelCompleteScreen` - Stats display, celebration effects
- `VictoryScreen` - Fireworks, score counting, congratulations
- `LevelIntroCard` - Brief display before gameplay starts
- `ScreenTransition` - Fade effects with callbacks
- HUD improvements: pixel-art hearts, powerup timer bars with warnings

### Deliverable
Complete menu system and polished UI.

---

## Phase 11: Audio ✅
**Estimated Time**: 1 Claude session

### Goals
- [x] Sound effects
  - Jump, land
  - Sword slash, hit
  - Collect item (coin, treasure, powerup, health, extra life)
  - Damage taken (hurt, death)
  - Enemy death
  - Boss hit, boss death
  - Cannon fire, musket shot
  - Shield block
  - Parrot attack
  - Door unlock
  - Menu sounds
  - Level complete, game over
- [x] Background music (per level)
  - Menu theme
  - Level 1-5 themes
  - Boss battle theme
  - Victory theme
- [x] Audio manager with volume control (SFX, music, master)

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
