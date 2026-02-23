"""Collectibles: treasure chests, coins, power-ups."""

import pygame

from game.collectible_sprites import get_collectible_sprites
from game.settings import CHEST_POINTS, COIN_VALUE, PARROT_DURATION


class Collectible(pygame.sprite.Sprite):
    """Base class for collectible items."""

    def __init__(self, x: int, y: int, width: int, height: int):
        super().__init__()
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.rect = self.image.get_rect(topleft=(x, y))
        self.collected = False

    def collect(self, player) -> dict:
        """
        Called when player collects this item.
        Returns dict with effects to apply.
        Override in subclasses.
        """
        self.collected = True
        self.kill()
        return {}

    def update(self) -> None:
        """Update the collectible (for animations)."""
        pass

    def draw(self, surface: pygame.Surface, camera_offset: tuple[int, int] = (0, 0)) -> None:
        """Draw the collectible."""
        if self.collected:
            return
        draw_rect = self.rect.move(-camera_offset[0], -camera_offset[1])
        surface.blit(self.image, draw_rect)


class TreasureChest(Collectible):
    """Required collectible - get all to complete level."""

    def __init__(self, x: int, y: int):
        super().__init__(x, y, 32, 24)
        sprites = get_collectible_sprites()
        self.image = sprites.get("treasure_chest")
        # Adjust rect to match sprite size
        self.rect = self.image.get_rect(topleft=(x, y))

    def collect(self, player) -> dict:
        """Collect treasure chest."""
        super().collect(player)
        return {
            "type": "treasure",
            "points": CHEST_POINTS
        }


class Coin(Collectible):
    """Gold coin for score - animated spinning."""

    def __init__(self, x: int, y: int):
        super().__init__(x, y, 16, 16)
        sprites = get_collectible_sprites()
        self.animation = sprites.get_coin_animation(frame_duration=8)
        self.image = self.animation.get_frame()
        self.rect = self.image.get_rect(topleft=(x, y))

    def update(self) -> None:
        """Update coin spinning animation."""
        self.animation.update()
        self.image = self.animation.get_frame()

    def collect(self, player) -> dict:
        """Collect coin."""
        super().collect(player)
        return {
            "type": "coin",
            "points": COIN_VALUE
        }


class RumBottle(Collectible):
    """Health restore item."""

    def __init__(self, x: int, y: int):
        super().__init__(x, y, 12, 20)
        sprites = get_collectible_sprites()
        self.image = sprites.get("rum_bottle")
        self.rect = self.image.get_rect(topleft=(x, y))

    def collect(self, player) -> dict:
        """Restore health."""
        super().collect(player)
        player.heal(1)
        return {
            "type": "health",
            "amount": 1
        }


class PirateFlag(Collectible):
    """Extra life."""

    def __init__(self, x: int, y: int):
        super().__init__(x, y, 24, 32)
        sprites = get_collectible_sprites()
        self.image = sprites.get("pirate_flag")
        self.rect = self.image.get_rect(topleft=(x, y))

    def collect(self, player) -> dict:
        """Grant extra life."""
        super().collect(player)
        player.lives += 1
        return {
            "type": "life",
            "lives": 1
        }


class LootChest(Collectible):
    """Special chest that contains power-ups."""

    def __init__(self, x: int, y: int, powerup_type: str = "parrot"):
        super().__init__(x, y, 32, 24)
        self.powerup_type = powerup_type
        sprites = get_collectible_sprites()
        self.image = sprites.get("loot_chest")
        self.rect = self.image.get_rect(topleft=(x, y))

    def collect(self, player) -> dict:
        """Grant power-up to player."""
        super().collect(player)

        if self.powerup_type == "parrot":
            player.has_parrot = True
            player.parrot_timer = PARROT_DURATION
            return {"type": "powerup", "powerup": "parrot"}
        elif self.powerup_type == "grog":
            player.has_grog = True
            player.grog_timer = 300  # 5 seconds
            player.damage_multiplier = 2
            return {"type": "powerup", "powerup": "grog"}
        elif self.powerup_type == "shield":
            player.has_shield = True
            return {"type": "powerup", "powerup": "shield"}

        return {"type": "powerup", "powerup": self.powerup_type}


class ExitDoor(pygame.sprite.Sprite):
    """Level exit - unlocked when all treasure is collected."""

    def __init__(self, x: int, y: int):
        super().__init__()
        self.sprites = get_collectible_sprites()
        self.image = self.sprites.get("exit_door_locked")
        self.rect = self.image.get_rect(topleft=(x, y))
        self.locked = True

    def _update_appearance(self) -> None:
        """Update visual based on locked state."""
        if self.locked:
            self.image = self.sprites.get("exit_door_locked")
        else:
            self.image = self.sprites.get("exit_door_unlocked")

    def unlock(self) -> None:
        """Unlock the exit."""
        self.locked = False
        self._update_appearance()

    def draw(self, surface: pygame.Surface, camera_offset: tuple[int, int] = (0, 0)) -> None:
        """Draw the exit door."""
        draw_rect = self.rect.move(-camera_offset[0], -camera_offset[1])
        surface.blit(self.image, draw_rect)
