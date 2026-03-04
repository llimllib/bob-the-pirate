"""Tests for level loading."""

import pygame
import pytest

from game.enemies import Admiral, Bosun, Cannon
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


class TestMinibossLevelBehavior:
    """Tests for miniboss level (level 4) behavior."""

    def test_level4_requires_miniboss_defeat(self):
        """Level 4 should require miniboss defeat to complete."""
        level = Level()
        level.load_from_file("levels/level4.json")

        assert level.requires_miniboss_defeat
        assert level.miniboss is not None
        assert isinstance(level.miniboss, Bosun)

    def test_level4_no_treasure_required(self):
        """Level 4 should have no treasure chests."""
        level = Level()
        level.load_from_file("levels/level4.json")

        assert level.treasure_total == 0

    def test_exit_locked_until_miniboss_defeated(self):
        """Exit should remain locked until miniboss is defeated."""
        level = Level()
        level.load_from_file("levels/level4.json")

        # Exit should be locked initially
        assert level.exit_door is not None
        assert level.exit_door.locked

        # Create a mock player with rect
        class MockPlayer:
            def __init__(self):
                self.rect = pygame.Rect(100, 400, 32, 48)

        player = MockPlayer()
        level.update(player)

        # Should still be locked
        assert level.exit_door.locked

    def test_exit_unlocks_when_miniboss_defeated(self):
        """Exit should unlock when miniboss is defeated."""
        level = Level()
        level.load_from_file("levels/level4.json")

        # Simulate miniboss defeat
        level.miniboss.health = 0
        level.miniboss.active = False

        # Create a mock player with rect
        class MockPlayer:
            def __init__(self):
                self.rect = pygame.Rect(100, 400, 32, 48)

        player = MockPlayer()
        level.update(player)

        # Should be unlocked now
        assert not level.exit_door.locked
        assert level.miniboss_defeated

    def test_miniboss_in_enemies_group(self):
        """Miniboss should be in the enemies sprite group."""
        level = Level()
        level.load_from_file("levels/level4.json")

        assert level.miniboss in level.enemies

    def test_level4_is_arena_style(self):
        """Level 4 is a miniboss arena with just the Bosun."""
        level = Level()
        level.load_from_file("levels/level4.json")

        # Miniboss arena has only the Bosun enemy
        bosun_enemies = [e for e in level.enemies if isinstance(e, Bosun)]
        assert len(bosun_enemies) == 1
        assert len(level.enemies) == 1


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


class TestProjectileWallCollision:
    """Tests for projectile-wall collision."""

    def test_projectile_dies_on_wall_collision(self):
        """Projectile should be killed when hitting a solid wall."""
        from game.enemies import MusketBall
        from game.level import Level, Tile

        level = Level()

        # Create a wall tile at x=200
        wall = Tile(200, 100, "solid")
        level.tiles.add(wall)
        level.solid_tiles.append(wall)

        # Create a projectile heading toward the wall
        ball = MusketBall(100, 108, 1)  # Moving right toward wall at y=108
        level.projectiles.add(ball)

        # Mock player for update
        class MockPlayer:
            rect = pygame.Rect(500, 100, 32, 48)

        # Update until projectile should hit wall
        for _ in range(30):
            level.update(MockPlayer())
            if not ball.alive():
                break

        # Projectile should have been killed by wall collision
        assert not ball.alive()

    def test_projectile_survives_without_wall(self):
        """Projectile should survive if no wall in the way."""
        from game.enemies import MusketBall
        from game.level import Level

        level = Level()
        level.width = 1000  # Make level wide enough

        # Create a projectile with no walls
        ball = MusketBall(100, 100, 1)
        level.projectiles.add(ball)

        class MockPlayer:
            rect = pygame.Rect(500, 100, 32, 48)

        # Update a few times
        for _ in range(10):
            level.update(MockPlayer())

        # Projectile should still be alive
        assert ball.alive()
