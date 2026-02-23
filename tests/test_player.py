"""Tests for the Player class."""

import pygame
import pytest

from game.player import Player
from game.settings import (
    ATTACK_DURATION,
    INVINCIBILITY_FRAMES,
    PLAYER_HEIGHT,
    PLAYER_JUMP_POWER,
    PLAYER_MAX_HEALTH,
    PLAYER_SPEED,
    PLAYER_WIDTH,
)


@pytest.fixture(autouse=True)
def init_pygame():
    """Initialize pygame for tests."""
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.HIDDEN)
    yield
    pygame.quit()


class TestPlayerInitialization:
    """Tests for Player initialization."""

    def test_player_initial_position(self):
        """Test player spawns at correct position."""
        player = Player(100, 200)
        assert player.rect.x == 100
        assert player.rect.y == 200

    def test_player_animation_frame_size(self):
        """Test player animation frames have correct dimensions."""
        player = Player(0, 0)
        # Check that animation frames are correct size
        idle_anim = player.sprite.animations["idle"]
        frame = idle_anim.get_frame()
        assert frame.get_width() == PLAYER_WIDTH
        assert frame.get_height() == PLAYER_HEIGHT

    def test_player_initial_health(self):
        """Test player starts with full health."""
        player = Player(0, 0)
        assert player.health == PLAYER_MAX_HEALTH
        assert player.max_health == PLAYER_MAX_HEALTH

    def test_player_initial_lives(self):
        """Test player starts with 3 lives."""
        player = Player(0, 0)
        assert player.lives == 3

    def test_player_initial_state(self):
        """Test player initial state flags."""
        player = Player(0, 0)
        assert player.velocity_x == 0
        assert player.velocity_y == 0
        assert player.on_ground is False
        assert player.facing_right is True
        assert player.attacking is False
        assert player.invincible is False

    def test_player_has_animations(self):
        """Test player has required animations loaded."""
        player = Player(0, 0)
        assert "idle" in player.sprite.animations
        assert "run" in player.sprite.animations
        assert "jump" in player.sprite.animations
        assert "fall" in player.sprite.animations
        assert "attack" in player.sprite.animations
        assert "hurt" in player.sprite.animations

    def test_player_starts_with_idle_animation(self):
        """Test player starts playing idle animation."""
        player = Player(0, 0)
        assert player.sprite.current_animation == "idle"


class TestPlayerMovement:
    """Tests for Player movement and input handling."""

    def test_move_right(self):
        """Test moving right sets velocity and facing."""
        player = Player(0, 0)
        keys = MockKeys({pygame.K_RIGHT: True})
        player.handle_input(keys)
        assert player.velocity_x == PLAYER_SPEED
        assert player.facing_right is True

    def test_move_left(self):
        """Test moving left sets velocity and facing."""
        player = Player(0, 0)
        keys = MockKeys({pygame.K_LEFT: True})
        player.handle_input(keys)
        assert player.velocity_x == -PLAYER_SPEED
        assert player.facing_right is False

    def test_move_with_wasd(self):
        """Test WASD controls work."""
        player = Player(0, 0)
        keys = MockKeys({pygame.K_d: True})
        player.handle_input(keys)
        assert player.velocity_x == PLAYER_SPEED

        keys = MockKeys({pygame.K_a: True})
        player.handle_input(keys)
        assert player.velocity_x == -PLAYER_SPEED

    def test_no_input_stops_movement(self):
        """Test releasing keys stops horizontal movement."""
        player = Player(0, 0)
        player.velocity_x = PLAYER_SPEED

        keys = MockKeys({})
        player.handle_input(keys)
        assert player.velocity_x == 0

    def test_jump_when_on_ground(self):
        """Test jumping sets vertical velocity when on ground."""
        player = Player(0, 0)
        player.on_ground = True

        keys = MockKeys({pygame.K_SPACE: True})
        player.handle_input(keys)

        assert player.velocity_y == PLAYER_JUMP_POWER
        assert player.on_ground is False

    def test_no_jump_when_airborne(self):
        """Test can't jump when already in air."""
        player = Player(0, 0)
        player.on_ground = False
        player.velocity_y = 5

        keys = MockKeys({pygame.K_SPACE: True})
        player.handle_input(keys)

        assert player.velocity_y == 5  # Unchanged

    def test_jump_with_w_key(self):
        """Test W key triggers jump."""
        player = Player(0, 0)
        player.on_ground = True

        keys = MockKeys({pygame.K_w: True})
        player.handle_input(keys)

        assert player.velocity_y == PLAYER_JUMP_POWER

    def test_jump_with_up_arrow(self):
        """Test Up arrow triggers jump."""
        player = Player(0, 0)
        player.on_ground = True

        keys = MockKeys({pygame.K_UP: True})
        player.handle_input(keys)

        assert player.velocity_y == PLAYER_JUMP_POWER


