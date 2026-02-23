"""Tests for player innate abilities: Barrel Roll and Anchor Slam."""

import pygame
import pytest

from game.player import Player
from game.settings import (
    ANCHOR_SLAM_COOLDOWN,
    ANCHOR_SLAM_SPEED,
    BARREL_ROLL_COOLDOWN,
    BARREL_ROLL_DURATION,
    BARREL_ROLL_SPEED,
)


@pytest.fixture(autouse=True)
def init_pygame():
    """Initialize pygame for all tests."""
    pygame.init()
    pygame.display.set_mode((800, 600))
    yield
    pygame.quit()


class TestBarrelRoll:
    """Tests for Barrel Roll ability."""

    def test_player_has_roll_state(self):
        """Player should have barrel roll state variables."""
        player = Player(100, 100)
        assert hasattr(player, 'rolling')
        assert hasattr(player, 'roll_timer')
        assert hasattr(player, 'roll_cooldown')
        assert hasattr(player, 'roll_direction')
        assert hasattr(player, 'last_left_tap')
        assert hasattr(player, 'last_right_tap')

    def test_roll_starts_false(self):
        """Player should not be rolling initially."""
        player = Player(100, 100)
        assert player.rolling is False
        assert player.roll_timer == 0
        assert player.roll_cooldown == 0

    def test_single_tap_does_not_roll(self):
        """Single direction tap should not trigger roll."""
        player = Player(100, 100)
        # First tap - should not roll
        result = player.try_barrel_roll(1, 10)
        assert result is False
        assert player.rolling is False

    def test_double_tap_triggers_roll(self):
        """Double-tap within window should trigger roll."""
        player = Player(100, 100)
        # First tap at frame 10
        player.try_barrel_roll(1, 10)
        # Second tap within window at frame 15
        result = player.try_barrel_roll(1, 15)
        assert result is True
        assert player.rolling is True

    def test_double_tap_outside_window_fails(self):
        """Double-tap outside window should not trigger roll."""
        player = Player(100, 100)
        # First tap at frame 10
        player.try_barrel_roll(1, 10)
        # Second tap outside window at frame 50
        result = player.try_barrel_roll(1, 50)
        assert result is False
        assert player.rolling is False

    def test_roll_sets_correct_direction(self):
        """Roll should use the correct direction."""
        player = Player(100, 100)
        # Roll left
        player.try_barrel_roll(-1, 10)
        player.try_barrel_roll(-1, 12)
        assert player.roll_direction == -1

        # Reset
        player.rolling = False
        player.roll_cooldown = 0

        # Roll right
        player.try_barrel_roll(1, 100)
        player.try_barrel_roll(1, 102)
        assert player.roll_direction == 1

    def test_roll_sets_invincibility(self):
        """Rolling should make player invincible."""
        player = Player(100, 100)
        player.try_barrel_roll(1, 10)
        player.try_barrel_roll(1, 12)
        assert player.invincible is True

    def test_roll_timer_set(self):
        """Roll should set timer to duration."""
        player = Player(100, 100)
        player.try_barrel_roll(1, 10)
        player.try_barrel_roll(1, 12)
        assert player.roll_timer == BARREL_ROLL_DURATION

    def test_roll_timer_decrements(self):
        """Roll timer should decrement each update."""
        player = Player(100, 100)
        player.try_barrel_roll(1, 10)
        player.try_barrel_roll(1, 12)
        initial_timer = player.roll_timer
        player.update()
        assert player.roll_timer == initial_timer - 1

    def test_roll_ends_after_duration(self):
        """Roll should end when timer reaches 0."""
        player = Player(100, 100)
        player.try_barrel_roll(1, 10)
        player.try_barrel_roll(1, 12)
        # Update until roll ends
        for _ in range(BARREL_ROLL_DURATION + 1):
            player.update()
        assert player.rolling is False

    def test_roll_sets_cooldown(self):
        """Roll ending should set cooldown."""
        player = Player(100, 100)
        player.try_barrel_roll(1, 10)
        player.try_barrel_roll(1, 12)
        # Run until roll ends - takes BARREL_ROLL_DURATION updates
        # On the last update, roll ends and cooldown is set then decremented
        for _ in range(BARREL_ROLL_DURATION):
            player.update()
        assert player.rolling is False  # Roll has ended
        # Cooldown was set to BARREL_ROLL_COOLDOWN, then decremented once
        assert player.roll_cooldown == BARREL_ROLL_COOLDOWN - 1

    def test_cannot_roll_during_cooldown(self):
        """Cannot start roll during cooldown."""
        player = Player(100, 100)
        player.roll_cooldown = 30
        result = player.try_barrel_roll(1, 10)
        assert result is False

    def test_cannot_roll_while_rolling(self):
        """Cannot start new roll while already rolling."""
        player = Player(100, 100)
        player.try_barrel_roll(1, 10)
        player.try_barrel_roll(1, 12)
        assert player.rolling is True
        # Try to roll again
        result = player.try_barrel_roll(-1, 20)
        assert result is False

    def test_roll_velocity(self):
        """Rolling should set horizontal velocity."""
        player = Player(100, 100)
        player.try_barrel_roll(1, 10)
        player.try_barrel_roll(1, 12)
        keys = pygame.key.get_pressed()
        player.handle_input(keys)
        assert player.velocity_x == BARREL_ROLL_SPEED

    def test_roll_velocity_left(self):
        """Rolling left should set negative velocity."""
        player = Player(100, 100)
        player.try_barrel_roll(-1, 10)
        player.try_barrel_roll(-1, 12)
        keys = pygame.key.get_pressed()
        player.handle_input(keys)
        assert player.velocity_x == -BARREL_ROLL_SPEED


