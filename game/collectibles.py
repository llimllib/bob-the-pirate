"""Collectibles: treasure chests, coins, power-ups."""

import pygame

from game.collectible_sprites import get_collectible_sprites
from game.settings import (
    CANNON_SHOT_AMMO,
    CHEST_POINTS,
    COIN_VALUE,
    CUTLASS_FURY_DURATION,
    DOUBLE_JUMP_DURATION,
    MAGNET_DURATION,
    MONKEY_DURATION,
    PARROT_DURATION,
)


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
        elif self.powerup_type == "cannon_shot":
            player.has_cannon_shot = True
            player.cannon_ammo = CANNON_SHOT_AMMO
            return {"type": "powerup", "powerup": "cannon_shot"}
        elif self.powerup_type == "double_jump":
            player.has_double_jump = True
            player.double_jump_timer = DOUBLE_JUMP_DURATION
            player.used_double_jump = False
            return {"type": "powerup", "powerup": "double_jump"}
        elif self.powerup_type == "cutlass_fury":
            player.has_cutlass_fury = True
            player.cutlass_fury_timer = CUTLASS_FURY_DURATION
            return {"type": "powerup", "powerup": "cutlass_fury"}
        elif self.powerup_type == "magnet":
            player.has_magnet = True
            player.magnet_timer = MAGNET_DURATION
            return {"type": "powerup", "powerup": "magnet"}
        elif self.powerup_type == "monkey":
            player.has_monkey = True
            player.monkey_timer = MONKEY_DURATION
            return {"type": "powerup", "powerup": "monkey"}

        return {"type": "powerup", "powerup": self.powerup_type}


class SecretDoor(Collectible):
    """Hidden door that unlocks a secret level."""

    def __init__(self, x: int, y: int, unlocks_level: str = "secret_crypt"):
        super().__init__(x, y, 32, 48)
        self.unlocks_level = unlocks_level
        # Create a spooky door appearance
        self.image = pygame.Surface((32, 48), pygame.SRCALPHA)
        # Dark purple door with ghostly glow
        pygame.draw.rect(self.image, (60, 40, 80), (2, 2, 28, 44))
        pygame.draw.rect(self.image, (100, 80, 120), (0, 0, 32, 48), 2)
        # Skull symbol
        pygame.draw.circle(self.image, (150, 150, 160), (16, 18), 8)
        pygame.draw.circle(self.image, (40, 30, 50), (12, 16), 3)
        pygame.draw.circle(self.image, (40, 30, 50), (20, 16), 3)
        pygame.draw.rect(self.image, (150, 150, 160), (12, 26, 8, 6))
        self.rect = self.image.get_rect(topleft=(x, y))

    def collect(self, player) -> dict:
        """Unlock the secret level."""
        super().collect(player)
        return {
            "type": "secret_door",
            "unlocks": self.unlocks_level
        }


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