class TestPlayerCombat:
    """Tests for Player combat system."""

    def test_attack_returns_hitbox(self):
        """Test attack returns a hitbox."""
        player = Player(100, 100)
        hitbox = player.attack()
        assert hitbox is not None
        assert isinstance(hitbox, pygame.Rect)

    def test_attack_sets_attacking_flag(self):
        """Test attack sets the attacking state."""
        player = Player(0, 0)
        player.attack()
        assert player.attacking is True
        assert player.attack_timer == ATTACK_DURATION

    def test_attack_clears_hit_tracking(self):
        """Test new attack clears the enemies_hit_this_attack set."""
        player = Player(0, 0)
        # Simulate having hit an enemy previously
        player.enemies_hit_this_attack.add(12345)
        assert len(player.enemies_hit_this_attack) == 1

        # Start new attack
        player.attack()

        # Set should be cleared
        assert len(player.enemies_hit_this_attack) == 0

    def test_attack_cooldown_prevents_attack(self):
        """Test can't attack during cooldown."""
        player = Player(0, 0)
        player.attack()
        player.attacking = False  # Simulate attack ending

        # Still on cooldown
        hitbox = player.attack()
        assert hitbox is None

    def test_attack_hitbox_direction_right(self):
        """Test attack hitbox is to the right when facing right."""
        player = Player(100, 100)
        player.facing_right = True
        hitbox = player.attack()

        assert hitbox.left == player.rect.right

    def test_attack_hitbox_direction_left(self):
        """Test attack hitbox is to the left when facing left."""
        player = Player(100, 100)
        player.facing_right = False
        hitbox = player.attack()

        assert hitbox.right == player.rect.left

    def test_attack_triggers_animation(self):
        """Test attack triggers attack animation."""
        player = Player(0, 0)
        player.attack()
        assert player.sprite.current_animation == "attack"

    def test_attack_timer_decrements(self):
        """Test attack timer decrements each update."""
        player = Player(0, 0)
        player.attack()
        initial_timer = player.attack_timer

        player.update()

        assert player.attack_timer == initial_timer - 1

    def test_attack_ends_after_duration(self):
        """Test attack ends after duration expires."""
        player = Player(0, 0)
        player.attack()

        for _ in range(ATTACK_DURATION + 1):
            player.update()

        assert player.attacking is False


class TestPlayerDamage:
    """Tests for Player damage and health system."""

    def test_take_damage_reduces_health(self):
        """Test taking damage reduces health."""
        player = Player(0, 0)
        initial_health = player.health

        player.take_damage(1)

        assert player.health == initial_health - 1

    def test_take_damage_grants_invincibility(self):
        """Test taking damage grants invincibility frames."""
        player = Player(0, 0)
        player.take_damage(1)

        assert player.invincible is True
        assert player.invincibility_timer == INVINCIBILITY_FRAMES

    def test_invincible_prevents_damage(self):
        """Test can't take damage while invincible."""
        player = Player(0, 0)
        player.invincible = True
        initial_health = player.health

        result = player.take_damage(1)

        assert result is False
        assert player.health == initial_health

    def test_take_damage_triggers_hurt_animation(self):
        """Test taking damage triggers hurt animation."""
        player = Player(0, 0)
        player.take_damage(1)

        assert player.hurt_timer > 0
        player._update_animation_state()
        assert player.sprite.current_animation == "hurt"

    def test_invincibility_expires(self):
        """Test invincibility expires after timer."""
        player = Player(0, 0)
        player.take_damage(1)

        for _ in range(INVINCIBILITY_FRAMES + 1):
            player.update()

        assert player.invincible is False

    def test_death_reduces_lives(self):
        """Test dying reduces lives."""
        player = Player(0, 0)
        player.health = 1

        player.take_damage(1)

        assert player.lives == 2

    def test_respawn_restores_health(self):
        """Test respawning restores health."""
        player = Player(0, 0)
        player.health = 1
        player.take_damage(1)

        assert player.health == PLAYER_MAX_HEALTH

    def test_heal_restores_health(self):
        """Test heal method restores health."""
        player = Player(0, 0)
        player.health = 2

        player.heal(2)

        assert player.health == 4

    def test_heal_caps_at_max(self):
        """Test heal doesn't exceed max health."""
        player = Player(0, 0)
        player.health = PLAYER_MAX_HEALTH - 1

        player.heal(5)

        assert player.health == PLAYER_MAX_HEALTH