class TestAnchorSlam:
    """Tests for Anchor Slam ability."""

    def test_player_has_slam_state(self):
        """Player should have anchor slam state variables."""
        player = Player(100, 100)
        assert hasattr(player, 'slamming')
        assert hasattr(player, 'slam_cooldown')
        assert hasattr(player, 'slam_landed')

    def test_slam_starts_false(self):
        """Player should not be slamming initially."""
        player = Player(100, 100)
        assert player.slamming is False
        assert player.slam_cooldown == 0
        assert player.slam_landed is False

    def test_cannot_slam_on_ground(self):
        """Cannot start slam while on ground."""
        player = Player(100, 100)
        player.on_ground = True
        result = player.try_anchor_slam()
        assert result is False
        assert player.slamming is False

    def test_can_slam_in_air(self):
        """Can start slam while in air."""
        player = Player(100, 100)
        player.on_ground = False
        result = player.try_anchor_slam()
        assert result is True
        assert player.slamming is True

    def test_slam_sets_velocity(self):
        """Slam should set fast downward velocity."""
        player = Player(100, 100)
        player.on_ground = False
        player.try_anchor_slam()
        assert player.velocity_y == ANCHOR_SLAM_SPEED

    def test_slam_stops_horizontal_velocity(self):
        """Slam should stop horizontal movement."""
        player = Player(100, 100)
        player.on_ground = False
        player.velocity_x = 5
        player.try_anchor_slam()
        assert player.velocity_x == 0

    def test_cannot_slam_during_cooldown(self):
        """Cannot slam during cooldown."""
        player = Player(100, 100)
        player.on_ground = False
        player.slam_cooldown = 30
        result = player.try_anchor_slam()
        assert result is False

    def test_cannot_slam_while_slamming(self):
        """Cannot start new slam while already slamming."""
        player = Player(100, 100)
        player.on_ground = False
        player.try_anchor_slam()
        result = player.try_anchor_slam()
        assert result is False

    def test_slam_landing_returns_true(self):
        """land_anchor_slam should return True on valid landing."""
        player = Player(100, 100)
        player.on_ground = False
        player.try_anchor_slam()
        player.on_ground = True  # Simulate landing
        result = player.land_anchor_slam()
        assert result is True

    def test_slam_landing_sets_cooldown(self):
        """Slam landing should set cooldown."""
        player = Player(100, 100)
        player.on_ground = False
        player.try_anchor_slam()
        player.on_ground = True
        player.land_anchor_slam()
        assert player.slam_cooldown == ANCHOR_SLAM_COOLDOWN

    def test_slam_landing_ends_slam(self):
        """Slam landing should end slamming state."""
        player = Player(100, 100)
        player.on_ground = False
        player.try_anchor_slam()
        player.on_ground = True
        player.land_anchor_slam()
        assert player.slamming is False
        assert player.slam_landed is True

    def test_slam_landing_only_once(self):
        """Slam landing should only trigger once."""
        player = Player(100, 100)
        player.on_ground = False
        player.try_anchor_slam()
        player.on_ground = True
        player.land_anchor_slam()
        # Second call should return False
        result = player.land_anchor_slam()
        assert result is False

    def test_slam_cooldown_decrements(self):
        """Slam cooldown should decrement each update."""
        player = Player(100, 100)
        player.slam_cooldown = 30
        player.update()
        assert player.slam_cooldown == 29

    def test_cannot_slam_while_rolling(self):
        """Cannot slam while rolling."""
        player = Player(100, 100)
        player.on_ground = False
        player.rolling = True
        result = player.try_anchor_slam()
        assert result is False

    def test_cannot_roll_while_slamming(self):
        """Cannot roll while slamming."""
        player = Player(100, 100)
        player.on_ground = False
        player.try_anchor_slam()
        result = player.try_barrel_roll(1, 10)
        assert result is False


