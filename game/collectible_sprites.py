"""Collectible sprite management."""

import os

import pygame

from game.animation import Animation


class CollectibleSprites:
    """
    Loads and manages collectible sprites from the sprite sheet.

    Sprite indices (x, y, width, height) in collectibles.png:
      treasure_chest: (0, 0, 32, 24)
      coin_1-4: spinning animation frames (16x16)
      loot_chest: (0, 24, 32, 24)
      rum_bottle: (0, 48, 12, 20)
      pirate_flag: (12, 48, 24, 32)
      exit_door_locked: (0, 80, 32, 64)
      exit_door_unlocked: (32, 80, 32, 64)
    """

    # Sprite index mapping (x, y, width, height)
    SPRITE_INDEX = {
        "treasure_chest": (0, 0, 32, 24),
        "coin_1": (32, 0, 16, 16),
        "coin_2": (48, 0, 16, 16),
        "coin_3": (32, 24, 16, 16),
        "coin_4": (48, 24, 16, 16),
        "loot_chest": (0, 24, 32, 24),
        "rum_bottle": (0, 48, 12, 20),
        "pirate_flag": (12, 48, 24, 32),
        "exit_door_locked": (0, 80, 32, 64),
        "exit_door_unlocked": (32, 80, 32, 64),
    }

    def __init__(self, sheet_path: str = "assets/collectibles/collectibles.png"):
        """
        Load collectible sprites from sprite sheet.

        Args:
            sheet_path: Path to the collectibles sprite sheet
        """
        self.sprites: dict[str, pygame.Surface] = {}
        self.sheet: pygame.Surface | None = None

        if os.path.exists(sheet_path):
            self._load_sheet(sheet_path)
        else:
            self._create_fallback_sprites()

    def _load_sheet(self, path: str) -> None:
        """Load sprites from sprite sheet image."""
        self.sheet = pygame.image.load(path).convert_alpha()

        for name, (x, y, w, h) in self.SPRITE_INDEX.items():
            sprite = pygame.Surface((w, h), pygame.SRCALPHA)
            sprite.blit(self.sheet, (0, 0), (x, y, w, h))
            self.sprites[name] = sprite

    def _create_fallback_sprites(self) -> None:
        """Create simple colored fallback sprites if sheet not found."""
        # Treasure chest fallback
        chest = pygame.Surface((32, 24), pygame.SRCALPHA)
        chest.fill((139, 69, 19))
        pygame.draw.rect(chest, (255, 255, 0), (4, 4, 24, 16))
        self.sprites["treasure_chest"] = chest

        # Coin fallback frames
        for i in range(1, 5):
            coin = pygame.Surface((16, 16), pygame.SRCALPHA)
            pygame.draw.circle(coin, (255, 255, 0), (8, 8), 8 - i)
            pygame.draw.circle(coin, (200, 180, 0), (8, 8), 6 - i if i < 4 else 2)
            self.sprites[f"coin_{i}"] = coin

        # Loot chest fallback (golden)
        loot = pygame.Surface((32, 24), pygame.SRCALPHA)
        loot.fill((255, 215, 0))
        pygame.draw.rect(loot, (200, 150, 0), (0, 0, 32, 24), 3)
        self.sprites["loot_chest"] = loot

        # Rum bottle fallback
        rum = pygame.Surface((12, 20), pygame.SRCALPHA)
        pygame.draw.rect(rum, (150, 80, 50), (2, 0, 8, 16))
        pygame.draw.rect(rum, (80, 40, 20), (4, 16, 4, 4))
        self.sprites["rum_bottle"] = rum

        # Pirate flag fallback
        flag = pygame.Surface((24, 32), pygame.SRCALPHA)
        pygame.draw.rect(flag, (255, 255, 255), (0, 0, 20, 24))
        pygame.draw.rect(flag, (0, 0, 0), (20, 0, 4, 32))
        pygame.draw.circle(flag, (0, 0, 0), (10, 10), 6)
        self.sprites["pirate_flag"] = flag

        # Exit door locked fallback
        door_locked = pygame.Surface((32, 64), pygame.SRCALPHA)
        door_locked.fill((100, 100, 100))
        pygame.draw.rect(door_locked, (60, 60, 60), (4, 4, 24, 56), 2)
        self.sprites["exit_door_locked"] = door_locked

        # Exit door unlocked fallback
        door_unlocked = pygame.Surface((32, 64), pygame.SRCALPHA)
        door_unlocked.fill((0, 200, 0))
        pygame.draw.rect(door_unlocked, (0, 150, 0), (4, 4, 24, 56), 2)
        self.sprites["exit_door_unlocked"] = door_unlocked

    def get(self, name: str) -> pygame.Surface:
        """
        Get a sprite by name.

        Args:
            name: Sprite name (e.g., 'treasure_chest', 'coin_1')

        Returns:
            The sprite surface
        """
        return self.sprites.get(name, pygame.Surface((16, 16), pygame.SRCALPHA))

    def get_coin_animation(self, frame_duration: int = 8) -> Animation:
        """
        Get a spinning coin animation.

        Args:
            frame_duration: Frames per animation frame

        Returns:
            Animation object for spinning coin
        """
        frames = [
            self.sprites["coin_1"],
            self.sprites["coin_2"],
            self.sprites["coin_3"],
            self.sprites["coin_4"],
        ]
        return Animation(frames, frame_duration, loop=True)


# Global singleton for collectible sprites (loaded once)
_collectible_sprites: CollectibleSprites | None = None


def get_collectible_sprites() -> CollectibleSprites:
    """Get the global CollectibleSprites instance (lazy loaded)."""
    global _collectible_sprites
    if _collectible_sprites is None:
        _collectible_sprites = CollectibleSprites()
    return _collectible_sprites