class TestPlayerAnimationStates:
    """Tests for Player animation state machine."""

    def test_idle_animation_when_stationary(self):
        """Test idle animation plays when not moving."""
        player = Player(0, 0)
        player.on_ground = True
        player.velocity_x = 0

        player._update_animation_state()

        assert player.sprite.current_animation == "idle"

    def test_run_animation_when_moving(self):
        """Test run animation plays when moving horizontally."""
        player = Player(0, 0)
        player.on_ground = True
        player.velocity_x = PLAYER_SPEED

        player._update_animation_state()

        assert player.sprite.current_animation == "run"

    def test_jump_animation_when_rising(self):
        """Test jump animation plays when rising."""
        player = Player(0, 0)
        player.on_ground = False
        player.velocity_y = -10

        player._update_animation_state()

        assert player.sprite.current_animation == "jump"

    def test_fall_animation_when_falling(self):
        """Test fall animation plays when falling."""
        player = Player(0, 0)
        player.on_ground = False
        player.velocity_y = 10

        player._update_animation_state()

        assert player.sprite.current_animation == "fall"

    def test_attack_animation_priority(self):
        """Test attack animation takes priority over movement."""
        player = Player(0, 0)
        player.on_ground = True
        player.velocity_x = PLAYER_SPEED
        player.attacking = True

        player._update_animation_state()

        assert player.sprite.current_animation == "attack"

    def test_hurt_animation_priority(self):
        """Test hurt animation takes priority over everything."""
        player = Player(0, 0)
        player.attacking = True
        player.hurt_timer = 10

        player._update_animation_state()

        assert player.sprite.current_animation == "hurt"

    def test_facing_direction_updates_sprite(self):
        """Test facing direction is synced to sprite."""
        player = Player(0, 0)
        player.facing_right = False

        player._update_animation_state()

        assert player.sprite.facing_right is False


class TestPlayerPowerups:
    """Tests for Player power-up system."""

    def test_parrot_timer_decrements(self):
        """Test parrot timer decrements each update."""
        player = Player(0, 0)
        player.has_parrot = True
        player.parrot_timer = 100

        player.update()

        assert player.parrot_timer == 99

    def test_parrot_expires(self):
        """Test parrot power-up expires when timer hits 0."""
        player = Player(0, 0)
        player.has_parrot = True
        player.parrot_timer = 1

        player.update()

        assert player.has_parrot is False

    def test_grog_timer_decrements(self):
        """Test grog timer decrements each update."""
        player = Player(0, 0)
        player.has_grog = True
        player.grog_timer = 100
        player.damage_multiplier = 2

        player.update()

        assert player.grog_timer == 99

    def test_grog_expires_resets_damage(self):
        """Test grog expiring resets damage multiplier."""
        player = Player(0, 0)
        player.has_grog = True
        player.grog_timer = 1
        player.damage_multiplier = 2

        player.update()

        assert player.has_grog is False
        assert player.damage_multiplier == 1


class TestPlayerUpdate:
    """Tests for Player update method."""

    def test_update_applies_gravity(self):
        """Test gravity is applied each update."""
        player = Player(0, 0)
        player.velocity_y = 0

        player.update()

        assert player.velocity_y > 0

    def test_update_caps_fall_speed(self):
        """Test fall speed is capped."""
        player = Player(0, 0)
        player.velocity_y = 100

        player.update()

        from game.settings import MAX_FALL_SPEED
        assert player.velocity_y <= MAX_FALL_SPEED

    def test_update_moves_player(self):
        """Test player position updates based on velocity."""
        player = Player(100, 100)
        player.velocity_x = 5
        player.velocity_y = 0

        player.update()

        assert player.rect.x == 105

    def test_update_updates_animation(self):
        """Test update calls animation update."""
        player = Player(0, 0)
        # Get whichever animation is current after update
        player.on_ground = True
        player.velocity_x = 0
        player.update()

        # The idle animation should have its timer incremented
        idle_anim = player.sprite.animations["idle"]
        # Timer should be 1 after one update (started at 0)
        assert idle_anim.timer == 1

    def test_update_refreshes_image(self):
        """Test update refreshes the image from animation."""
        player = Player(0, 0)

        player.update()

        # Image should be updated (may or may not be same surface)
        assert player.image is not None


class MockKeys:
    """Mock for pygame key state."""

    def __init__(self, pressed: dict):
        self.pressed = pressed

    def __getitem__(self, key):
        return self.pressed.get(key, False)
