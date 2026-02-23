"""Tile sprite management for levels."""

import os

import pygame

from game.settings import TILE_SIZE


class TileSprites:
    """
    Loads and manages tile sprites from a tileset image.

    Tile indices (col, row) in tileset.png:
      solid_top: (0, 0)
      solid_middle: (1, 0)
      solid_bottom: (2, 0)
      solid_left: (3, 0)
      solid_right: (0, 1)
      solid_top_left: (1, 1)
      solid_top_right: (2, 1)
      solid_bottom_left: (3, 1)
      solid_bottom_right: (0, 2)
      platform: (1, 2)
      crate: (0, 3)
      barrel: (1, 3)
      anchor: (2, 3)
      rope_coil: (3, 3)
    """

    # Tile index mapping
    TILE_INDEX = {
        "solid_top": (0, 0),
        "solid_middle": (1, 0),
        "solid_bottom": (2, 0),
        "solid_left": (3, 0),
        "solid_right": (0, 1),
        "solid_top_left": (1, 1),
        "solid_top_right": (2, 1),
        "solid_bottom_left": (3, 1),
        "solid_bottom_right": (0, 2),
        "platform": (1, 2),
        "metal_platform": (2, 2),
        "crate": (0, 3),
        "barrel": (1, 3),
        "anchor": (2, 3),
        "rope_coil": (3, 3),
    }

    def __init__(self, tileset_path: str = "assets/tiles/tileset.png"):
        """
        Load tile sprites from tileset.

        Args:
            tileset_path: Path to the tileset image
        """
        self.sprites: dict[str, pygame.Surface] = {}
        self.tileset: pygame.Surface | None = None

        if os.path.exists(tileset_path):
            self._load_tileset(tileset_path)
        else:
            self._create_fallback_sprites()

    def _load_tileset(self, path: str) -> None:
        """Load sprites from tileset image."""
        self.tileset = pygame.image.load(path).convert_alpha()

        for name, (col, row) in self.TILE_INDEX.items():
            x = col * TILE_SIZE
            y = row * TILE_SIZE
            sprite = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
            sprite.blit(self.tileset, (0, 0), (x, y, TILE_SIZE, TILE_SIZE))
            self.sprites[name] = sprite

    def _create_fallback_sprites(self) -> None:
        """Create simple colored fallback sprites if tileset not found."""
        # Solid tile fallback (brown)
        solid = pygame.Surface((TILE_SIZE, TILE_SIZE))
        solid.fill((139, 69, 19))

        # Platform fallback
        platform = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        platform.fill((0, 0, 0, 0))
        pygame.draw.rect(platform, (100, 80, 60), (0, 0, TILE_SIZE, 8))

        # Decoration fallback (green)
        decoration = pygame.Surface((TILE_SIZE, TILE_SIZE))
        decoration.fill((0, 128, 0))

        # Map all solid variants to base solid
        for name in self.TILE_INDEX:
            if name.startswith("solid"):
                self.sprites[name] = solid.copy()
            elif name == "platform":
                self.sprites[name] = platform
            else:
                self.sprites[name] = decoration.copy()

    def get(self, name: str) -> pygame.Surface:
        """
        Get a tile sprite by name.

        Args:
            name: Tile name (e.g., 'solid_top', 'platform', 'crate')

        Returns:
            The tile sprite surface
        """
        return self.sprites.get(name, self.sprites.get("solid_middle",
                                pygame.Surface((TILE_SIZE, TILE_SIZE))))


