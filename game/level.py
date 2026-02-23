"""Level loading and management."""

import json
import pygame
from game.settings import TILE_SIZE, SCREEN_WIDTH, SCREEN_HEIGHT, GREEN, BROWN


class Tile(pygame.sprite.Sprite):
    """A single tile in the level."""

    def __init__(self, x: int, y: int, tile_type: str = "solid"):
        super().__init__()
        self.image = pygame.Surface((TILE_SIZE, TILE_SIZE))
        self.tile_type = tile_type
        
        # Color based on type
        if tile_type == "solid":
            self.image.fill(BROWN)
        elif tile_type == "platform":
            self.image.fill((100, 80, 60))
        elif tile_type == "decoration":
            self.image.fill(GREEN)
        
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, surface: pygame.Surface, camera_offset: tuple[int, int] = (0, 0)) -> None:
        """Draw the tile."""
        draw_rect = self.rect.move(-camera_offset[0], -camera_offset[1])
        surface.blit(self.image, draw_rect)


class Level:
    """Manages a game level."""

    def __init__(self):
        self.tiles = pygame.sprite.Group()
        self.enemies = pygame.sprite.Group()
        self.collectibles = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()
        
        self.player_start = (100, 100)
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        self.treasure_total = 0
        self.treasure_collected = 0
        self.exit_door = None

    def load_from_file(self, filepath: str) -> None:
        """Load level from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        self.width = data.get("width", SCREEN_WIDTH)
        self.height = data.get("height", SCREEN_HEIGHT)
        self.player_start = tuple(data.get("player_start", [100, 100]))
        
        # Load tiles
        for tile_data in data.get("tiles", []):
            tile = Tile(
                tile_data["x"] * TILE_SIZE,
                tile_data["y"] * TILE_SIZE,
                tile_data.get("type", "solid")
            )
            self.tiles.add(tile)
        
        # TODO: Load enemies and collectibles from data

    def create_test_level(self) -> None:
        """Create a simple test level for development."""
        # Ground
        for x in range(0, 1200, TILE_SIZE):
            tile = Tile(x, SCREEN_HEIGHT - TILE_SIZE, "solid")
            self.tiles.add(tile)
        
        # Some platforms
        for x in range(200, 400, TILE_SIZE):
            tile = Tile(x, SCREEN_HEIGHT - TILE_SIZE * 4, "solid")
            self.tiles.add(tile)
        
        for x in range(500, 700, TILE_SIZE):
            tile = Tile(x, SCREEN_HEIGHT - TILE_SIZE * 6, "solid")
            self.tiles.add(tile)
        
        for x in range(800, 1000, TILE_SIZE):
            tile = Tile(x, SCREEN_HEIGHT - TILE_SIZE * 3, "solid")
            self.tiles.add(tile)
        
        self.width = 1200
        self.player_start = (100, SCREEN_HEIGHT - TILE_SIZE * 3)

    def check_collision_x(self, player) -> None:
        """Handle horizontal collision with tiles."""
        for tile in self.tiles:
            if player.rect.colliderect(tile.rect):
                if player.velocity_x > 0:  # Moving right
                    player.rect.right = tile.rect.left
                elif player.velocity_x < 0:  # Moving left
                    player.rect.left = tile.rect.right

    def check_collision_y(self, player) -> None:
        """Handle vertical collision with tiles."""
        player.on_ground = False
        
        for tile in self.tiles:
            if player.rect.colliderect(tile.rect):
                if player.velocity_y > 0:  # Falling
                    player.rect.bottom = tile.rect.top
                    player.velocity_y = 0
                    player.on_ground = True
                elif player.velocity_y < 0:  # Jumping
                    player.rect.top = tile.rect.bottom
                    player.velocity_y = 0

    def update(self, player) -> None:
        """Update all level entities."""
        # Update enemies
        for enemy in self.enemies:
            enemy.update(player.rect)
        
        # Update projectiles
        for projectile in self.projectiles:
            projectile.update()
            # Remove off-screen projectiles
            if (projectile.rect.right < 0 or 
                projectile.rect.left > self.width or
                projectile.rect.top > self.height):
                projectile.kill()
        
        # Check if all treasure collected
        if self.treasure_collected >= self.treasure_total and self.exit_door:
            self.exit_door.unlock()

    def collect_item(self, player) -> list[dict]:
        """Check for collectible pickups. Returns list of collected item info."""
        collected = []
        for item in self.collectibles:
            if player.rect.colliderect(item.rect) and not item.collected:
                result = item.collect(player)
                collected.append(result)
                
                if result.get("type") == "treasure":
                    self.treasure_collected += 1
        
        return collected

    def draw(self, surface: pygame.Surface, camera_offset: tuple[int, int] = (0, 0)) -> None:
        """Draw all level elements."""
        # Draw tiles
        for tile in self.tiles:
            tile.draw(surface, camera_offset)
        
        # Draw collectibles
        for item in self.collectibles:
            item.draw(surface, camera_offset)
        
        # Draw exit
        if self.exit_door:
            self.exit_door.draw(surface, camera_offset)
        
        # Draw enemies
        for enemy in self.enemies:
            enemy.draw(surface, camera_offset)
        
        # Draw projectiles
        for projectile in self.projectiles:
            projectile.draw(surface, camera_offset)
