"""Tests for level loading."""

import pygame
import pytest

from game.enemies import Admiral, Cannon
from game.level import Level


@pytest.fixture(autouse=True)
def init_pygame():
    """Initialize pygame for all tests."""
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.HIDDEN)
    yield
    pygame.quit()


class TestLevelLoading:
    """Tests for loading levels from JSON."""

    def test_load_boss_level(self):
        """Boss level should load with boss enemy."""
        level = Level()
        level.load_from_file("levels/boss_arena.json")

        assert level.name == "Admiral's Quarters"
        assert level.is_boss_level
        assert level.boss is not None
        assert isinstance(level.boss, Admiral)

    def test_boss_level_has_arena_bounds(self):
        """Boss should have arena bounds set from level data."""
        level = Level()
        level.load_from_file("levels/boss_arena.json")

        boss = level.boss
        assert boss.arena_left == 64
        assert boss.arena_right == 736

    def test_load_level_with_all_enemy_types(self):
        """Level 2 should load all enemy types."""
        level = Level()
        level.load_from_file("levels/level2.json")

        enemy_types = set(type(e).__name__ for e in level.enemies)

        assert "Sailor" in enemy_types
        assert "Musketeer" in enemy_types
        assert "Officer" in enemy_types
        assert "Cannon" in enemy_types

    def test_level2_is_not_boss_level(self):
        """Regular levels should not be marked as boss levels."""
        level = Level()
        level.load_from_file("levels/level2.json")

        assert not level.is_boss_level
        assert level.boss is None

    def test_level1_loads(self):
        """Level 1 should load without errors."""
        level = Level()
        level.load_from_file("levels/level1.json")

        assert level.name == "Port Town"
        assert len(level.tiles) > 0
        assert len(level.enemies) > 0

    def test_cannon_direction_from_level(self):
        """Cannon direction should be set from level data."""
        level = Level()
        level.load_from_file("levels/level2.json")

        cannons = [e for e in level.enemies if isinstance(e, Cannon)]

        # Should have at least one cannon
        assert len(cannons) > 0

        # Check that cannons have facing set
        for cannon in cannons:
            assert hasattr(cannon, 'faces_right')


class TestBossLevelBehavior:
    """Tests for boss level-specific behavior."""

    def test_boss_in_enemies_group(self):
        """Boss should be in the enemies sprite group."""
        level = Level()
        level.load_from_file("levels/boss_arena.json")

        assert level.boss in level.enemies

    def test_boss_level_no_treasure_required(self):
        """Boss level should work without treasure chests."""
        level = Level()
        level.load_from_file("levels/boss_arena.json")

        # Boss levels might have 0 treasure
        assert level.treasure_total >= 0

    def test_boss_shares_projectile_group(self):
        """Boss should use the level's projectile group."""
        level = Level()
        level.load_from_file("levels/boss_arena.json")

        boss = level.boss
        # Trigger a pistol shot (timer decrements then checks, so 16 -> 15)
        boss.state = boss.STATE_PISTOL_SHOT
        boss.state_timer = 16
        boss.update(pygame.Rect(300, 400, 32, 48))

        # Projectile should be in level's group
        assert len(level.projectiles) == 1