class TestAbilityAnimations:
    """Tests for ability animation states."""

    def test_roll_animation_plays(self):
        """Roll should trigger roll animation."""
        player = Player(100, 100)
        player.try_barrel_roll(1, 10)
        player.try_barrel_roll(1, 12)
        player._update_animation_state()
        assert player.sprite.current_animation == "roll"

    def test_slam_animation_plays(self):
        """Slam should trigger slam animation."""
        player = Player(100, 100)
        player.on_ground = False
        player.try_anchor_slam()
        player._update_animation_state()
        assert player.sprite.current_animation == "slam"

    def test_roll_animation_priority_over_run(self):
        """Roll animation should override run animation."""
        player = Player(100, 100)
        player.velocity_x = 5  # Would normally trigger run
        player.try_barrel_roll(1, 10)
        player.try_barrel_roll(1, 12)
        player._update_animation_state()
        assert player.sprite.current_animation == "roll"

    def test_slam_animation_priority_over_fall(self):
        """Slam animation should override fall animation."""
        player = Player(100, 100)
        player.on_ground = False
        player.velocity_y = 5  # Would normally trigger fall
        player.try_anchor_slam()
        player._update_animation_state()
        assert player.sprite.current_animation == "slam"

    def test_hurt_overrides_roll(self):
        """Hurt animation should override roll."""
        player = Player(100, 100)
        player.try_barrel_roll(1, 10)
        player.try_barrel_roll(1, 12)
        player.hurt_timer = 10
        player._update_animation_state()
        assert player.sprite.current_animation == "hurt"


class TestAbilityInputBlocking:
    """Tests for input blocking during abilities."""

    def test_normal_input_blocked_during_roll(self):
        """Normal horizontal input should be blocked during roll."""
        player = Player(100, 100)
        player.try_barrel_roll(1, 10)
        player.try_barrel_roll(1, 12)
        # Simulate pressing left (should be ignored)
        player.velocity_x = 0
        keys = pygame.key.get_pressed()  # No keys pressed
        player.handle_input(keys)
        # Velocity should be roll speed, not 0
        assert player.velocity_x == BARREL_ROLL_SPEED

    def test_normal_input_blocked_during_slam(self):
        """Normal horizontal input should be blocked during slam."""
        player = Player(100, 100)
        player.on_ground = False
        player.velocity_x = 5
        player.try_anchor_slam()
        keys = pygame.key.get_pressed()
        player.handle_input(keys)
        # Velocity should be 0 during slam
        assert player.velocity_x == 0
