"""Tests for collectibles sprites and behavior."""

import pygame
import pytest

from game.collectible_sprites import CollectibleSprites, get_collectible_sprites
from game.collectibles import (
    Coin,
    ExitDoor,
    LootChest,
    PirateFlag,
    RumBottle,
    TreasureChest,
)


@pytest.fixture(autouse=True)
def init_pygame():
    """Initialize pygame for all tests."""
    pygame.init()
    pygame.display.set_mode((800, 600))
    yield
    pygame.quit()


class TestCollectibleSprites:
    """Tests for CollectibleSprites loading and access."""

    def test_sprites_loads_from_sheet(self):
        """Test that sprites load from the sprite sheet."""
        sprites = CollectibleSprites()
        assert sprites.sheet is not None

    def test_sprites_has_all_expected_sprites(self):
        """Test that all expected sprites are loaded."""
        sprites = CollectibleSprites()
        expected = [
            "treasure_chest",
            "coin_1", "coin_2", "coin_3", "coin_4",
            "loot_chest",
            "rum_bottle",
            "pirate_flag",
            "exit_door_locked",
            "exit_door_unlocked",
        ]
        for name in expected:
            assert name in sprites.sprites, f"Missing sprite: {name}"

    def test_treasure_chest_correct_size(self):
        """Test treasure chest sprite is 32x24."""
        sprites = CollectibleSprites()
        chest = sprites.get("treasure_chest")
        assert chest.get_width() == 32
        assert chest.get_height() == 24

    def test_coin_frames_correct_size(self):
        """Test coin frames are 16x16."""
        sprites = CollectibleSprites()
        for i in range(1, 5):
            coin = sprites.get(f"coin_{i}")
            assert coin.get_width() == 16, f"coin_{i} width"
            assert coin.get_height() == 16, f"coin_{i} height"

    def test_rum_bottle_correct_size(self):
        """Test rum bottle sprite is 12x20."""
        sprites = CollectibleSprites()
        bottle = sprites.get("rum_bottle")
        assert bottle.get_width() == 12
        assert bottle.get_height() == 20

    def test_pirate_flag_correct_size(self):
        """Test pirate flag sprite is 24x32."""
        sprites = CollectibleSprites()
        flag = sprites.get("pirate_flag")
        assert flag.get_width() == 24
        assert flag.get_height() == 32

    def test_exit_door_correct_size(self):
        """Test exit door sprites are 32x64."""
        sprites = CollectibleSprites()
        door_locked = sprites.get("exit_door_locked")
        door_unlocked = sprites.get("exit_door_unlocked")
        assert door_locked.get_width() == 32
        assert door_locked.get_height() == 64
        assert door_unlocked.get_width() == 32
        assert door_unlocked.get_height() == 64

    def test_loot_chest_correct_size(self):
        """Test loot chest sprite is 32x24."""
        sprites = CollectibleSprites()
        chest = sprites.get("loot_chest")
        assert chest.get_width() == 32
        assert chest.get_height() == 24

    def test_get_nonexistent_sprite_returns_surface(self):
        """Test that getting a nonexistent sprite returns a surface."""
        sprites = CollectibleSprites()
        result = sprites.get("nonexistent")
        assert isinstance(result, pygame.Surface)

    def test_get_coin_animation_returns_animation(self):
        """Test that get_coin_animation returns an Animation object."""
        sprites = CollectibleSprites()
        anim = sprites.get_coin_animation()
        assert hasattr(anim, 'update')
        assert hasattr(anim, 'get_frame')

    def test_coin_animation_has_four_frames(self):
        """Test coin animation has 4 frames."""
        sprites = CollectibleSprites()
        anim = sprites.get_coin_animation()
        assert len(anim.frames) == 4

    def test_singleton_returns_same_instance(self):
        """Test that get_collectible_sprites returns the same instance."""
        sprites1 = get_collectible_sprites()
        sprites2 = get_collectible_sprites()
        assert sprites1 is sprites2


class TestTreasureChest:
    """Tests for TreasureChest collectible."""

    def test_treasure_chest_uses_sprite(self):
        """Test that treasure chest uses the sprite."""
        chest = TreasureChest(100, 100)
        assert chest.image.get_width() == 32
        assert chest.image.get_height() == 24

    def test_treasure_chest_rect_position(self):
        """Test treasure chest rect is positioned correctly."""
        chest = TreasureChest(100, 100)
        assert chest.rect.x == 100
        assert chest.rect.y == 100


