"""Tests for enemy classes."""

import pygame
import pytest

from game.enemies import Admiral, AdmiralBullet, Cannon, Cannonball, Officer
from game.settings import (
    ADMIRAL_HEALTH,
    ADMIRAL_PHASE_2_THRESHOLD,
    ADMIRAL_PHASE_3_THRESHOLD,
    OFFICER_HEALTH,
)


@pytest.fixture(autouse=True)
def init_pygame():
    """Initialize pygame for all tests."""
    pygame.init()
    yield
    pygame.quit()


@pytest.fixture
def projectile_group():
    """Create a sprite group for projectiles."""
    return pygame.sprite.Group()


@pytest.fixture
def player_rect():
    """Create a player rect for testing."""
    return pygame.Rect(100, 100, 32, 48)


class TestOfficer:
    """Tests for Officer enemy."""

    def test_officer_initial_state(self):
        """Officer should start with correct health and not attacking."""
        officer = Officer(100, 100)
        assert officer.health == OFFICER_HEALTH
        assert not officer.attacking
        assert officer.attack_timer == 0
        assert officer.attack_cooldown == 0

    def test_officer_chases_player_in_range(self):
        """Officer should move toward player when in chase range."""
        officer = Officer(100, 100)
        player_rect = pygame.Rect(200, 100, 32, 48)  # Player to the right

        initial_x = officer.rect.x
        for _ in range(10):
            officer.update(player_rect)

        assert officer.rect.x > initial_x  # Moved right toward player
        assert officer.facing_right

    def test_officer_attacks_when_close(self):
        """Officer should attack when player is within attack range."""
        officer = Officer(100, 100)
        player_rect = pygame.Rect(110, 100, 32, 48)  # Very close

        officer.update(player_rect)

        assert officer.attacking
        assert officer.attack_timer > 0

    def test_officer_attack_hitbox_exists_when_attacking(self):
        """Officer should have attack hitbox only when attacking."""
        officer = Officer(100, 100)

        # Not attacking - no hitbox
        assert officer.get_attack_hitbox() is None

        # Trigger attack
        player_rect = pygame.Rect(110, 100, 32, 48)
        officer.update(player_rect)

        # Now attacking - should have hitbox
        hitbox = officer.get_attack_hitbox()
        assert hitbox is not None
        assert isinstance(hitbox, pygame.Rect)

    def test_officer_attack_hitbox_direction(self):
        """Attack hitbox should be on correct side based on facing direction."""
        officer = Officer(100, 100)

        # Attack facing right
        player_rect = pygame.Rect(130, 100, 32, 48)
        officer.update(player_rect)
        hitbox_right = officer.get_attack_hitbox()
        assert hitbox_right.left >= officer.rect.right - 5  # Hitbox to the right

        # Reset and attack facing left
        officer2 = Officer(200, 100)
        player_rect_left = pygame.Rect(170, 100, 32, 48)
        officer2.update(player_rect_left)
        hitbox_left = officer2.get_attack_hitbox()
        assert hitbox_left.right <= officer2.rect.left + 5  # Hitbox to the left

    def test_officer_respects_attack_cooldown(self):
        """Officer should not attack again until cooldown expires."""
        officer = Officer(100, 100)
        player_rect = pygame.Rect(110, 100, 32, 48)

        # First attack
        officer.update(player_rect)
        assert officer.attacking

        # Run through attack duration
        for _ in range(30):
            officer.update(player_rect)

        # Should be on cooldown now, not attacking again immediately
        assert officer.attack_cooldown > 0 or officer.attacking

    def test_officer_ignores_player_at_different_height(self):
        """Officer should not chase player on different platform."""
        officer = Officer(100, 100)
        player_rect = pygame.Rect(150, 300, 32, 48)  # Far below

        initial_x = officer.rect.x
        for _ in range(10):
            officer.update(player_rect)

        assert officer.rect.x == initial_x  # Didn't move


class TestCannon:
    """Tests for Cannon enemy."""

    def test_cannon_initial_state(self, projectile_group):
        """Cannon should start with correct settings."""
        cannon = Cannon(100, 100, projectile_group, faces_right=True)
        assert cannon.health == 2
        assert cannon.faces_right
        assert len(projectile_group) == 0

    def test_cannon_fires_periodically(self, projectile_group):
        """Cannon should fire cannonballs at regular intervals."""
        cannon = Cannon(100, 100, projectile_group, faces_right=True)
        cannon.shoot_timer = 1  # About to fire

        cannon.update()

        assert len(projectile_group) == 1
        assert isinstance(list(projectile_group)[0], Cannonball)

    def test_cannon_direction(self, projectile_group):
        """Cannonball should travel in cannon's facing direction."""
        # Right-facing cannon
        cannon_right = Cannon(100, 100, projectile_group, faces_right=True)
        cannon_right.shoot_timer = 1
        cannon_right.update()

        cannonball = list(projectile_group)[0]
        assert cannonball.velocity_x > 0  # Moving right

        # Left-facing cannon
        projectile_group.empty()
        cannon_left = Cannon(100, 100, projectile_group, faces_right=False)
        cannon_left.shoot_timer = 1
        cannon_left.update()

        cannonball = list(projectile_group)[0]
        assert cannonball.velocity_x < 0  # Moving left

    def test_cannonball_has_arc(self, projectile_group):
        """Cannonball should arc downward due to gravity."""
        cannon = Cannon(100, 100, projectile_group, faces_right=True)
        cannon.shoot_timer = 1
        cannon.update()

        cannonball = list(projectile_group)[0]
        initial_vy = cannonball.velocity_y

        # Update a few times
        for _ in range(10):
            cannonball.update()

        # Velocity should have increased (more downward)
        assert cannonball.velocity_y > initial_vy


