"""Tests for the new power-ups: Cannon Shot, Double Jump, Cutlass Fury, Magnet, Monkey."""

import pygame
import pytest

from game.player import Player
from game.settings import (
    ATTACK_COOLDOWN,
    ATTACK_RANGE,
    CUTLASS_FURY_COOLDOWN_MULT,
    CUTLASS_FURY_DURATION,
    CUTLASS_FURY_RANGE_MULT,
    DOUBLE_JUMP_DURATION,
)


@pytest.fixture(autouse=True)
def init_pygame():
    """Initialize pygame for all tests."""
    pygame.init()
    pygame.display.set_mode((800, 600))
    yield
    pygame.quit()


class TestCannonShot:
    """Tests for Cannon Shot power-up."""

    def test_cannon_shot_initial_state(self):
        """Test player starts without cannon shot."""
        player = Player(100, 100)
        assert not player.has_cannon_shot
        assert player.cannon_ammo == 0

    def test_cannon_shot_can_fire_with_ammo(self):
        """Test player can fire cannon when has ammo."""
        player = Player(100, 100)
        player.has_cannon_shot = True
        player.cannon_ammo = 5

        result = player.fire_cannon()
        assert result is True
        assert player.cannon_ammo == 4

    def test_cannon_shot_cannot_fire_without_ammo(self):
        """Test player cannot fire cannon without ammo."""
        player = Player(100, 100)
        player.has_cannon_shot = True
        player.cannon_ammo = 0

        result = player.fire_cannon()
        assert result is False

    def test_cannon_shot_depletes(self):
        """Test cannon shot power-up depletes when ammo runs out."""
        player = Player(100, 100)
        player.has_cannon_shot = True
        player.cannon_ammo = 1

        player.fire_cannon()
        assert player.cannon_ammo == 0
        assert not player.has_cannon_shot

    def test_cannon_shot_respects_cooldown(self):
        """Test cannon shot respects attack cooldown."""
        player = Player(100, 100)
        player.has_cannon_shot = True
        player.cannon_ammo = 5
        player.attack_cooldown = 10  # On cooldown

        result = player.fire_cannon()
        assert result is False
        assert player.cannon_ammo == 5  # Not consumed


class TestDoubleJump:
    """Tests for Double Jump power-up."""

    def test_double_jump_initial_state(self):
        """Test player starts without double jump."""
        player = Player(100, 100)
        assert not player.has_double_jump
        assert player.double_jump_timer == 0
        assert not player.used_double_jump

    def test_double_jump_works_in_air(self):
        """Test double jump works when player is in the air."""
        player = Player(100, 100)
        player.has_double_jump = True
        player.double_jump_timer = DOUBLE_JUMP_DURATION
        player.on_ground = False
        player.velocity_y = 5  # Falling

        result = player.try_double_jump()
        assert result is True
        assert player.velocity_y < 0  # Now going up
        assert player.used_double_jump

    def test_double_jump_fails_on_ground(self):
        """Test double jump doesn't work on ground."""
        player = Player(100, 100)
        player.has_double_jump = True
        player.double_jump_timer = DOUBLE_JUMP_DURATION
        player.on_ground = True

        result = player.try_double_jump()
        assert result is False

    def test_double_jump_cannot_use_twice(self):
        """Test can only double jump once per air time."""
        player = Player(100, 100)
        player.has_double_jump = True
        player.double_jump_timer = DOUBLE_JUMP_DURATION
        player.on_ground = False
        player.used_double_jump = True

        result = player.try_double_jump()
        assert result is False

    def test_double_jump_resets_on_landing(self):
        """Test double jump resets when landing."""
        player = Player(100, 100)
        player.has_double_jump = True
        player.double_jump_timer = DOUBLE_JUMP_DURATION
        player.used_double_jump = True
        player.on_ground = True

        player.update()

        assert not player.used_double_jump

    def test_double_jump_timer_expires(self):
        """Test double jump expires after timer runs out."""
        player = Player(100, 100)
        player.has_double_jump = True
        player.double_jump_timer = 1

        player.update()

        assert not player.has_double_jump


