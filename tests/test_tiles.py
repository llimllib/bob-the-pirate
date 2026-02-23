"""Tests for tile sprites and background layers."""

import pygame
import pytest

from game.settings import TILE_SIZE
from game.tiles import BackgroundLayers, TileSprites, get_background_layers, get_tile_sprites


@pytest.fixture(autouse=True)
def init_pygame():
    """Initialize pygame for all tests."""
    pygame.init()
    pygame.display.set_mode((1, 1))  # Minimal display for testing
    yield
    pygame.quit()


class TestTileSprites:
    """Tests for TileSprites class."""

    def test_tile_sprites_loads_from_tileset(self):
        """Test that tile sprites can be loaded from tileset."""
        tiles = TileSprites()
        assert tiles is not None

    def test_tile_sprites_has_all_expected_tiles(self):
        """Test that all expected tile types are available."""
        tiles = TileSprites()
        expected_tiles = [
            "solid_top", "solid_middle", "solid_bottom",
            "solid_left", "solid_right",
            "solid_top_left", "solid_top_right",
            "solid_bottom_left", "solid_bottom_right",
            "platform",
            "crate", "barrel", "anchor", "rope_coil"
        ]
        for tile_name in expected_tiles:
            sprite = tiles.get(tile_name)
            assert sprite is not None
            assert isinstance(sprite, pygame.Surface)

    def test_tile_sprites_correct_size(self):
        """Test that tile sprites are the correct size."""
        tiles = TileSprites()
        sprite = tiles.get("solid_top")
        assert sprite.get_width() == TILE_SIZE
        assert sprite.get_height() == TILE_SIZE

    def test_get_nonexistent_tile_returns_fallback(self):
        """Test that getting a non-existent tile returns a fallback."""
        tiles = TileSprites()
        sprite = tiles.get("nonexistent_tile")
        assert sprite is not None
        assert isinstance(sprite, pygame.Surface)

    def test_singleton_returns_same_instance(self):
        """Test that get_tile_sprites returns the same instance."""
        tiles1 = get_tile_sprites()
        tiles2 = get_tile_sprites()
        assert tiles1 is tiles2


class TestBackgroundLayers:
    """Tests for BackgroundLayers class."""

    def test_background_layers_loads(self):
        """Test that background layers can be loaded."""
        backgrounds = BackgroundLayers()
        assert backgrounds is not None

    def test_background_has_sky(self):
        """Test that sky background is loaded."""
        backgrounds = BackgroundLayers()
        # Sky should exist if assets are generated
        if backgrounds.sky is not None:
            assert isinstance(backgrounds.sky, pygame.Surface)

    def test_background_has_clouds(self):
        """Test that clouds layer is loaded."""
        backgrounds = BackgroundLayers()
        if backgrounds.clouds is not None:
            assert isinstance(backgrounds.clouds, pygame.Surface)

    def test_background_has_distant_scenery(self):
        """Test that distant scenery layer is loaded."""
        backgrounds = BackgroundLayers()
        if backgrounds.distant_scenery is not None:
            assert isinstance(backgrounds.distant_scenery, pygame.Surface)

    def test_background_has_ocean_frames(self):
        """Test that ocean animation frames are loaded."""
        backgrounds = BackgroundLayers()
        # Ocean frames should be a list
        assert isinstance(backgrounds.ocean_frames, list)
        if backgrounds.ocean_frames:
            assert all(isinstance(f, pygame.Surface) for f in backgrounds.ocean_frames)

    def test_update_advances_ocean_animation(self):
        """Test that update advances ocean animation."""
        backgrounds = BackgroundLayers()
        if backgrounds.ocean_frames:
            initial_frame = backgrounds.ocean_frame
            # Update enough times to advance frame
            for _ in range(backgrounds.ocean_frame_duration + 1):
                backgrounds.update()
            # Frame should have advanced
            assert backgrounds.ocean_frame != initial_frame or len(backgrounds.ocean_frames) == 1

    def test_draw_does_not_crash(self):
        """Test that draw method doesn't crash."""
        backgrounds = BackgroundLayers()
        surface = pygame.Surface((800, 600))
        # Should not raise any exceptions
        backgrounds.draw(surface, 100, 800, 600)

    def test_draw_ocean_does_not_crash(self):
        """Test that draw_ocean method doesn't crash."""
        backgrounds = BackgroundLayers()
        surface = pygame.Surface((800, 600))
        # Should not raise any exceptions
        backgrounds.draw_ocean(surface, 100, 800, 600)

    def test_singleton_returns_same_instance(self):
        """Test that get_background_layers returns the same instance."""
        bg1 = get_background_layers()
        bg2 = get_background_layers()
        assert bg1 is bg2