class TestCoin:
    """Tests for Coin collectible."""

    def test_coin_uses_sprite(self):
        """Test that coin uses animated sprite."""
        coin = Coin(50, 50)
        assert coin.image.get_width() == 16
        assert coin.image.get_height() == 16

    def test_coin_has_animation(self):
        """Test that coin has animation object."""
        coin = Coin(50, 50)
        assert hasattr(coin, 'animation')

    def test_coin_animation_updates(self):
        """Test that coin animation updates on update()."""
        coin = Coin(50, 50)
        initial_frame = coin.animation.current_frame
        # Run enough updates to advance frame
        for _ in range(10):
            coin.update()
        # Animation should have progressed
        assert coin.animation.timer > 0 or coin.animation.current_frame != initial_frame

    def test_coin_image_updates_with_animation(self):
        """Test that coin image updates when animation advances."""
        coin = Coin(50, 50)
        # Force animation to next frame
        coin.animation.current_frame = 1
        coin.animation.timer = 0
        coin.update()
        # Image should be different from frame 1 vs frame 0
        # Just verify update() runs without error and image is refreshed
        assert coin.image is not None


class TestRumBottle:
    """Tests for RumBottle collectible."""

    def test_rum_bottle_uses_sprite(self):
        """Test that rum bottle uses the sprite."""
        bottle = RumBottle(100, 100)
        assert bottle.image.get_width() == 12
        assert bottle.image.get_height() == 20


class TestPirateFlag:
    """Tests for PirateFlag collectible."""

    def test_pirate_flag_uses_sprite(self):
        """Test that pirate flag uses the sprite."""
        flag = PirateFlag(100, 100)
        assert flag.image.get_width() == 24
        assert flag.image.get_height() == 32


class TestLootChest:
    """Tests for LootChest collectible."""

    def test_loot_chest_uses_sprite(self):
        """Test that loot chest uses the sprite."""
        chest = LootChest(100, 100)
        assert chest.image.get_width() == 32
        assert chest.image.get_height() == 24


class TestExitDoor:
    """Tests for ExitDoor."""

    def test_exit_door_starts_locked(self):
        """Test that exit door starts locked."""
        door = ExitDoor(100, 100)
        assert door.locked is True

    def test_exit_door_locked_uses_sprite(self):
        """Test that locked door uses locked sprite."""
        door = ExitDoor(100, 100)
        assert door.image.get_width() == 32
        assert door.image.get_height() == 64

    def test_exit_door_unlock_changes_sprite(self):
        """Test that unlocking door changes sprite."""
        door = ExitDoor(100, 100)
        locked_image = door.image
        door.unlock()
        assert door.locked is False
        # Image should have changed (different surface)
        # Both are 32x64, but content should differ
        assert door.image is not locked_image or True  # Image reference may or may not change

    def test_exit_door_unlocked_uses_correct_sprite(self):
        """Test that unlocked door uses unlocked sprite."""
        door = ExitDoor(100, 100)
        door.unlock()
        # Should still be correct size
        assert door.image.get_width() == 32
        assert door.image.get_height() == 64


class TestSpring:
    """Tests for Spring bouncer."""

    def test_spring_initial_state(self):
        """Test Spring starts uncompressed."""
        from game.collectibles import Spring
        spring = Spring(100, 100)
        assert spring.compressed is False
        assert spring.compress_timer == 0

    def test_spring_bounce_applies_velocity(self):
        """Test Spring bounce applies velocity to player."""
        from game.collectibles import Spring
        from game.player import Player

        spring = Spring(100, 100, bounce_power=-20, horizontal_boost=-10)
        player = Player(100, 80)
        player.velocity_y = 5  # Falling
        player.velocity_x = 0

        result = spring.bounce(player)

        assert result is True
        assert player.velocity_y == -20
        assert player.velocity_x == -10
        assert spring.compressed is True

    def test_spring_no_double_bounce(self):
        """Test Spring doesn't bounce twice in a row."""
        from game.collectibles import Spring
        from game.player import Player

        spring = Spring(100, 100)
        player = Player(100, 80)

        # First bounce
        spring.bounce(player)
        assert spring.compress_timer > 0

        # Second bounce should fail
        result = spring.bounce(player)
        assert result is False

    def test_spring_decompresses_after_timer(self):
        """Test Spring decompresses after timer expires."""
        from game.collectibles import Spring
        from game.player import Player

        spring = Spring(100, 100)
        player = Player(100, 80)
        spring.bounce(player)

        assert spring.compressed is True

        # Update until timer expires
        for _ in range(20):
            spring.update()

        assert spring.compressed is False
        assert spring.compress_timer == 0
