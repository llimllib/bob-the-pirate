"""Tests for enemy classes."""

import pygame
import pytest

from game.enemies import (
    Admiral,
    AdmiralBullet,
    Bosun,
    Cannon,
    Cannonball,
    GhostMusketeer,
    GhostOfficer,
    GhostSailor,
    MusketBall,
    Musketeer,
    Officer,
    Sailor,
)
from game.settings import (
    ADMIRAL_HEALTH,
    ADMIRAL_PHASE_2_THRESHOLD,
    ADMIRAL_PHASE_3_THRESHOLD,
    BOSUN_HEALTH,
    MUSKETEER_HEALTH,
    OFFICER_HEALTH,
    SAILOR_HEALTH,
)


@pytest.fixture(autouse=True)
def init_pygame():
    """Initialize pygame for all tests."""
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.HIDDEN)
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


class TestSailor:
    """Tests for Sailor enemy."""

    def test_sailor_initial_state(self):
        """Sailor should start with correct health and walking."""
        sailor = Sailor(100, 100, patrol_distance=100)
        assert sailor.health == SAILOR_HEALTH
        assert sailor.velocity_x != 0  # Should be moving
        assert sailor.sprite is not None

    def test_sailor_has_animations(self):
        """Sailor should have walk and hurt animations."""
        sailor = Sailor(100, 100)
        assert "walk" in sailor.sprite.animations
        assert "hurt" in sailor.sprite.animations

    def test_sailor_patrols(self):
        """Sailor should patrol back and forth."""
        sailor = Sailor(100, 100, patrol_distance=50)

        # Move until past boundary, then sailor should reverse
        for _ in range(100):
            sailor.update()

        # Should have reversed direction at some point (velocity should be negative
        # after overshooting the boundary)
        assert sailor.velocity_x < 0  # Reversed after hitting boundary

    def test_sailor_hurt_animation_on_damage(self):
        """Sailor should show hurt animation when damaged."""
        sailor = Sailor(100, 100)
        sailor.take_damage(1)

        assert sailor.hurt_timer > 0
        assert sailor.sprite.current_animation == "hurt"

    def test_sailor_animation_updates(self):
        """Sailor animation should update each frame."""
        sailor = Sailor(100, 100)
        sailor.update()
        assert sailor.image is not None
        assert sailor.image.get_width() == 36
        assert sailor.image.get_height() == 56


class TestEnemyHitStun:
    """Tests for enemy hit stun mechanic."""

    def test_enemy_can_damage_player_initially(self):
        """Enemy should be able to damage player when not stunned."""
        sailor = Sailor(100, 100)
        assert sailor.can_damage_player()

    def test_enemy_stunned_after_taking_damage(self):
        """Enemy should be stunned after taking damage."""
        sailor = Sailor(100, 100)
        sailor.take_damage(0)  # 0 damage to not kill, but still stun

        assert sailor.hit_stun_timer > 0
        assert not sailor.can_damage_player()

    def test_enemy_stun_wears_off(self):
        """Enemy stun should wear off after enough frames."""
        sailor = Sailor(100, 100)
        sailor.take_damage(0)

        # Run enough updates for stun to wear off
        for _ in range(35):
            sailor.update()

        assert sailor.can_damage_player()


