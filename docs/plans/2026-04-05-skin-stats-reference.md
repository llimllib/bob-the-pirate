# Skin Stats Reference

**Date:** 2026-04-05

## Captain Bob (Default) - Baseline Stats

### Movement
| Stat | Value | Notes |
|------|-------|-------|
| Speed | 5 | Horizontal movement pixels/frame |
| Jump Power | -15 | Negative = upward velocity |
| Gravity | 0.8 | Applied per frame |
| Max Fall Speed | 15 | Terminal velocity |
| Barrel Roll Speed | 12 | Faster than walk |
| Barrel Roll Duration | 15 frames | 0.25 seconds |
| Barrel Roll Cooldown | 45 frames | 0.75 seconds |

### Combat
| Stat | Value | Notes |
|------|-------|-------|
| Max Health | 5 | Hearts |
| Lives | 3 | Respawns |
| Attack Duration | 15 frames | 0.25 seconds |
| Attack Cooldown | 20 frames | ~0.33 seconds |
| Attack Range | 24 pixels | Sword hitbox length |
| Attack Damage | 1 | Base damage (multiplied by grog) |
| Invincibility Frames | 60 | 1 second after hit |

### Anchor Slam (Innate Ability)
| Stat | Value | Notes |
|------|-------|-------|
| Slam Speed | 20 | Downward velocity |
| Slam Damage | 2 | AoE damage |
| Slam Radius | 50 pixels | Damage area |
| Slam Cooldown | 60 frames | 1 second |

### Visual
- Brown pirate outfit with red bandana
- Cutlass sword attack animation
- Standard pirate walk/run cycle

### Attack Behavior
- **Type:** Melee swing
- **Movement:** Cannot move while attacking
- **Hitbox:** Forward-facing arc based on facing direction
- **Tracking:** Enemies hit once per attack (tracked by ID)

---

## Planned Skin Variations

### Sailor Bob
- **Visual:** Same outfit as Sailor enemy
- **Stats:** Identical to Captain Bob
- **Effects:** None
- **Complexity:** Sprite swap only

### Ghost Captain
- **Visual:** Spectral blue-green, wispy trail effect
- **Stats:**
  - Health: Higher than default (exact TBD)
  - Speed: Lower than default (exact TBD)
- **Attack:** Blue-green flame aura
  - Longer duration than normal attack
  - Can move while attacking
  - Same damage/range as normal
- **Effects:** Wispy particle trail while moving

### Skeleton Pirate
- **Visual:** Bone-white, tattered clothes, no bandana
- **Stats:**
  - Damage: Higher than default
  - Health: Lower than default
- **Attack:** Bone projectile visual (same hitbox)
- **Effects:** None
- **Level hint:** Arrow pointing to hidden skin location in Cliff Fortress

### Blackbeard
- **Visual:** Big black beard, peg leg, tricorn hat
- **Stats:**
  - Speed: Higher than default
- **Attack:** Normal
- **Effects:** Special angry idle animation after idle too long

### Noble Pirate
- **Visual:** Gold bandanna, fancy clothes
- **Stats:** Normal
- **Attack:** Instant kill on enemies with 3+ base health
  - Does NOT apply to Bosun (miniboss)
  - Does NOT apply to Admiral (boss)
  - Does NOT apply to Ghost Captain (secret boss)
- **Effects:** None

### Admiral Bob
- **Visual:** Very fancy admiral hat
- **Stats:** Identical to Captain Bob
- **Effects:** None
- **Complexity:** Sprite swap only