class TestAdmiral:
    """Tests for Admiral boss."""

    def test_admiral_initial_state(self, projectile_group):
        """Admiral should start with correct health and phase 1."""
        boss = Admiral(400, 400, projectile_group)
        assert boss.health == ADMIRAL_HEALTH
        assert boss.max_health == ADMIRAL_HEALTH
        assert boss.phase == 1
        assert boss.state == Admiral.STATE_IDLE

    def test_admiral_phase_transitions(self, projectile_group):
        """Admiral should change phases at health thresholds."""
        boss = Admiral(400, 400, projectile_group)

        # Phase 1
        assert boss.current_phase == 1

        # Damage to phase 2 threshold
        damage_to_phase2 = ADMIRAL_HEALTH - ADMIRAL_PHASE_2_THRESHOLD
        boss.take_damage(damage_to_phase2)
        assert boss.current_phase == 2
        assert boss.state == Admiral.STATE_STUNNED  # Brief stun on phase change

        # Damage to phase 3 threshold
        damage_to_phase3 = ADMIRAL_PHASE_2_THRESHOLD - ADMIRAL_PHASE_3_THRESHOLD
        boss.take_damage(damage_to_phase3)
        assert boss.current_phase == 3
        assert boss.state == Admiral.STATE_STUNNED

    def test_admiral_death(self, projectile_group):
        """Admiral should die when health reaches 0."""
        boss = Admiral(400, 400, projectile_group)

        result = boss.take_damage(ADMIRAL_HEALTH)

        assert result  # Died
        assert not boss.active

    def test_admiral_sword_attack_hitbox(self, projectile_group, player_rect):
        """Admiral should have hitbox during sword attack."""
        boss = Admiral(400, 400, projectile_group)
        boss.state = Admiral.STATE_SWORD_ATTACK
        boss.state_timer = 15  # Mid-attack

        hitbox = boss.get_attack_hitbox()

        assert hitbox is not None
        assert isinstance(hitbox, pygame.Rect)

    def test_admiral_charge_hitbox(self, projectile_group, player_rect):
        """Admiral should have hitbox during charge attack."""
        boss = Admiral(400, 400, projectile_group)
        boss.state = Admiral.STATE_CHARGE
        boss.state_timer = 30

        hitbox = boss.get_attack_hitbox()

        assert hitbox is not None
        # Charge hitbox is the inflated body rect
        assert hitbox.width > boss.rect.width

    def test_admiral_no_hitbox_when_idle(self, projectile_group):
        """Admiral should not have attack hitbox when idle."""
        boss = Admiral(400, 400, projectile_group)
        boss.state = Admiral.STATE_IDLE

        hitbox = boss.get_attack_hitbox()

        assert hitbox is None

    def test_admiral_pistol_fires_projectile(self, projectile_group, player_rect):
        """Admiral should fire projectile during pistol attack."""
        boss = Admiral(400, 400, projectile_group)
        boss.state = Admiral.STATE_PISTOL_SHOT
        boss.state_timer = 16  # Will be 15 after decrement, triggering fire

        boss.update(player_rect)

        assert len(projectile_group) == 1
        assert isinstance(list(projectile_group)[0], AdmiralBullet)

    def test_admiral_summon_sets_pending(self, projectile_group, player_rect):
        """Admiral summon state should set summon_pending flag."""
        boss = Admiral(400, 400, projectile_group)
        boss.state = Admiral.STATE_SUMMON
        boss.state_timer = 31  # Will be 30 after decrement, triggering summon

        boss.update(player_rect)

        assert boss.summon_pending

    def test_admiral_respects_arena_bounds(self, projectile_group, player_rect):
        """Admiral should stay within arena bounds."""
        boss = Admiral(400, 400, projectile_group)
        boss.set_arena_bounds(100, 700)
        boss.state = Admiral.STATE_WALK
        boss.facing_right = True

        # Walk right until hitting boundary
        for _ in range(500):
            boss.update(player_rect)
            if boss.state == Admiral.STATE_WALK:
                boss.facing_right = True  # Keep going right

        assert boss.rect.x <= 700

    def test_admiral_damage_flash(self, projectile_group):
        """Admiral should have damage flash after taking damage."""
        boss = Admiral(400, 400, projectile_group)

        boss.take_damage(1)

        assert boss.damage_flash > 0

    def test_admiral_states_reachable(self, projectile_group, player_rect):
        """Admiral should be able to reach various combat states."""
        boss = Admiral(400, 400, projectile_group)
        states_seen = set()

        # Run simulation for a while
        for i in range(1000):
            boss.update(player_rect)
            states_seen.add(boss.state)

            # Force state transitions by resetting cooldown
            if i % 100 == 0:
                boss.attack_cooldown = 0
                boss.state_timer = 0

        # Should see at least idle, walk, and one attack state
        assert Admiral.STATE_IDLE in states_seen
        assert Admiral.STATE_WALK in states_seen
        assert len(states_seen) >= 3


class TestProjectiles:
    """Tests for projectile classes."""

    def test_cannonball_moves_with_gravity(self):
        """Cannonball should move and be affected by gravity."""
        ball = Cannonball(100, 100, 1)
        initial_vy = ball.velocity_y

        for _ in range(20):
            ball.update()

        # Should have moved right
        assert ball.rect.x > 100
        # Should have moved down (after initial upward arc)
        assert ball.velocity_y > initial_vy

    def test_admiral_bullet_moves_straight(self):
        """Admiral bullet should move in straight line."""
        bullet = AdmiralBullet(100, 100, 1)
        initial_y = bullet.rect.y

        for _ in range(10):
            bullet.update()

        # Should have moved right
        assert bullet.rect.x > 100
        # Y should be unchanged (no gravity)
        assert bullet.rect.y == initial_y