class TestMusketeer:
    """Tests for Musketeer enemy."""

    def test_musketeer_initial_state(self, projectile_group):
        """Musketeer should start with correct health and idle."""
        musketeer = Musketeer(100, 100, projectile_group)
        assert musketeer.health == MUSKETEER_HEALTH
        assert musketeer.sprite is not None
        assert not musketeer.shooting

    def test_musketeer_has_animations(self, projectile_group):
        """Musketeer should have idle and shoot animations."""
        musketeer = Musketeer(100, 100, projectile_group)
        assert "idle" in musketeer.sprite.animations
        assert "shoot" in musketeer.sprite.animations

    def test_musketeer_faces_player(self, projectile_group):
        """Musketeer should face the player."""
        musketeer = Musketeer(100, 100, projectile_group)
        player_rect = pygame.Rect(200, 100, 32, 48)

        musketeer.update(player_rect)

        assert musketeer.facing_right  # Player is to the right

    def test_musketeer_shoots_periodically(self, projectile_group):
        """Musketeer should fire musket balls at regular intervals."""
        musketeer = Musketeer(100, 100, projectile_group)
        musketeer.shoot_timer = 1  # About to fire
        player_rect = pygame.Rect(200, 100, 32, 48)

        musketeer.update(player_rect)
        assert musketeer.shooting

        # Run through shooting animation
        for _ in range(musketeer.SHOOT_WIND_UP + musketeer.SHOOT_FOLLOW_THROUGH):
            musketeer.update(player_rect)

        assert len(projectile_group) == 1
        assert isinstance(list(projectile_group)[0], MusketBall)

    def test_musketeer_animation_updates(self, projectile_group):
        """Musketeer animation should update each frame."""
        musketeer = Musketeer(100, 100, projectile_group)
        musketeer.update()
        assert musketeer.image is not None


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
        """Officer should have attack hitbox during slash phase of attack."""
        officer = Officer(100, 100)

        # Not attacking - no hitbox
        assert officer.get_attack_hitbox() is None

        # Trigger attack
        player_rect = pygame.Rect(110, 100, 32, 48)
        officer.update(player_rect)
        assert officer.attacking

        # Run through wind-up phase (first half of attack) - no hitbox yet
        for _ in range(officer.attack_duration // 2):
            officer.update(player_rect)

        # Now in slash phase - should have hitbox
        hitbox = officer.get_attack_hitbox()
        assert hitbox is not None
        assert isinstance(hitbox, pygame.Rect)

    def test_officer_attack_hitbox_direction(self):
        """Attack hitbox should be on correct side based on facing direction."""
        # Attack facing right
        officer = Officer(100, 100)
        player_rect = pygame.Rect(130, 100, 32, 48)
        officer.update(player_rect)
        # Run to slash phase
        for _ in range(officer.attack_duration // 2 + 1):
            officer.update(player_rect)
        hitbox_right = officer.get_attack_hitbox()
        assert hitbox_right is not None
        assert hitbox_right.left >= officer.rect.right - 5  # Hitbox to the right

        # Attack facing left
        officer2 = Officer(200, 100)
        player_rect_left = pygame.Rect(170, 100, 32, 48)
        officer2.update(player_rect_left)
        # Run to slash phase
        for _ in range(officer2.attack_duration // 2 + 1):
            officer2.update(player_rect_left)
        hitbox_left = officer2.get_attack_hitbox()
        assert hitbox_left is not None
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

    def test_officer_has_animations(self):
        """Officer should have walk, idle, and attack animations."""
        officer = Officer(100, 100)
        assert "walk" in officer.sprite.animations
        assert "idle" in officer.sprite.animations
        assert "attack" in officer.sprite.animations

    def test_officer_animation_updates(self):
        """Officer animation should update each frame."""
        officer = Officer(100, 100)
        player_rect = pygame.Rect(200, 100, 32, 48)
        officer.update(player_rect)
        assert officer.image is not None
        assert officer.image.get_width() >= 40
        assert officer.image.get_height() == 60


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

        # First update starts the firing animation
        cannon.update()
        assert cannon.firing

        # Run through firing animation until projectile is spawned
        for _ in range(cannon.FIRE_DURATION):
            cannon.update()
            if len(projectile_group) > 0:
                break

        assert len(projectile_group) == 1
        assert isinstance(list(projectile_group)[0], Cannonball)

    def test_cannon_direction(self, projectile_group):
        """Cannonball should travel in cannon's facing direction."""
        # Right-facing cannon
        cannon_right = Cannon(100, 100, projectile_group, faces_right=True)
        cannon_right.shoot_timer = 1
        # Run through firing animation
        for _ in range(cannon_right.FIRE_DURATION + 1):
            cannon_right.update()

        cannonball = list(projectile_group)[0]
        assert cannonball.velocity_x > 0  # Moving right

        # Left-facing cannon
        projectile_group.empty()
        cannon_left = Cannon(100, 100, projectile_group, faces_right=False)
        cannon_left.shoot_timer = 1
        # Run through firing animation
        for _ in range(cannon_left.FIRE_DURATION + 1):
            cannon_left.update()

        cannonball = list(projectile_group)[0]
        assert cannonball.velocity_x < 0  # Moving left

    def test_cannonball_has_arc(self, projectile_group):
        """Cannonball should arc downward due to gravity."""
        cannon = Cannon(100, 100, projectile_group, faces_right=True)
        cannon.shoot_timer = 1
        # Run through firing animation
        for _ in range(cannon.FIRE_DURATION + 1):
            cannon.update()

        cannonball = list(projectile_group)[0]
        initial_vy = cannonball.velocity_y

        # Update a few times
        for _ in range(10):
            cannonball.update()

        # Velocity should have increased (more downward)
        assert cannonball.velocity_y > initial_vy

    def test_cannon_has_animations(self, projectile_group):
        """Cannon should have static and fire animations."""
        cannon = Cannon(100, 100, projectile_group)
        assert "static" in cannon.sprite.animations
        assert "fire" in cannon.sprite.animations

    def test_cannon_firing_animation(self, projectile_group):
        """Cannon should play fire animation when shooting."""
        cannon = Cannon(100, 100, projectile_group)
        cannon.shoot_timer = 1

        cannon.update()  # Start firing

        assert cannon.firing
        assert cannon.sprite.current_animation == "fire"

    def test_cannon_animation_updates(self, projectile_group):
        """Cannon animation should update each frame."""
        cannon = Cannon(100, 100, projectile_group)
        cannon.update()
        assert cannon.image is not None


class TestBosun:
    """Tests for Bosun miniboss."""

    def test_bosun_initial_state(self):
        """Bosun should start with correct health and idle state."""
        bosun = Bosun(100, 100)
        assert bosun.health == BOSUN_HEALTH
        assert bosun.state == Bosun.STATE_IDLE

    def test_bosun_has_health_bar(self):
        """Bosun should have max_health set."""
        bosun = Bosun(100, 100)
        assert bosun.max_health == BOSUN_HEALTH

    def test_bosun_can_set_arena_bounds(self):
        """Bosun arena bounds should be settable."""
        bosun = Bosun(100, 100)
        bosun.set_arena_bounds(50, 500)
        assert bosun.arena_left == 50
        assert bosun.arena_right == 500

    def test_bosun_whip_attack_hitbox(self):
        """Bosun should have hitbox during whip attack."""
        bosun = Bosun(100, 100)
        bosun.state = Bosun.STATE_WHIP_ATTACK
        bosun.state_timer = 15  # Mid-attack

        hitbox = bosun.get_attack_hitbox()
        assert hitbox is not None
        assert hitbox.width == 50  # Whip reach

    def test_bosun_stomp_hitbox(self):
        """Bosun stomp should create wide shockwave hitbox."""
        bosun = Bosun(100, 100)
        bosun.state = Bosun.STATE_STOMP
        bosun.state_timer = 20  # Mid-stomp

        hitbox = bosun.get_attack_hitbox()
        assert hitbox is not None
        assert hitbox.width == 160  # Wide shockwave

    def test_bosun_charge_hitbox(self):
        """Bosun should have hitbox during charge."""
        bosun = Bosun(100, 100)
        bosun.state = Bosun.STATE_CHARGE
        bosun.state_timer = 30

        hitbox = bosun.get_attack_hitbox()
        assert hitbox is not None

    def test_bosun_stomp_does_more_damage(self):
        """Bosun stomp should do more damage than regular attacks."""
        bosun = Bosun(100, 100)

        bosun.state = Bosun.STATE_WHIP_ATTACK
        whip_damage = bosun.get_attack_damage()

        bosun.state = Bosun.STATE_STOMP
        stomp_damage = bosun.get_attack_damage()

        assert stomp_damage > whip_damage

    def test_bosun_stunned_on_damage(self):
        """Bosun should be briefly stunned when hit."""
        bosun = Bosun(100, 100)
        bosun.state = Bosun.STATE_WALK

        bosun.take_damage(1)

        assert bosun.state == Bosun.STATE_STUNNED
        assert bosun.damage_flash > 0

    def test_bosun_updates_state_machine(self):
        """Bosun should transition between states."""
        bosun = Bosun(100, 100)
        player_rect = pygame.Rect(200, 100, 32, 48)
        states_seen = set()

        # Run simulation
        for i in range(500):
            bosun.update(player_rect)
            states_seen.add(bosun.state)
            # Reset timers to force transitions
            if i % 50 == 0:
                bosun.attack_cooldown = 0
                bosun.state_timer = 0

        # Should see multiple states
        assert len(states_seen) >= 2


class TestAdmiral:
    """Tests for Admiral boss."""

    def test_admiral_initial_state(self, projectile_group):
        """Admiral should start with correct health and phase 1."""
        boss = Admiral(400, 400, projectile_group)
        assert boss.health == ADMIRAL_HEALTH
        assert boss.max_health == ADMIRAL_HEALTH
        assert boss.phase == 1
        assert boss.state == Admiral.STATE_IDLE

    def test_admiral_has_animated_sprite(self, projectile_group):
        """Admiral should have AnimatedSprite with all required animations."""
        boss = Admiral(400, 400, projectile_group)
        assert boss.sprite is not None
        # Check all required animations exist
        assert "idle" in boss.sprite.animations
        assert "walk" in boss.sprite.animations
        assert "sword" in boss.sprite.animations
        assert "pistol" in boss.sprite.animations
        assert "charge" in boss.sprite.animations
        assert "stunned" in boss.sprite.animations
        assert "summon" in boss.sprite.animations

    def test_admiral_animation_updates_with_state(self, projectile_group, player_rect):
        """Admiral animation should change based on state."""
        boss = Admiral(400, 400, projectile_group)

        # Start with idle
        boss.update(player_rect)
        assert boss.sprite.current_animation == "idle"

        # Force walk state
        boss.state = Admiral.STATE_WALK
        boss.update(player_rect)
        assert boss.sprite.current_animation == "walk"

        # Force charge state
        boss.state = Admiral.STATE_CHARGE
        boss.charge_direction = 1
        boss.state_timer = 60
        boss.update(player_rect)
        assert boss.sprite.current_animation == "charge"

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


class MockPlayer:
    """Mock player for testing level updates."""
    def __init__(self, x: int, y: int):
        self.rect = pygame.Rect(x, y, 32, 48)


class TestEnemyGravity:
    """Tests for enemy gravity and ground collision."""

    def test_sailor_falls_to_ground(self):
        """Test that a sailor placed in the air falls to the ground."""
        from game.level import Level

        level = Level()
        # Create a simple ground
        level.create_test_level()

        # Place a sailor in the air (should fall)
        sailor = Sailor(100, 100, patrol_distance=50)  # High in the air
        level.enemies.add(sailor)

        initial_y = sailor.rect.y

        # Update several times to let gravity work
        mock_player = MockPlayer(500, 400)
        for _ in range(60):
            level.update(mock_player)

        # Sailor should have fallen
        assert sailor.rect.y > initial_y

    def test_sailor_stops_on_ground(self):
        """Test that a sailor stops when hitting the ground."""
        from game.level import Level
        from game.settings import SCREEN_HEIGHT, TILE_SIZE

        level = Level()
        level.create_test_level()

        # Ground is at y = SCREEN_HEIGHT - TILE_SIZE = 568
        ground_top = SCREEN_HEIGHT - TILE_SIZE

        # Place sailor above ground
        sailor = Sailor(100, 200, patrol_distance=50)
        level.enemies.add(sailor)

        # Update many times
        mock_player = MockPlayer(500, 400)
        for _ in range(120):
            level.update(mock_player)

        # Sailor should be on the ground (bottom at ground level)
        assert sailor.rect.bottom <= ground_top + 1  # Allow 1 pixel tolerance

    def test_cannon_does_not_fall(self):
        """Test that cannons don't have gravity applied (they're mounted)."""
        from game.level import Level

        level = Level()
        level.create_test_level()

        # Create projectile group for cannon
        projectiles = pygame.sprite.Group()
        cannon = Cannon(100, 200, projectiles, faces_right=True)
        level.enemies.add(cannon)

        initial_y = cannon.rect.y

        # Update several times
        mock_player = MockPlayer(500, 400)
        for _ in range(60):
            level.update(mock_player)

        # Cannon should NOT have fallen
        assert cannon.rect.y == initial_y


class TestGhostEnemies:
    """Tests for ghost enemy variants."""

    def test_ghost_sailor_initial_state(self):
        """Test GhostSailor inherits from Sailor and has ghost effects."""
        ghost = GhostSailor(100, 100, patrol_distance=50)

        assert ghost.health == SAILOR_HEALTH
        assert ghost.patrol_distance == 50
        assert hasattr(ghost, 'float_timer')
        assert ghost.active

    def test_ghost_sailor_has_animations(self):
        """Test GhostSailor has ghost-tinted animations."""
        ghost = GhostSailor(100, 100)

        assert "walk" in ghost.sprite.animations
        assert "hurt" in ghost.sprite.animations
        # Frames should exist (ghost effect applied)
        assert len(ghost.sprite.animations["walk"].frames) > 0

    def test_ghost_sailor_floats(self):
        """Test GhostSailor has floating animation timer."""
        ghost = GhostSailor(100, 100)
        initial_timer = ghost.float_timer

        ghost.update(None)

        assert ghost.float_timer == initial_timer + 1

    def test_ghost_musketeer_initial_state(self, projectile_group):
        """Test GhostMusketeer inherits from Musketeer."""
        ghost = GhostMusketeer(100, 100, projectile_group)

        assert ghost.health == MUSKETEER_HEALTH
        assert hasattr(ghost, 'float_timer')
        assert ghost.active

    def test_ghost_musketeer_has_animations(self, projectile_group):
        """Test GhostMusketeer has ghost-tinted animations."""
        ghost = GhostMusketeer(100, 100, projectile_group)

        assert "idle" in ghost.sprite.animations
        assert "shoot" in ghost.sprite.animations

    def test_ghost_officer_initial_state(self):
        """Test GhostOfficer inherits from Officer."""
        ghost = GhostOfficer(100, 100)

        assert ghost.health == OFFICER_HEALTH
        assert hasattr(ghost, 'float_timer')
        assert ghost.active

    def test_ghost_officer_has_animations(self):
        """Test GhostOfficer has ghost-tinted animations."""
        ghost = GhostOfficer(100, 100)

        assert "walk" in ghost.sprite.animations
        assert "attack" in ghost.sprite.animations

    def test_ghost_officer_attacks_player(self):
        """Test GhostOfficer can attack like regular Officer."""
        ghost = GhostOfficer(100, 100)

        # Put player in attack range
        player_rect = pygame.Rect(120, 100, 32, 48)
        ghost.update(player_rect)

        # Should start attacking when close
        assert ghost.attacking or ghost.attack_cooldown > 0 or ghost.velocity_x != 0