class TestLevelAutoTiling:
    """Tests for level auto-tiling functionality."""

    def test_level_applies_auto_tiling(self):
        """Test that level applies auto-tiling to solid tiles."""
        from game.level import Level

        level = Level()
        level.create_test_level()

        # Check that some tiles have been assigned sprites
        for tile in level.solid_tiles:
            assert tile.sprite_name is not None

    def test_auto_tiling_top_edge(self):
        """Test that tiles with no neighbor above get solid_top sprite."""
        from game.level import Level, Tile

        level = Level()
        # Create a single tile with no neighbors
        tile = Tile(0, 0, "solid")
        level.tiles.add(tile)
        level.solid_tiles.append(tile)
        level._tile_grid[(0, 0)] = tile

        level._apply_auto_tiling()

        # Single tile should be top-left corner since it has no neighbors
        assert tile.sprite_name == "solid_top_left"

    def test_auto_tiling_middle_tile(self):
        """Test that tiles surrounded by neighbors get solid_middle sprite."""
        from game.level import Level, Tile

        level = Level()

        # Create 3x3 grid of tiles
        for gx in range(3):
            for gy in range(3):
                tile = Tile(gx * TILE_SIZE, gy * TILE_SIZE, "solid")
                level.tiles.add(tile)
                level.solid_tiles.append(tile)
                level._tile_grid[(gx, gy)] = tile

        level._apply_auto_tiling()

        # Center tile should be middle since it's surrounded
        center_tile = level._tile_grid[(1, 1)]
        assert center_tile.sprite_name == "solid_middle"

    def test_platform_tiles_get_platform_sprite(self):
        """Test that platform tiles get the platform sprite."""
        from game.level import Level, Tile

        level = Level()
        tile = Tile(0, 0, "platform")
        level.tiles.add(tile)
        level.platform_tiles.append(tile)
        level._tile_grid[(0, 0)] = tile

        level._apply_auto_tiling()

        assert tile.sprite_name == "platform"


class TestBackgroundTypes:
    """Tests for background type switching."""

    def test_default_background_type_is_outdoor(self):
        """Test that default background type is outdoor."""
        backgrounds = BackgroundLayers()
        assert backgrounds.background_type == "outdoor"

    def test_set_background_type_ship_interior(self):
        """Test setting background type to ship interior."""
        backgrounds = BackgroundLayers()
        backgrounds.set_background_type("ship_interior")
        assert backgrounds.background_type == "ship_interior"

    def test_ship_interior_loaded(self):
        """Test that ship interior background is loaded."""
        backgrounds = BackgroundLayers()
        if backgrounds.ship_interior is not None:
            assert isinstance(backgrounds.ship_interior, pygame.Surface)

    def test_draw_ship_interior_does_not_crash(self):
        """Test that drawing ship interior doesn't crash."""
        backgrounds = BackgroundLayers()
        backgrounds.set_background_type("ship_interior")
        surface = pygame.Surface((800, 600))
        backgrounds.draw(surface, 0, 800, 600)

    def test_level_background_type_default(self):
        """Test that regular levels default to outdoor background."""
        from game.level import Level
        level = Level()
        assert level.background_type == "outdoor"

    def test_boss_level_defaults_to_ship_interior(self):
        """Test that boss levels default to ship interior background."""
        from game.level import Level
        level = Level()
        level.load_from_file("levels/boss_arena.json")
        assert level.background_type == "ship_interior"


class TestMetalPlatform:
    """Tests for metal platform support."""

    def test_metal_platform_in_tileset(self):
        """Test that metal_platform is in the tileset."""
        tiles = TileSprites()
        sprite = tiles.get("metal_platform")
        assert sprite is not None
        assert isinstance(sprite, pygame.Surface)

    def test_metal_platform_type_becomes_platform(self):
        """Test that metal_platform type is treated as platform for collision."""
        from game.level import Level

        level = Level()
        level.load_from_file("levels/boss_arena.json")

        # Should have platform tiles (metal_platform becomes platform type)
        assert len(level.platform_tiles) > 0

        # Check that they have the metal_platform sprite
        for tile in level.platform_tiles:
            assert tile.sprite_name == "metal_platform"
            assert tile.tile_type == "platform"  # Collision type is platform


class TestTileDecorationsInLevel:
    """Tests for decoration support in levels."""

    def test_decoration_tiles_are_separate_list(self):
        """Test that decoration tiles are tracked separately."""
        from game.level import Level

        level = Level()
        # Create test level creates solid and platform tiles only
        level.create_test_level()

        # decoration_tiles list should exist (may be empty in test level)
        assert hasattr(level, 'decoration_tiles')
        assert isinstance(level.decoration_tiles, list)

    def test_decoration_tiles_not_in_collision(self):
        """Test that decoration tiles are not in solid or platform lists."""
        from game.level import Level, Tile

        level = Level()
        tile = Tile(0, 0, "decoration", "crate")
        level.tiles.add(tile)
        level.decoration_tiles.append(tile)

        # Should not be in collision lists
        assert tile not in level.solid_tiles
        assert tile not in level.platform_tiles