class BackgroundLayers:
    """
    Manages parallax background layers.

    Supports two background types:
      - "outdoor": Sky, clouds, distant scenery (for outdoor levels)
      - "ship_interior": Ship interior (for boss arena)

    Layers for outdoor (back to front):
      - sky: Static background
      - distant_scenery: Slow parallax (0.2x)
      - clouds: Medium parallax (0.5x)
    """

    def __init__(self, backgrounds_path: str = "assets/backgrounds"):
        """
        Load background layers.

        Args:
            backgrounds_path: Path to backgrounds directory
        """
        self.backgrounds_path = backgrounds_path
        self.background_type = "outdoor"  # Default

        # Outdoor backgrounds
        self.sky: pygame.Surface | None = None
        self.clouds: pygame.Surface | None = None
        self.distant_scenery: pygame.Surface | None = None
        self.ocean_frames: list[pygame.Surface] = []
        self.ocean_frame = 0
        self.ocean_timer = 0
        self.ocean_frame_duration = 15  # Frames per animation frame

        # Interior backgrounds
        self.ship_interior: pygame.Surface | None = None

        self._load_backgrounds(backgrounds_path)

    def set_background_type(self, bg_type: str) -> None:
        """
        Set the background type to use.

        Args:
            bg_type: "outdoor" or "ship_interior"
        """
        self.background_type = bg_type

    def _load_backgrounds(self, path: str) -> None:
        """Load all background images."""
        # Sky
        sky_path = os.path.join(path, "sky.png")
        if os.path.exists(sky_path):
            self.sky = pygame.image.load(sky_path).convert()

        # Clouds
        clouds_path = os.path.join(path, "clouds.png")
        if os.path.exists(clouds_path):
            self.clouds = pygame.image.load(clouds_path).convert_alpha()

        # Distant scenery
        scenery_path = os.path.join(path, "distant_scenery.png")
        if os.path.exists(scenery_path):
            self.distant_scenery = pygame.image.load(scenery_path).convert_alpha()

        # Ocean animation frames
        for i in range(4):
            ocean_path = os.path.join(path, f"ocean_{i}.png")
            if os.path.exists(ocean_path):
                self.ocean_frames.append(pygame.image.load(ocean_path).convert_alpha())

        # Ship interior
        ship_path = os.path.join(path, "ship_interior.png")
        if os.path.exists(ship_path):
            self.ship_interior = pygame.image.load(ship_path).convert()

    def update(self) -> None:
        """Update animated elements."""
        if self.ocean_frames:
            self.ocean_timer += 1
            if self.ocean_timer >= self.ocean_frame_duration:
                self.ocean_timer = 0
                self.ocean_frame = (self.ocean_frame + 1) % len(self.ocean_frames)

    def draw(
        self,
        surface: pygame.Surface,
        camera_x: float,
        screen_width: int,
        screen_height: int
    ) -> None:
        """
        Draw all background layers with parallax.

        Args:
            surface: Surface to draw on
            camera_x: Camera X position for parallax calculation
            screen_width: Screen width
            screen_height: Screen height
        """
        if self.background_type == "ship_interior":
            self._draw_ship_interior(surface)
        else:
            self._draw_outdoor(surface, camera_x, screen_width, screen_height)

    def _draw_ship_interior(self, surface: pygame.Surface) -> None:
        """Draw ship interior background (static, no parallax)."""
        if self.ship_interior:
            surface.blit(self.ship_interior, (0, 0))
        else:
            # Fallback: dark brown fill
            surface.fill((80, 55, 35))

    def _draw_outdoor(
        self,
        surface: pygame.Surface,
        camera_x: float,
        screen_width: int,
        screen_height: int
    ) -> None:
        """Draw outdoor background with parallax layers."""
        # Sky (static, no parallax)
        if self.sky:
            surface.blit(self.sky, (0, 0))

        # Distant scenery (0.2x parallax, positioned at horizon)
        if self.distant_scenery:
            scenery_width = self.distant_scenery.get_width()
            parallax_x = int(camera_x * 0.2) % scenery_width
            y_pos = screen_height - 300 - 80  # Above ocean

            # Draw twice for seamless scrolling
            surface.blit(self.distant_scenery, (-parallax_x, y_pos))
            if parallax_x > 0:
                surface.blit(self.distant_scenery, (scenery_width - parallax_x, y_pos))

        # Clouds (0.5x parallax, top portion)
        if self.clouds:
            clouds_width = self.clouds.get_width()
            parallax_x = int(camera_x * 0.5) % clouds_width

            surface.blit(self.clouds, (-parallax_x, 20))
            if parallax_x > 0:
                surface.blit(self.clouds, (clouds_width - parallax_x, 20))

    def draw_ocean(
        self,
        surface: pygame.Surface,
        camera_x: float,
        screen_width: int,
        screen_height: int
    ) -> None:
        """
        Draw ocean layer (should be called after tiles for proper layering).

        Args:
            surface: Surface to draw on
            camera_x: Camera X position
            screen_width: Screen width
            screen_height: Screen height
        """
        if not self.ocean_frames:
            return

        ocean = self.ocean_frames[self.ocean_frame]
        ocean_width = ocean.get_width()
        ocean_height = ocean.get_height()

        # Position at bottom of screen
        y_pos = screen_height - ocean_height

        # Tile horizontally
        parallax_x = int(camera_x * 0.8) % ocean_width
        x = -parallax_x
        while x < screen_width:
            surface.blit(ocean, (x, y_pos))
            x += ocean_width


# Global singleton for tile sprites (loaded once)
_tile_sprites: TileSprites | None = None


def get_tile_sprites() -> TileSprites:
    """Get the global TileSprites instance (lazy loaded)."""
    global _tile_sprites
    if _tile_sprites is None:
        _tile_sprites = TileSprites()
    return _tile_sprites


# Global singleton for backgrounds
_background_layers: BackgroundLayers | None = None


def get_background_layers() -> BackgroundLayers:
    """Get the global BackgroundLayers instance (lazy loaded)."""
    global _background_layers
    if _background_layers is None:
        _background_layers = BackgroundLayers()
    return _background_layers
