"""Tests for power-up entities."""

import pygame
import pytest

from game.player import Player
from game.powerups import GhostShield, Parrot


@pytest.fixture(autouse=True)
def init_pygame():
    """Initialize pygame for all tests."""
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.HIDDEN)
    yield
    pygame.quit()


@pytest.fixture
def player():
    """Create a player for testing."""
    return Player(100, 100)


@pytest.fixture
def enemy_group():
    """Create an empty sprite group for enemies."""
    return pygame.sprite.Group()


class TestParrot:
    """Tests for Parrot companion."""

    def test_parrot_initial_state(self, player):
        """Parrot should initialize with correct position and state."""
        parrot = Parrot(player)
        assert parrot.player is player
        assert not parrot.attacking
        assert parrot.attack_cooldown == 0

    def test_parrot_has_animated_sprite(self, player):
        """Parrot should have AnimatedSprite with required animations."""
        parrot = Parrot(player)
        assert parrot.sprite is not None
        assert "flying" in parrot.sprite.animations
        assert "attack" in parrot.sprite.animations

    def test_parrot_starts_with_flying_animation(self, player):
        """Parrot should start with flying animation."""
        parrot = Parrot(player)
        assert parrot.sprite.current_animation == "flying"

    def test_parrot_animation_changes_on_attack(self, player, enemy_group):
        """Parrot animation should change to attack when attacking."""
        parrot = Parrot(player)

        # Simulate attack state
        parrot.attacking = True
        parrot.attack_timer = 0
        parrot.attack_duration = 20
        parrot.update(enemy_group)

        assert parrot.sprite.current_animation == "attack"

    def test_parrot_follows_player(self, player, enemy_group):
        """Parrot should follow player position."""
        parrot = Parrot(player)

        # Update a few times to let parrot follow
        for _ in range(10):
            parrot.update(enemy_group)

        # Parrot should be near player
        assert abs(parrot.rect.centerx - player.rect.centerx) < 50
        assert abs(parrot.rect.centery - player.rect.top) < 50

    def test_parrot_image_updates_from_animation(self, player, enemy_group):
        """Parrot image should update from animation frames."""
        parrot = Parrot(player)

        # Update several times
        for _ in range(20):
            parrot.update(enemy_group)

        # Image should still be valid surface
        assert parrot.image is not None
        assert isinstance(parrot.image, pygame.Surface)


class TestGhostShield:
    """Tests for GhostShield power-up."""

    def test_shield_initial_state(self, player):
        """Shield should start active."""
        shield = GhostShield(player)
        assert shield.active

    def test_shield_absorbs_hit(self, player):
        """Shield should absorb one hit and deactivate."""
        shield = GhostShield(player)

        result = shield.absorb_hit()

        assert result  # Hit was absorbed
        assert not shield.active

    def test_shield_cannot_absorb_twice(self, player):
        """Shield should not absorb after deactivated."""
        shield = GhostShield(player)

        shield.absorb_hit()  # First hit
        result = shield.absorb_hit()  # Second hit

        assert not result  # Not absorbed

    def test_shield_update_animates(self, player):
        """Shield should have animation (pulse_angle changes)."""
        shield = GhostShield(player)
        initial_angle = shield.pulse_angle

        shield.update()

        assert shield.pulse_angle > initial_angle
