# Skins System Design

**Date:** 2026-04-05

## Overview

Hidden collectible skins that permanently unlock alternate appearances for Captain Bob. One skin hidden in each of the 6 levels, selectable from main menu or pause menu.

## Skins

| Level | Skin Name | Theme | Hiding Method |
|-------|-----------|-------|---------------|
| 1 - Port Town | Sailor Bob | Humble deckhand outfit | Visible but hard to reach |
| 2 - HMS Revenge | Ghost Captain | Spectral pirate (existing sprite) | Partially hidden with shimmer |
| 3 - Cliff Fortress | Skeleton Pirate | Undead buccaneer | Completely hidden |
| 4 - The Armory | Blackbeard | Legendary pirate, big dark beard | Visible but tricky platforming |
| 5 - Governor's Mansion | Noble Pirate | Fancy stolen aristocrat clothes | Partially hidden |
| 6 - Admiral's Quarters | Admiral Bob | Ironic British naval uniform | Completely hidden |

## Implementation

### 1. New Files

- `game/skins.py` - Skin registry, save/load, skin definitions
- `assets/sprites/sailor_bob.png` - Sailor skin spritesheet
- `assets/sprites/skeleton_pirate.png` - Skeleton skin spritesheet
- `assets/sprites/blackbeard.png` - Blackbeard skin spritesheet
- `assets/sprites/noble_pirate.png` - Noble skin spritesheet
- `assets/sprites/admiral_bob.png` - Admiral skin spritesheet
- (ghost_captain.png already exists)

### 2. SkinPickup Collectible (collectibles.py)

```python
class SkinPickup(Collectible):
    """Hidden skin collectible."""
    
    def __init__(self, x: int, y: int, skin_id: str, hidden_type: str = "visible"):
        # hidden_type: "visible", "hidden", "shimmer"
        # For "hidden": invisible until touched
        # For "shimmer": semi-transparent, subtle visual hint
```

### 3. Skin Registry (skins.py)

```python
SKINS = {
    "default": {"name": "Captain Bob", "sprite": "player.png"},
    "sailor": {"name": "Sailor Bob", "sprite": "sailor_bob.png"},
    "ghost": {"name": "Ghost Captain", "sprite": "ghost_captain.png"},
    "skeleton": {"name": "Skeleton Pirate", "sprite": "skeleton_pirate.png"},
    "blackbeard": {"name": "Blackbeard", "sprite": "blackbeard.png"},
    "noble": {"name": "Noble Pirate", "sprite": "noble_pirate.png"},
    "admiral": {"name": "Admiral Bob", "sprite": "admiral_bob.png"},
}

def get_unlocked_skins() -> list[str]
def unlock_skin(skin_id: str) -> None
def get_selected_skin() -> str
def set_selected_skin(skin_id: str) -> None
def load_skin_progress() -> None
def save_skin_progress() -> None
```

### 4. Save File

Location: `~/.bob_the_pirate/skins.json`

```json
{
    "unlocked": ["default", "ghost", "skeleton"],
    "selected": "ghost"
}
```

### 5. Player Skin Loading

Modify `Player._load_animations()` to load the selected skin's spritesheet instead of hardcoded `player.png`.

### 6. UI Additions

**Main Menu:**
- Add "Skins" option between Play and Quit
- Skins submenu shows grid/list of skins
- Locked skins shown grayed out with "???" or lock icon
- Selected skin highlighted

**Pause Menu:**
- Add "Skins" option
- Same interface as main menu

**Pickup Notification:**
- Small corner notification (bottom-right)
- Shows skin icon + "Unlocked: [Skin Name]"
- Fades out after 3 seconds
- No gameplay interruption

### 7. Level JSON Format

Add to level JSON files:

```json
{
    "skins": [
        {
            "type": "skin",
            "skin_id": "ghost",
            "hidden_type": "shimmer",
            "x": 1200,
            "y": 300
        }
    ]
}
```

### 8. Shimmer Effect

For `hidden_type: "shimmer"`:
- Render at 30% opacity
- Subtle sine-wave alpha oscillation (25%-35%)
- Optional particle sparkle effect

For `hidden_type: "hidden"`:
- Completely invisible
- Only collision detection active

## Implementation Order

1. Create `game/skins.py` with registry and save/load
2. Create `SkinPickup` collectible class
3. Add skin loading to `Level.load_from_file()`
4. Modify `Player` to use selected skin
5. Add pickup notification to UI
6. Add Skins menu to main menu
7. Add Skins menu to pause menu
8. Create placeholder sprites for 5 new skins
9. Place skins in level JSON files
10. Write tests

## Testing

- Test skin unlock persists after game restart
- Test skin selection persists after game restart
- Test all 3 hidden types render correctly
- Test skin change reflects in player appearance
- Test notification appears and fades
- Test menu navigation and selection