class TestCutlassFury:
    """Tests for Cutlass Fury power-up."""

    def test_cutlass_fury_initial_state(self):
        """Test player starts without cutlass fury."""
        player = Player(100, 100)
        assert not player.has_cutlass_fury
        assert player.cutlass_fury_timer == 0

    def test_cutlass_fury_reduces_cooldown(self):
        """Test cutlass fury reduces attack cooldown."""
        player = Player(100, 100)
        player.has_cutlass_fury = True
        player.cutlass_fury_timer = CUTLASS_FURY_DURATION

        player.attack()

        expected_cooldown = int(ATTACK_COOLDOWN * CUTLASS_FURY_COOLDOWN_MULT)
        assert player.attack_cooldown == expected_cooldown

    def test_cutlass_fury_increases_range(self):
        """Test cutlass fury increases attack range."""
        player = Player(100, 100)
        player.has_cutlass_fury = True
        player.cutlass_fury_timer = CUTLASS_FURY_DURATION

        player.attack()
        hitbox = player.get_attack_hitbox()

        expected_range = int(ATTACK_RANGE * CUTLASS_FURY_RANGE_MULT)
        assert hitbox.width == expected_range

    def test_cutlass_fury_normal_without_powerup(self):
        """Test normal attack range without power-up."""
        player = Player(100, 100)
        assert not player.has_cutlass_fury

        player.attack()
        hitbox = player.get_attack_hitbox()

        assert hitbox.width == ATTACK_RANGE

    def test_cutlass_fury_timer_expires(self):
        """Test cutlass fury expires after timer runs out."""
        player = Player(100, 100)
        player.has_cutlass_fury = True
        player.cutlass_fury_timer = 1

        player.update()

        assert not player.has_cutlass_fury


class TestTreasureMagnet:
    """Tests for Treasure Magnet power-up."""

    def test_magnet_initial_state(self):
        """Test player starts without magnet."""
        player = Player(100, 100)
        assert not player.has_magnet
        assert player.magnet_timer == 0

    def test_magnet_timer_expires(self):
        """Test magnet expires after timer runs out."""
        player = Player(100, 100)
        player.has_magnet = True
        player.magnet_timer = 1

        player.update()

        assert not player.has_magnet


class TestMonkeyMate:
    """Tests for Monkey Mate power-up."""

    def test_monkey_initial_state(self):
        """Test player starts without monkey."""
        player = Player(100, 100)
        assert not player.has_monkey
        assert player.monkey_timer == 0

    def test_monkey_timer_expires(self):
        """Test monkey expires after timer runs out."""
        player = Player(100, 100)
        player.has_monkey = True
        player.monkey_timer = 1

        player.update()

        assert not player.has_monkey


class TestMonkeyEntity:
    """Tests for Monkey companion entity."""

    def test_monkey_creates(self):
        """Test monkey companion can be created."""
        from game.powerups import Monkey

        player = Player(100, 100)
        projectiles = pygame.sprite.Group()
        monkey = Monkey(player, projectiles)

        assert monkey is not None
        assert monkey.player == player

    def test_monkey_follows_player(self):
        """Test monkey follows player position."""
        from game.powerups import Monkey

        player = Player(100, 100)
        projectiles = pygame.sprite.Group()
        monkey = Monkey(player, projectiles)

        # Move player
        player.rect.x = 200

        # Update monkey several times
        enemies = pygame.sprite.Group()
        for _ in range(20):
            monkey.update(enemies)

        # Monkey should be near player
        assert abs(monkey.rect.centerx - player.rect.centerx) < 50


class TestPlayerCannonball:
    """Tests for player-fired cannonball."""

    def test_cannonball_creates(self):
        """Test cannonball can be created."""
        from game.powerups import PlayerCannonball

        cannonball = PlayerCannonball(100, 100, 1)
        assert cannonball is not None
        assert cannonball.velocity_x > 0  # Moving right

    def test_cannonball_moves(self):
        """Test cannonball moves when updated."""
        from game.powerups import PlayerCannonball

        cannonball = PlayerCannonball(100, 100, 1)
        initial_x = cannonball.rect.x

        cannonball.update()

        assert cannonball.rect.x > initial_x

    def test_cannonball_direction(self):
        """Test cannonball respects direction."""
        from game.powerups import PlayerCannonball

        cannonball_right = PlayerCannonball(100, 100, 1)
        cannonball_left = PlayerCannonball(100, 100, -1)

        assert cannonball_right.velocity_x > 0
        assert cannonball_left.velocity_x < 0


class TestCoconut:
    """Tests for coconut projectile."""

    def test_coconut_creates(self):
        """Test coconut can be created."""
        from game.powerups import Coconut

        coconut = Coconut(100, 100, 200, 100)
        assert coconut is not None

    def test_coconut_moves_toward_target(self):
        """Test coconut moves toward target."""
        from game.powerups import Coconut

        coconut = Coconut(100, 100, 200, 100)  # Target to the right
        initial_x = coconut.rect.x

        coconut.update()

        assert coconut.rect.x > initial_x  # Moved right

    def test_coconut_despawns(self):
        """Test coconut despawns after lifetime."""
        from game.powerups import Coconut

        coconut = Coconut(100, 100, 200, 100)
        coconut.lifetime = 1

        group = pygame.sprite.Group()
        group.add(coconut)

        coconut.update()

        assert coconut not in group
