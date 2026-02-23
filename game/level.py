"""Level loading and management."""

import json

import pygame

from game.settings import BROWN, GREEN, SCREEN_HEIGHT, SCREEN_WIDTH, TILE_SIZE


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
            # One-way platform - thinner, different color
            self.image.fill((0, 0, 0, 0))
            self.image.set_colorkey((0, 0, 0))
            pygame.draw.rect(self.image, (100, 80, 60), (0, 0, TILE_SIZE, 8))
        elif tile_type == "decoration":
            self.image.fill(GREEN)

        self.rect = self.image.get_rect(topleft=(x, y))

    @property
    def is_one_way(self) -> bool:
        """Check if this is a one-way platform."""
        return self.tile_type == "platform"

    def draw(self, surface: pygame.Surface, camera_offset: tuple[int, int] = (0, 0)) -> None:
        """Draw the tile."""
        draw_rect = self.rect.move(-camera_offset[0], -camera_offset[1])
        surface.blit(self.image, draw_rect)


class Level:
    """Manages a game level."""

    def __init__(self):
        self.tiles = pygame.sprite.Group()
        self.solid_tiles = []  # For collision checking
        self.platform_tiles = []  # One-way platforms
        self.enemies = pygame.sprite.Group()
        self.collectibles = pygame.sprite.Group()
        self.projectiles = pygame.sprite.Group()

        self.name = "Unknown"
        self.player_start = (100, 100)
        self.width = SCREEN_WIDTH
        self.height = SCREEN_HEIGHT
        self.treasure_total = 0
        self.treasure_collected = 0
        self.exit_door = None

        # Boss level support
        self.is_boss_level = False
        self.boss = None

    def load_from_file(self, filepath: str) -> None:
        """Load level from JSON file."""
        # Import here to avoid circular imports
        from game.collectibles import (
            Coin,
            ExitDoor,
            LootChest,
            PirateFlag,
            RumBottle,
            TreasureChest,
        )
        from game.enemies import Admiral, Cannon, Musketeer, Officer, Sailor

        with open(filepath, 'r') as f:
            data = json.load(f)

        self.name = data.get("name", "Unknown Level")
        self.width = data.get("width", SCREEN_WIDTH)
        self.height = data.get("height", SCREEN_HEIGHT)
        self.player_start = tuple(data.get("player_start", [100, 100]))
        self.is_boss_level = data.get("is_boss_level", False)
        self.boss = None

        # Load tiles
        for tile_data in data.get("tiles", []):
            tile = Tile(
                tile_data["x"] * TILE_SIZE,
                tile_data["y"] * TILE_SIZE,
                tile_data.get("type", "solid")
            )
            self.tiles.add(tile)

            # Sort into collision lists
            if tile.tile_type == "platform":
                self.platform_tiles.append(tile)
            elif tile.tile_type != "decoration":
                self.solid_tiles.append(tile)

        # Load enemies
        for enemy_data in data.get("enemies", []):
            enemy_type = enemy_data.get("type", "sailor")
            x = enemy_data.get("x", 0)
            y = enemy_data.get("y", 0)

            if enemy_type == "sailor":
                patrol_dist = enemy_data.get("patrol_distance", 100)
                enemy = Sailor(x, y, patrol_dist)
            elif enemy_type == "musketeer":
                enemy = Musketeer(x, y, self.projectiles)
            elif enemy_type == "officer":
                enemy = Officer(x, y)
            elif enemy_type == "cannon":
                faces_right = enemy_data.get("faces_right", True)
                enemy = Cannon(x, y, self.projectiles, faces_right)
            elif enemy_type == "admiral":
                enemy = Admiral(x, y, self.projectiles)
                # Set arena bounds
                arena_left = enemy_data.get("arena_left", x - 200)
                arena_right = enemy_data.get("arena_right", x + 200)
                enemy.set_arena_bounds(arena_left, arena_right)
                self.boss = enemy
            else:
                continue

            self.enemies.add(enemy)

        # Load collectibles
        for item_data in data.get("collectibles", []):
            item_type = item_data.get("type", "coin")
            x = item_data.get("x", 0)
            y = item_data.get("y", 0)

            if item_type == "treasure":
                item = TreasureChest(x, y)
                self.treasure_total += 1
            elif item_type == "coin":
                item = Coin(x, y)
            elif item_type == "rum":
                item = RumBottle(x, y)
            elif item_type == "flag":
                item = PirateFlag(x, y)
            elif item_type == "loot":
                powerup = item_data.get("powerup", "parrot")
                item = LootChest(x, y, powerup)
            else:
                continue

            self.collectibles.add(item)

        # Load exit door
        exit_data = data.get("exit")
        if exit_data:
            self.exit_door = ExitDoor(exit_data["x"], exit_data["y"])

    def create_test_level(self) -> None:
        """Create a simple test level for development."""
        # Ground
        for x in range(0, 1200, TILE_SIZE):
            tile = Tile(x, SCREEN_HEIGHT - TILE_SIZE, "solid")
            self.tiles.add(tile)
            self.solid_tiles.append(tile)

        # Some solid platforms
        for x in range(200, 400, TILE_SIZE):
            tile = Tile(x, SCREEN_HEIGHT - TILE_SIZE * 4, "solid")
            self.tiles.add(tile)
            self.solid_tiles.append(tile)

        # One-way platform
        for x in range(500, 700, TILE_SIZE):
            tile = Tile(x, SCREEN_HEIGHT - TILE_SIZE * 6, "platform")
            self.tiles.add(tile)
            self.platform_tiles.append(tile)

        for x in range(800, 1000, TILE_SIZE):
            tile = Tile(x, SCREEN_HEIGHT - TILE_SIZE * 3, "solid")
            self.tiles.add(tile)
            self.solid_tiles.append(tile)

        self.width = 1200
        self.player_start = (100, SCREEN_HEIGHT - TILE_SIZE * 3)

    def check_collision_x(self, player) -> None:
        """Handle horizontal collision with solid tiles only."""
        # Only solid tiles block horizontal movement (not one-way platforms)
        for tile in self.solid_tiles:
            if player.rect.colliderect(tile.rect):
                if player.velocity_x > 0:  # Moving right
                    player.rect.right = tile.rect.left
                elif player.velocity_x < 0:  # Moving left
                    player.rect.left = tile.rect.right

        # Level boundaries - prevent walking off edges
        if player.rect.left < 0:
            player.rect.left = 0
        if player.rect.right > self.width:
            player.rect.right = self.width

    def check_collision_y(self, player) -> None:
        """Handle vertical collision with tiles."""
        player.on_ground = False

        # Check solid tiles (block from all directions)
        for tile in self.solid_tiles:
            if player.rect.colliderect(tile.rect):
                if player.velocity_y > 0:  # Falling
                    player.rect.bottom = tile.rect.top
                    player.velocity_y = 0
                    player.on_ground = True
                elif player.velocity_y < 0:  # Jumping
                    player.rect.top = tile.rect.bottom
                    player.velocity_y = 0

        # Check one-way platforms (only block when falling from above)
        for tile in self.platform_tiles:
            if player.rect.colliderect(tile.rect):
                # Only collide if player is falling and feet are near platform top
                if player.velocity_y > 0:
                    # Check if player's feet were above platform before this frame
                    feet_were_above = (player.rect.bottom - player.velocity_y) <= tile.rect.top + 4
                    if feet_were_above:
                        player.rect.bottom = tile.rect.top
                        player.velocity_y = 0
                        player.on_ground = True

        # If not already on ground, check if standing on a surface (1 pixel probe)
        if not player.on_ground and player.velocity_y >= 0:
            probe_rect = pygame.Rect(player.rect.x, player.rect.bottom, player.rect.width, 1)
            for tile in self.solid_tiles:
                if probe_rect.colliderect(tile.rect):
                    player.on_ground = True
                    player.velocity_y = 0
                    break
            if not player.on_ground:
                for tile in self.platform_tiles:
                    if probe_rect.colliderect(tile.rect):
                        player.on_ground = True
                        player.velocity_y = 0
                        break

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
