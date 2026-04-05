"""Skin system: unlockable alternate appearances for Captain Bob."""

import json
from pathlib import Path
from typing import TypedDict


class SkinInfo(TypedDict):
    """Type definition for skin metadata."""
    name: str
    sprite: str
    description: str


# All available skins
SKINS: dict[str, SkinInfo] = {
    "default": {
        "name": "Captain Bob",
        "sprite": "player.png",
        "description": "The original sea dog",
    },
    "sailor": {
        "name": "Sailor Bob",
        "sprite": "sailor_bob.png",
        "description": "Humble deckhand outfit",
    },
    "ghost": {
        "name": "Ghost Captain",
        "sprite": "ghost_captain.png",
        "description": "Spectral pirate from beyond",
    },
    "skeleton": {
        "name": "Skeleton Pirate",
        "sprite": "skeleton_pirate.png",
        "description": "Undead buccaneer",
    },
    "blackbeard": {
        "name": "Blackbeard",
        "sprite": "blackbeard.png",
        "description": "The legendary pirate",
    },
    "noble": {
        "name": "Noble Pirate",
        "sprite": "noble_pirate.png",
        "description": "Fancy stolen aristocrat clothes",
    },
    "admiral": {
        "name": "Admiral Bob",
        "sprite": "admiral_bob.png",
        "description": "Ironic British naval uniform",
    },
}

# Save file location
SAVE_DIR = Path.home() / ".bob_the_pirate"
SAVE_FILE = SAVE_DIR / "skins.json"

# In-memory state
_unlocked_skins: set[str] = {"default"}
_selected_skin: str = "default"
_initialized: bool = False


def _ensure_initialized() -> None:
    """Ensure skin progress is loaded from file."""
    global _initialized
    if not _initialized:
        load_skin_progress()
        _initialized = True


def get_all_skins() -> dict[str, SkinInfo]:
    """Get all available skins."""
    return SKINS


def get_unlocked_skins() -> list[str]:
    """Get list of unlocked skin IDs."""
    _ensure_initialized()
    return list(_unlocked_skins)


def is_skin_unlocked(skin_id: str) -> bool:
    """Check if a specific skin is unlocked."""
    _ensure_initialized()
    return skin_id in _unlocked_skins


def unlock_skin(skin_id: str) -> bool:
    """
    Unlock a skin.

    Returns True if this is a new unlock, False if already unlocked.
    """
    _ensure_initialized()
    if skin_id not in SKINS:
        return False
    if skin_id in _unlocked_skins:
        return False
    _unlocked_skins.add(skin_id)
    save_skin_progress()
    return True


def get_selected_skin() -> str:
    """Get the currently selected skin ID."""
    _ensure_initialized()
    return _selected_skin


def get_selected_skin_sprite() -> str:
    """Get the sprite filename for the currently selected skin."""
    _ensure_initialized()
    skin = SKINS.get(_selected_skin, SKINS["default"])
    return skin["sprite"]


def set_selected_skin(skin_id: str) -> bool:
    """
    Set the selected skin.

    Returns True if successful, False if skin not unlocked or doesn't exist.
    """
    global _selected_skin
    _ensure_initialized()
    if skin_id not in SKINS:
        return False
    if skin_id not in _unlocked_skins:
        return False
    _selected_skin = skin_id
    save_skin_progress()
    return True


def load_skin_progress() -> None:
    """Load skin progress from save file."""
    global _unlocked_skins, _selected_skin

    if not SAVE_FILE.exists():
        _unlocked_skins = {"default"}
        _selected_skin = "default"
        return

    try:
        with open(SAVE_FILE, "r") as f:
            data = json.load(f)

        # Load unlocked skins (validate they exist)
        unlocked = data.get("unlocked", ["default"])
        _unlocked_skins = {s for s in unlocked if s in SKINS}
        _unlocked_skins.add("default")  # Always unlocked

        # Load selected skin (validate it's unlocked)
        selected = data.get("selected", "default")
        if selected in _unlocked_skins:
            _selected_skin = selected
        else:
            _selected_skin = "default"

    except (json.JSONDecodeError, IOError):
        # Reset to defaults on error
        _unlocked_skins = {"default"}
        _selected_skin = "default"


def save_skin_progress() -> None:
    """Save skin progress to file."""
    _ensure_initialized()

    # Ensure save directory exists
    SAVE_DIR.mkdir(parents=True, exist_ok=True)

    data = {
        "unlocked": list(_unlocked_skins),
        "selected": _selected_skin,
    }

    try:
        with open(SAVE_FILE, "w") as f:
            json.dump(data, f, indent=2)
    except IOError:
        pass  # Silently fail on save errors


def reset_skin_progress() -> None:
    """Reset all skin progress (for testing)."""
    global _unlocked_skins, _selected_skin, _initialized
    _unlocked_skins = {"default"}
    _selected_skin = "default"
    _initialized = True

    # Delete save file if it exists
    if SAVE_FILE.exists():
        try:
            SAVE_FILE.unlink()
        except IOError:
            pass


def is_admiral_bob_active() -> bool:
    """
    Check if Admiral Bob skin is currently selected.

    Used for applying Admiral Bob's special effect (removing first instance
    of each regular enemy type).
    """
    _ensure_initialized()
    return _selected_skin == "admiral"


def is_ghost_captain_active() -> bool:
    """
    Check if Ghost Captain skin is currently selected.

    Used for applying Ghost Captain's special effects:
    - Higher max health (+2)
    - Lower movement speed (80%)
    - Can move while attacking
    - Longer attack duration (150%)
    - Wispy particle trail while moving
    """
    _ensure_initialized()
    return _selected_skin == "ghost"


def is_skeleton_pirate_active() -> bool:
    """
    Check if Skeleton Pirate skin is currently selected.

    Used for applying Skeleton Pirate's special effects:
    - Lower max health (-2, 3 total)
    - Higher damage (2x)
    - Every 4th attack throws a bone projectile
    """
    _ensure_initialized()
    return _selected_skin == "skeleton"
