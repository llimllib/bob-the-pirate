"""Collectibles: treasure chests, coins, power-ups."""

import pygame
from game.settings import (
    TILE_SIZE, COIN_VALUE, CHEST_POINTS, PARROT_DURATION,
    YELLOW, RED, GREEN, WHITE
)


class Collectible(pygame.sprite.Sprite):
    """Base class for collectible items."""

    def __init__(self, x: int, y: int, width: int, height: int, color: tuple):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
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

    def draw(self, surface: pygame.Surface, camera_offset: tuple[int, int] = (0, 0)) -> None:
        """Draw the collectible."""
        if self.collected:
            return
        draw_rect = self.rect.move(-camera_offset[0], -camera_offset[1])
        surface.blit(self.image, draw_rect)


class TreasureChest(Collectible):
    """Required collectible - get all to complete level."""

    def __init__(self, x: int, y: int):
        super().__init__(x, y, TILE_SIZE, TILE_SIZE - 8, (139, 69, 19))
        # Draw chest details
        pygame.draw.rect(self.image, YELLOW, (4, 4, TILE_SIZE - 8, TILE_SIZE - 16))
        pygame.draw.rect(self.image, (100, 50, 0), (0, 0, TILE_SIZE, TILE_SIZE - 8), 2)

    def collect(self, player) -> dict:
        """Collect treasure chest."""
        super().collect(player)
        return {
            "type": "treasure",
            "points": CHEST_POINTS
        }


class Coin(Collectible):
    """Gold coin for score."""

    def __init__(self, x: int, y: int):
        super().__init__(x, y, 16, 16, YELLOW)
        # Make it circular-ish
        self.image.fill((0, 0, 0, 0))
        self.image.set_colorkey((0, 0, 0))
        pygame.draw.circle(self.image, YELLOW, (8, 8), 8)
        pygame.draw.circle(self.image, (200, 180, 0), (8, 8), 6)

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
        super().__init__(x, y, 12, 20, (100, 60, 40))
        # Draw bottle shape
        pygame.draw.rect(self.image, (150, 80, 50), (2, 0, 8, 16))
        pygame.draw.rect(self.image, (80, 40, 20), (4, 16, 4, 4))

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
        super().__init__(x, y, 24, 32, (0, 0, 0))
        # Draw flag
        pygame.draw.rect(self.image, WHITE, (0, 0, 20, 24))
        pygame.draw.rect(self.image, (0, 0, 0), (20, 0, 4, 32))
        # Skull (simplified)
        pygame.draw.circle(self.image, (0, 0, 0), (10, 10), 6)

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
        super().__init__(x, y, TILE_SIZE, TILE_SIZE - 8, (139, 69, 19))
        self.powerup_type = powerup_type
        # Draw special chest (golden)
        pygame.draw.rect(self.image, (255, 215, 0), (4, 4, TILE_SIZE - 8, TILE_SIZE - 16))
        pygame.draw.rect(self.image, (200, 150, 0), (0, 0, TILE_SIZE, TILE_SIZE - 8), 3)

    def collect(self, player) -> dict:
        """Grant power-up to player."""
        super().collect(player)
        
        if self.powerup_type == "parrot":
            player.has_parrot = True
            player.parrot_timer = PARROT_DURATION
            return {"type": "powerup", "powerup": "parrot"}
        elif self.powerup_type == "grog":
            # TODO: Implement grog rage
            return {"type": "powerup", "powerup": "grog"}
        elif self.powerup_type == "shield":
            # TODO: Implement shield
            return {"type": "powerup", "powerup": "shield"}
        
        return {"type": "powerup", "powerup": self.powerup_type}


class ExitDoor(pygame.sprite.Sprite):
    """Level exit - unlocked when all treasure is collected."""

    def __init__(self, x: int, y: int):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE * 2))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.locked = True
        self._update_appearance()

    def _update_appearance(self) -> None:
        """Update visual based on locked state."""
        if self.locked:
            self.image.fill((100, 100, 100))
            pygame.draw.rect(self.image, (60, 60, 60), (4, 4, TILE_SIZE - 8, TILE_SIZE * 2 - 8), 2)
        else:
            self.image.fill((0, 200, 0))
            pygame.draw.rect(self.image, (0, 150, 0), (4, 4, TILE_SIZE - 8, TILE_SIZE * 2 - 8), 2)

    def unlock(self) -> None:
        """Unlock the exit."""
        self.locked = False
        self._update_appearance()

    def draw(self, surface: pygame.Surface, camera_offset: tuple[int, int] = (0, 0)) -> None:
        """Draw the exit door."""
        draw_rect = self.rect.move(-camera_offset[0], -camera_offset[1])
        surface.blit(self.image, draw_rect)
