"""Tests for the skins system."""

import pygame
import pytest


@pytest.fixture(autouse=True)
def init_pygame():
    """Initialize pygame for tests."""
    pygame.init()
    pygame.display.set_mode((800, 600), pygame.HIDDEN)
    yield
    pygame.quit()


class TestSkinsRegistry:
    """Tests for the skins registry and state management."""

    def test_skins_has_default(self):
        """Default skin should always be available."""
        from game.skins import SKINS

        assert "default" in SKINS
        assert SKINS["default"]["name"] == "Captain Bob"

    def test_skins_has_all_expected_skins(self):
        """All planned skins should be defined."""
        from game.skins import SKINS

        expected = ["default", "sailor", "ghost", "skeleton", "blackbeard", "noble", "admiral"]
        for skin_id in expected:
            assert skin_id in SKINS

    def test_skin_info_has_required_fields(self):
        """Each skin should have name, sprite, and description."""
        from game.skins import SKINS

        for skin_id, info in SKINS.items():
            assert "name" in info, f"{skin_id} missing name"
            assert "sprite" in info, f"{skin_id} missing sprite"
            assert "description" in info, f"{skin_id} missing description"

    def test_default_always_unlocked(self):
        """Default skin should always be unlocked."""
        from game.skins import is_skin_unlocked, reset_skin_progress

        reset_skin_progress()
        assert is_skin_unlocked("default")

    def test_unlock_skin(self):
        """Unlocking a skin should mark it as unlocked."""
        from game.skins import is_skin_unlocked, reset_skin_progress, unlock_skin

        reset_skin_progress()
        assert not is_skin_unlocked("ghost")

        result = unlock_skin("ghost")

        assert result is True
        assert is_skin_unlocked("ghost")

    def test_unlock_skin_returns_false_if_already_unlocked(self):
        """Unlocking an already unlocked skin returns False."""
        from game.skins import reset_skin_progress, unlock_skin

        reset_skin_progress()
        unlock_skin("ghost")

        result = unlock_skin("ghost")

        assert result is False

    def test_unlock_invalid_skin_returns_false(self):
        """Unlocking a non-existent skin returns False."""
        from game.skins import reset_skin_progress, unlock_skin

        reset_skin_progress()

        result = unlock_skin("nonexistent_skin")

        assert result is False

    def test_get_unlocked_skins(self):
        """get_unlocked_skins should return all unlocked skins."""
        from game.skins import get_unlocked_skins, reset_skin_progress, unlock_skin

        reset_skin_progress()
        unlock_skin("ghost")
        unlock_skin("skeleton")

        unlocked = get_unlocked_skins()

        assert "default" in unlocked
        assert "ghost" in unlocked
        assert "skeleton" in unlocked
        assert len(unlocked) == 3

    def test_set_selected_skin(self):
        """Setting selected skin should change current selection."""
        from game.skins import (
            get_selected_skin,
            reset_skin_progress,
            set_selected_skin,
            unlock_skin,
        )

        reset_skin_progress()
        unlock_skin("ghost")

        result = set_selected_skin("ghost")

        assert result is True
        assert get_selected_skin() == "ghost"

    def test_cannot_select_locked_skin(self):
        """Cannot select a skin that isn't unlocked."""
        from game.skins import (
            get_selected_skin,
            reset_skin_progress,
            set_selected_skin,
        )

        reset_skin_progress()

        result = set_selected_skin("ghost")

        assert result is False
        assert get_selected_skin() == "default"

    def test_cannot_select_invalid_skin(self):
        """Cannot select a non-existent skin."""
        from game.skins import reset_skin_progress, set_selected_skin

        reset_skin_progress()

        result = set_selected_skin("nonexistent")

        assert result is False

    def test_get_selected_skin_sprite(self):
        """get_selected_skin_sprite returns the sprite filename."""
        from game.skins import (
            get_selected_skin_sprite,
            reset_skin_progress,
            set_selected_skin,
            unlock_skin,
        )

        reset_skin_progress()
        unlock_skin("ghost")
        set_selected_skin("ghost")

        sprite = get_selected_skin_sprite()

        assert sprite == "ghost_captain.png"


class TestSkinPickup:
    """Tests for the SkinPickup collectible."""

    def test_skin_pickup_creates(self):
        """SkinPickup should create successfully."""
        from game.collectibles import SkinPickup

        pickup = SkinPickup(100, 200, "ghost", "visible")

        assert pickup.rect.x == 100
        assert pickup.rect.y == 200
        assert pickup.skin_id == "ghost"
        assert pickup.hidden_type == "visible"

    def test_skin_pickup_collect_returns_skin_info(self):
        """Collecting should return skin info."""
        from game.collectibles import SkinPickup
        from game.player import Player

        pickup = SkinPickup(100, 200, "ghost", "visible")
        player = Player(0, 0)

        result = pickup.collect(player)

        assert result["type"] == "skin"
        assert result["skin_id"] == "ghost"

    def test_skin_pickup_hidden_type_hidden(self):
        """Hidden pickups should not draw anything."""
        from game.collectibles import SkinPickup

        pickup = SkinPickup(100, 200, "ghost", "hidden")
        surface = pygame.Surface((800, 600))

        # Should not crash and should not draw (but hard to test visually)
        pickup.draw(surface, (0, 0))

    def test_skin_pickup_shimmer_type(self):
        """Shimmer pickups should draw with alpha."""
        from game.collectibles import SkinPickup

        pickup = SkinPickup(100, 200, "ghost", "shimmer")
        surface = pygame.Surface((800, 600))

        # Should not crash
        pickup.draw(surface, (0, 0))
        pickup.update()
        pickup.draw(surface, (0, 0))


class TestSkinsMenu:
    """Tests for the SkinsMenu screen."""

    def test_skins_menu_opens(self):
        """SkinsMenu should open properly."""
        from game.screens import SkinsMenu

        menu = SkinsMenu()
        menu.open()

        assert menu.active is True

    def test_skins_menu_closes(self):
        """SkinsMenu should close properly."""
        from game.screens import SkinsMenu

        menu = SkinsMenu()
        menu.open()
        menu.close()

        assert menu.active is False

    def test_skins_menu_escape_returns_back(self):
        """ESC should return 'back'."""
        from game.screens import SkinsMenu

        menu = SkinsMenu()
        menu.open()

        result = menu.handle_input(pygame.K_ESCAPE)

        assert result == "back"

    def test_skins_menu_navigation(self):
        """UP/DOWN should change selection."""
        from game.screens import SkinsMenu

        menu = SkinsMenu()
        menu.open()
        initial = menu.selected

        menu.handle_input(pygame.K_DOWN)

        assert menu.selected == initial + 1

    def test_skins_menu_select_unlocked_skin(self):
        """Selecting an unlocked skin returns 'changed'."""
        from game.screens import SkinsMenu
        from game.skins import reset_skin_progress

        reset_skin_progress()
        menu = SkinsMenu()
        menu.open()
        menu.selected = 0  # Default skin

        result = menu.handle_input(pygame.K_RETURN)

        assert result == "changed"

    def test_skins_menu_cannot_select_locked_skin(self):
        """Selecting a locked skin returns None."""
        from game.screens import SkinsMenu
        from game.skins import SKINS, reset_skin_progress

        reset_skin_progress()
        menu = SkinsMenu()
        menu.open()
        # Find a locked skin
        skin_ids = list(SKINS.keys())
        menu.selected = skin_ids.index("ghost")  # Ghost is locked initially

        result = menu.handle_input(pygame.K_RETURN)

        assert result is None

    def test_skins_menu_draw_does_not_crash(self):
        """Drawing should not crash."""
        from game.screens import SkinsMenu

        menu = SkinsMenu()
        menu.open()
        surface = pygame.Surface((800, 600))

        menu.draw(surface)


class TestSkinNotification:
    """Tests for the SkinNotification UI."""

    def test_notification_initially_inactive(self):
        """Notification should start inactive."""
        from game.ui import SkinNotification

        notif = SkinNotification()

        assert notif.active is False

    def test_notification_show_activates(self):
        """Showing a notification should activate it."""
        from game.ui import SkinNotification

        notif = SkinNotification()
        notif.show("Ghost Captain")

        assert notif.active is True
        assert notif.skin_name == "Ghost Captain"

    def test_notification_update_advances_timer(self):
        """Update should advance the timer."""
        from game.ui import SkinNotification

        notif = SkinNotification()
        notif.show("Ghost Captain")
        initial_timer = notif.timer

        notif.update()

        assert notif.timer == initial_timer + 1

    def test_notification_expires(self):
        """Notification should expire after duration."""
        from game.ui import SkinNotification

        notif = SkinNotification()
        notif.show("Ghost Captain")

        # Run through duration
        for _ in range(notif.duration):
            notif.update()

        assert notif.active is False

    def test_notification_draw_does_not_crash(self):
        """Drawing should not crash."""
        from game.ui import SkinNotification

        notif = SkinNotification()
        notif.show("Ghost Captain")
        surface = pygame.Surface((800, 600))

        notif.draw(surface)


class TestAdmiralBobEffect:
    """Tests for Admiral Bob skin special effect."""

    def test_is_admiral_bob_active_when_selected(self):
        """is_admiral_bob_active returns True when admiral skin is selected."""
        from game.skins import (
            is_admiral_bob_active,
            reset_skin_progress,
            set_selected_skin,
            unlock_skin,
        )

        reset_skin_progress()
        unlock_skin("admiral")
        set_selected_skin("admiral")

        assert is_admiral_bob_active() is True

    def test_is_admiral_bob_active_when_not_selected(self):
        """is_admiral_bob_active returns False when different skin is selected."""
        from game.skins import is_admiral_bob_active, reset_skin_progress

        reset_skin_progress()
        # Default skin is selected

        assert is_admiral_bob_active() is False

    def test_admiral_bob_removes_first_enemy_of_each_type(self):
        """Admiral Bob effect removes first instance of each regular enemy type."""
        from game.level import Level
        from game.skins import reset_skin_progress, set_selected_skin, unlock_skin

        reset_skin_progress()
        unlock_skin("admiral")
        set_selected_skin("admiral")

        # Load level 1 which has multiple sailors
        level = Level()
        level.load_from_file("levels/level1.json")
        admiral_bob_enemy_count = len(level.enemies)

        # The key test: when we reload without Admiral Bob, we should have more enemies
        reset_skin_progress()  # Back to default skin

        level2 = Level()
        level2.load_from_file("levels/level1.json")

        # Should have more enemies without Admiral Bob
        assert len(level2.enemies) > admiral_bob_enemy_count

    def test_admiral_bob_does_not_remove_bosun(self):
        """Admiral Bob effect should not remove the Bosun."""
        from game.enemies import Bosun
        from game.level import Level
        from game.skins import reset_skin_progress, set_selected_skin, unlock_skin

        reset_skin_progress()
        unlock_skin("admiral")
        set_selected_skin("admiral")

        # Load level 4 which has the Bosun
        level = Level()
        level.load_from_file("levels/level4.json")

        # Count Bosuns
        bosun_count = sum(1 for e in level.enemies if isinstance(e, Bosun))

        # Bosun should still be present
        assert bosun_count >= 1

    def test_admiral_bob_does_not_remove_admiral_boss(self):
        """Admiral Bob effect should not remove the Admiral boss."""
        from game.enemies import Admiral
        from game.level import Level
        from game.skins import reset_skin_progress, set_selected_skin, unlock_skin

        reset_skin_progress()
        unlock_skin("admiral")
        set_selected_skin("admiral")

        # Load boss_arena which has the Admiral boss
        level = Level()
        level.load_from_file("levels/boss_arena.json")

        # Count Admirals
        admiral_count = sum(1 for e in level.enemies if isinstance(e, Admiral))

        # Admiral should still be present
        assert admiral_count >= 1
        assert level.boss is not None

    def test_admiral_bob_does_not_remove_ghost_captain(self):
        """Admiral Bob effect should not remove the Ghost Captain boss."""
        from game.enemies import GhostCaptain
        from game.level import Level
        from game.skins import reset_skin_progress, set_selected_skin, unlock_skin

        reset_skin_progress()
        unlock_skin("admiral")
        set_selected_skin("admiral")

        # Load secret_crypt which has the Ghost Captain boss
        level = Level()
        level.load_from_file("levels/secret_crypt.json")

        # Count Ghost Captains
        ghost_captain_count = sum(1 for e in level.enemies if isinstance(e, GhostCaptain))

        # Ghost Captain should still be present
        assert ghost_captain_count >= 1
        assert level.boss is not None

    def test_admiral_bob_effect_does_not_persist_across_reloads(self):
        """Enemies should reappear when level is reloaded with different skin."""
        from game.level import Level
        from game.skins import reset_skin_progress, set_selected_skin, unlock_skin

        # First, load with Admiral Bob
        reset_skin_progress()
        unlock_skin("admiral")
        set_selected_skin("admiral")

        level1 = Level()
        level1.load_from_file("levels/level1.json")
        admiral_bob_enemy_count = len(level1.enemies)

        # Now switch to skeleton skin and reload
        unlock_skin("skeleton")
        set_selected_skin("skeleton")

        level2 = Level()
        level2.load_from_file("levels/level1.json")
        skeleton_enemy_count = len(level2.enemies)

        # Enemies should be back (more enemies without Admiral Bob)
        assert skeleton_enemy_count > admiral_bob_enemy_count

        # Reload with Admiral Bob again should remove enemies again
        set_selected_skin("admiral")

        level3 = Level()
        level3.load_from_file("levels/level1.json")

        assert len(level3.enemies) == admiral_bob_enemy_count

    def test_admiral_bob_removes_first_of_each_type_separately(self):
        """Admiral Bob should remove first sailor AND first musketeer separately."""
        from game.level import Level
        from game.skins import reset_skin_progress, set_selected_skin, unlock_skin

        # Load without Admiral Bob to get baseline
        reset_skin_progress()

        level_normal = Level()
        level_normal.load_from_file("levels/level2.json")  # Level 2 has multiple enemy types

        # Count by type
        normal_counts: dict[str, int] = {}
        for e in level_normal.enemies:
            name = e.__class__.__name__
            normal_counts[name] = normal_counts.get(name, 0) + 1

        # Now load with Admiral Bob
        unlock_skin("admiral")
        set_selected_skin("admiral")

        level_admiral = Level()
        level_admiral.load_from_file("levels/level2.json")

        # Count by type
        admiral_counts: dict[str, int] = {}
        for e in level_admiral.enemies:
            name = e.__class__.__name__
            admiral_counts[name] = admiral_counts.get(name, 0) + 1

        # Each regular enemy type should have 1 fewer (or 0 if there was only 1)
        # Boss types (Bosun, Admiral, GhostCaptain) should be unchanged
        boss_types = {"Bosun", "Admiral", "GhostCaptain"}
        for enemy_type, normal_count in normal_counts.items():
            if enemy_type in boss_types:
                # Boss types should be unchanged
                assert admiral_counts.get(enemy_type, 0) == normal_count, \
                    f"{enemy_type} count should be unchanged"
            else:
                # Regular types should have 1 fewer
                expected = max(0, normal_count - 1)
                assert admiral_counts.get(enemy_type, 0) == expected, \
                    f"{enemy_type}: expected {expected}, got {admiral_counts.get(enemy_type, 0)}"


class TestPlayerSkinLoading:
    """Tests for player skin loading."""

    def test_player_loads_default_skin(self):
        """Player should load default skin initially."""
        from game.player import Player
        from game.skins import reset_skin_progress

        reset_skin_progress()
        player = Player(0, 0)

        # Player should have loaded animations
        assert player.sprite is not None
        assert "idle" in player.sprite.animations

    def test_player_reload_skin(self):
        """Player should be able to reload with different skin."""
        from game.player import Player
        from game.skins import reset_skin_progress, set_selected_skin, unlock_skin

        reset_skin_progress()
        player = Player(0, 0)

        # Unlock and select a different skin
        unlock_skin("ghost")
        set_selected_skin("ghost")

        # Reload should not crash
        player.reload_skin()

        assert player.sprite is not None

    def test_sailor_bob_skin_loads(self):
        """Sailor Bob skin should load without errors."""
        from game.player import Player
        from game.skins import reset_skin_progress, set_selected_skin, unlock_skin

        reset_skin_progress()
        unlock_skin("sailor")
        set_selected_skin("sailor")

        player = Player(0, 0)

        assert player.sprite is not None
        assert "idle" in player.sprite.animations
        assert "run" in player.sprite.animations
        assert "attack" in player.sprite.animations


class TestGhostCaptainSkin:
    """Tests for Ghost Captain skin special behavior."""

    def test_is_ghost_captain_active_when_selected(self):
        """is_ghost_captain_active should return True when ghost skin selected."""
        from game.skins import (
            is_ghost_captain_active,
            reset_skin_progress,
            set_selected_skin,
            unlock_skin,
        )

        reset_skin_progress()
        unlock_skin("ghost")
        set_selected_skin("ghost")

        assert is_ghost_captain_active()

    def test_is_ghost_captain_active_when_not_selected(self):
        """is_ghost_captain_active should return False for other skins."""
        from game.skins import (
            is_ghost_captain_active,
            reset_skin_progress,
            set_selected_skin,
        )

        reset_skin_progress()
        set_selected_skin("default")

        assert not is_ghost_captain_active()

    def test_ghost_captain_has_bonus_health(self):
        """Ghost Captain skin should give +2 max health."""
        from game.player import Player
        from game.settings import GHOST_SKIN_HEALTH_BONUS, PLAYER_MAX_HEALTH
        from game.skins import reset_skin_progress, set_selected_skin, unlock_skin

        # Normal player
        reset_skin_progress()
        normal_player = Player(0, 0)
        assert normal_player.max_health == PLAYER_MAX_HEALTH

        # Ghost Captain player
        unlock_skin("ghost")
        set_selected_skin("ghost")
        ghost_player = Player(0, 0)

        assert ghost_player.max_health == PLAYER_MAX_HEALTH + GHOST_SKIN_HEALTH_BONUS
        assert ghost_player.health == ghost_player.max_health

    def test_ghost_captain_is_ghost_flag_set(self):
        """Ghost Captain player should have is_ghost_captain flag True."""
        from game.player import Player
        from game.skins import reset_skin_progress, set_selected_skin, unlock_skin

        reset_skin_progress()
        unlock_skin("ghost")
        set_selected_skin("ghost")

        player = Player(0, 0)
        assert player.is_ghost_captain

    def test_normal_player_is_ghost_flag_false(self):
        """Normal player should have is_ghost_captain flag False."""
        from game.player import Player
        from game.skins import reset_skin_progress

        reset_skin_progress()
        player = Player(0, 0)
        assert not player.is_ghost_captain

    def test_ghost_captain_has_longer_attack_duration(self):
        """Ghost Captain should have 2-second flame attack duration."""
        from game.player import Player
        from game.settings import GHOST_SKIN_ATTACK_DURATION
        from game.skins import reset_skin_progress, set_selected_skin, unlock_skin

        reset_skin_progress()
        unlock_skin("ghost")
        set_selected_skin("ghost")

        player = Player(0, 0)
        player.attack()

        # Ghost Captain has 2-second (120 frame) flame attack
        assert player.attack_timer == GHOST_SKIN_ATTACK_DURATION

    def test_normal_player_attack_duration(self):
        """Normal player should have standard attack duration."""
        from game.player import Player
        from game.settings import ATTACK_DURATION
        from game.skins import reset_skin_progress

        reset_skin_progress()
        player = Player(0, 0)
        player.attack()

        assert player.attack_timer == ATTACK_DURATION

    def test_ghost_captain_has_trail_particles(self):
        """Ghost Captain should have trail_particles list."""
        from game.player import Player
        from game.skins import reset_skin_progress, set_selected_skin, unlock_skin

        reset_skin_progress()
        unlock_skin("ghost")
        set_selected_skin("ghost")

        player = Player(0, 0)
        assert hasattr(player, "trail_particles")
        assert isinstance(player.trail_particles, list)

    def test_ghost_captain_generates_particles_when_moving(self):
        """Ghost Captain should generate trail particles when moving."""
        from game.player import Player
        from game.skins import reset_skin_progress, set_selected_skin, unlock_skin

        reset_skin_progress()
        unlock_skin("ghost")
        set_selected_skin("ghost")

        player = Player(0, 0)
        player.velocity_x = 5  # Moving

        # Update a few frames
        for _ in range(10):
            player.update()

        # Should have generated particles
        assert len(player.trail_particles) > 0

    def test_ghost_captain_no_particles_when_standing(self):
        """Ghost Captain should not generate particles when standing on ground."""
        from game.player import Player
        from game.skins import reset_skin_progress, set_selected_skin, unlock_skin

        reset_skin_progress()
        unlock_skin("ghost")
        set_selected_skin("ghost")

        player = Player(0, 0)
        player.velocity_x = 0
        player.on_ground = True  # Simulating standing on ground

        # Clear any existing particles
        player.trail_particles = []

        # Update a single frame with no movement and on_ground
        # When on_ground, velocity_y should stay 0 (or be reset by collision)
        player.velocity_y = 0
        player._update_ghost_trail()

        # Should have no particles since not moving
        assert len(player.trail_particles) == 0

    def test_ghost_captain_reload_skin_updates_flag(self):
        """Reloading skin should update is_ghost_captain flag."""
        from game.player import Player
        from game.skins import reset_skin_progress, set_selected_skin, unlock_skin

        # Start as normal
        reset_skin_progress()
        player = Player(0, 0)
        assert not player.is_ghost_captain

        # Switch to ghost
        unlock_skin("ghost")
        set_selected_skin("ghost")
        player.reload_skin()

        assert player.is_ghost_captain

    def test_ghost_captain_reload_updates_max_health(self):
        """Reloading skin should update max health for ghost captain."""
        from game.player import Player
        from game.settings import GHOST_SKIN_HEALTH_BONUS, PLAYER_MAX_HEALTH
        from game.skins import reset_skin_progress, set_selected_skin, unlock_skin

        # Start as normal
        reset_skin_progress()
        player = Player(0, 0)
        assert player.max_health == PLAYER_MAX_HEALTH

        # Switch to ghost
        unlock_skin("ghost")
        set_selected_skin("ghost")
        player.reload_skin()

        assert player.max_health == PLAYER_MAX_HEALTH + GHOST_SKIN_HEALTH_BONUS

    def test_ghost_captain_draw_does_not_crash(self):
        """Ghost Captain draw with particles should not crash."""
        from game.player import Player
        from game.skins import reset_skin_progress, set_selected_skin, unlock_skin

        reset_skin_progress()
        unlock_skin("ghost")
        set_selected_skin("ghost")

        player = Player(100, 100)
        player.velocity_x = 5  # Generate particles

        for _ in range(5):
            player.update()

        # Draw should not crash
        surface = pygame.Surface((800, 600))
        player.draw(surface, (0, 0))

    def test_ghost_captain_has_larger_attack_hitbox(self):
        """Ghost Captain should have larger flame attack hitbox."""
        from game.player import Player
        from game.settings import (
            ATTACK_RANGE,
            GHOST_SKIN_ATTACK_HEIGHT,
            GHOST_SKIN_ATTACK_RANGE,
            PLAYER_HEIGHT,
        )
        from game.skins import reset_skin_progress, set_selected_skin, unlock_skin

        # Normal player attack hitbox
        reset_skin_progress()
        normal_player = Player(100, 100)
        normal_player.attack()
        normal_hitbox = normal_player.get_attack_hitbox()

        assert normal_hitbox.width == ATTACK_RANGE
        assert normal_hitbox.height == PLAYER_HEIGHT // 2

        # Ghost Captain attack hitbox (larger flames)
        unlock_skin("ghost")
        set_selected_skin("ghost")
        ghost_player = Player(100, 100)
        ghost_player.attack()
        ghost_hitbox = ghost_player.get_attack_hitbox()

        assert ghost_hitbox.width == GHOST_SKIN_ATTACK_RANGE
        assert ghost_hitbox.height == GHOST_SKIN_ATTACK_HEIGHT
        assert ghost_hitbox.width > normal_hitbox.width
        assert ghost_hitbox.height > normal_hitbox.height

    def test_ghost_captain_flame_resets_hits_on_frame_change(self):
        """Ghost Captain flame attack should reset hit tracking when animation frame changes."""
        from game.player import Player
        from game.skins import reset_skin_progress, set_selected_skin, unlock_skin

        reset_skin_progress()
        unlock_skin("ghost")
        set_selected_skin("ghost")

        player = Player(100, 100)
        player.attack()

        # Simulate hitting an enemy
        player.enemies_hit_this_attack.add(12345)
        assert 12345 in player.enemies_hit_this_attack

        initial_frame = player.sprite.get_current_frame_index()

        # Update until animation frame changes (20 frames per animation frame)
        for _ in range(25):
            player.update()
            if player.sprite.get_current_frame_index() != initial_frame:
                break

        # Hit tracking should have been cleared when frame changed
        assert 12345 not in player.enemies_hit_this_attack

    def test_ghost_captain_flame_animation_loops(self):
        """Ghost Captain flame attack animation should loop during the 2-second attack."""
        from game.player import Player
        from game.skins import reset_skin_progress, set_selected_skin, unlock_skin

        reset_skin_progress()
        unlock_skin("ghost")
        set_selected_skin("ghost")

        player = Player(100, 100)
        player.attack()

        # Track how many times we see frame 0
        frame_0_count = 0
        last_frame = -1

        # Run for 120 frames (2 seconds)
        for _ in range(120):
            player.update()
            current_frame = player.sprite.get_current_frame_index()
            if current_frame == 0 and last_frame != 0:
                frame_0_count += 1
            last_frame = current_frame

        # Should have looped multiple times (at 20 frames per anim frame, ~2 loops)
        assert frame_0_count >= 2


class TestSkeletonPirateSkin:
    """Tests for Skeleton Pirate skin special behavior."""

    def test_is_skeleton_pirate_active_when_selected(self):
        """is_skeleton_pirate_active should return True when skeleton skin selected."""
        from game.skins import (
            is_skeleton_pirate_active,
            reset_skin_progress,
            set_selected_skin,
            unlock_skin,
        )

        reset_skin_progress()
        unlock_skin("skeleton")
        set_selected_skin("skeleton")

        assert is_skeleton_pirate_active()

    def test_is_skeleton_pirate_active_when_not_selected(self):
        """is_skeleton_pirate_active should return False for other skins."""
        from game.skins import (
            is_skeleton_pirate_active,
            reset_skin_progress,
            set_selected_skin,
        )

        reset_skin_progress()
        set_selected_skin("default")

        assert not is_skeleton_pirate_active()

    def test_skeleton_pirate_has_reduced_health(self):
        """Skeleton Pirate skin should give -2 max health (3 total)."""
        from game.player import Player
        from game.settings import PLAYER_MAX_HEALTH, SKELETON_SKIN_HEALTH_PENALTY
        from game.skins import reset_skin_progress, set_selected_skin, unlock_skin

        # Normal player
        reset_skin_progress()
        normal_player = Player(0, 0)
        assert normal_player.max_health == PLAYER_MAX_HEALTH

        # Skeleton Pirate player
        unlock_skin("skeleton")
        set_selected_skin("skeleton")
        skeleton_player = Player(0, 0)

        assert skeleton_player.max_health == PLAYER_MAX_HEALTH - SKELETON_SKIN_HEALTH_PENALTY
        assert skeleton_player.health == skeleton_player.max_health

    def test_skeleton_pirate_is_skeleton_flag_set(self):
        """Skeleton Pirate player should have is_skeleton_pirate flag True."""
        from game.player import Player
        from game.skins import reset_skin_progress, set_selected_skin, unlock_skin

        reset_skin_progress()
        unlock_skin("skeleton")
        set_selected_skin("skeleton")

        player = Player(0, 0)
        assert player.is_skeleton_pirate

    def test_normal_player_is_skeleton_flag_false(self):
        """Normal player should have is_skeleton_pirate flag False."""
        from game.player import Player
        from game.skins import reset_skin_progress

        reset_skin_progress()
        player = Player(0, 0)
        assert not player.is_skeleton_pirate

    def test_skeleton_pirate_has_higher_damage_multiplier(self):
        """Skeleton Pirate should have 2x damage multiplier."""
        from game.player import Player
        from game.settings import SKELETON_SKIN_DAMAGE_MULT
        from game.skins import reset_skin_progress, set_selected_skin, unlock_skin

        # Normal player damage
        reset_skin_progress()
        normal_player = Player(0, 0)
        assert normal_player.get_total_damage_multiplier() == 1.0

        # Skeleton Pirate damage
        unlock_skin("skeleton")
        set_selected_skin("skeleton")
        skeleton_player = Player(0, 0)

        assert skeleton_player.get_total_damage_multiplier() == SKELETON_SKIN_DAMAGE_MULT

    def test_skeleton_pirate_bone_throw_every_4th_attack(self):
        """Skeleton Pirate should set pending_bone_throw on every 4th attack."""
        from game.player import Player
        from game.skins import reset_skin_progress, set_selected_skin, unlock_skin

        reset_skin_progress()
        unlock_skin("skeleton")
        set_selected_skin("skeleton")

        player = Player(0, 0)

        # Attacks 1-3 should not trigger bone
        for i in range(3):
            player.attack()
            assert not player.pending_bone_throw, f"Attack {i+1} should not trigger bone"
            # Reset for next attack
            player.attacking = False
            player.attack_cooldown = 0

        # Attack 4 should trigger bone
        player.attack()
        assert player.pending_bone_throw, "Attack 4 should trigger bone throw"

    def test_skeleton_pirate_attack_count_resets_after_bone(self):
        """Attack count should reset to 0 after bone throw."""
        from game.player import Player
        from game.skins import reset_skin_progress, set_selected_skin, unlock_skin

        reset_skin_progress()
        unlock_skin("skeleton")
        set_selected_skin("skeleton")

        player = Player(0, 0)

        # Do 4 attacks to trigger bone
        for _ in range(4):
            player.attack()
            player.attacking = False
            player.attack_cooldown = 0

        # Count should be reset
        assert player.attack_count == 0

    def test_skeleton_pirate_reload_skin_updates_flag(self):
        """Reloading skin should update is_skeleton_pirate flag."""
        from game.player import Player
        from game.skins import reset_skin_progress, set_selected_skin, unlock_skin

        # Start as normal
        reset_skin_progress()
        player = Player(0, 0)
        assert not player.is_skeleton_pirate

        # Switch to skeleton
        unlock_skin("skeleton")
        set_selected_skin("skeleton")
        player.reload_skin()

        assert player.is_skeleton_pirate

    def test_skeleton_pirate_reload_updates_max_health(self):
        """Reloading skin should update max health for skeleton pirate."""
        from game.player import Player
        from game.settings import PLAYER_MAX_HEALTH, SKELETON_SKIN_HEALTH_PENALTY
        from game.skins import reset_skin_progress, set_selected_skin, unlock_skin

        # Start as normal
        reset_skin_progress()
        player = Player(0, 0)
        assert player.max_health == PLAYER_MAX_HEALTH

        # Switch to skeleton
        unlock_skin("skeleton")
        set_selected_skin("skeleton")
        player.reload_skin()

        assert player.max_health == PLAYER_MAX_HEALTH - SKELETON_SKIN_HEALTH_PENALTY


class TestBlackbeardSkin:
    """Tests for Blackbeard skin functionality."""

    def test_is_blackbeard_active_when_selected(self):
        """is_blackbeard_active should return True when blackbeard skin selected."""
        from game.skins import (
            is_blackbeard_active,
            reset_skin_progress,
            set_selected_skin,
            unlock_skin,
        )

        reset_skin_progress()
        unlock_skin("blackbeard")
        set_selected_skin("blackbeard")

        assert is_blackbeard_active()

    def test_is_blackbeard_active_when_not_selected(self):
        """is_blackbeard_active should return False for other skins."""
        from game.skins import (
            is_blackbeard_active,
            reset_skin_progress,
            set_selected_skin,
        )

        reset_skin_progress()
        set_selected_skin("default")

        assert not is_blackbeard_active()

    def test_blackbeard_player_has_flag_set(self):
        """Player should have is_blackbeard flag when skin is active."""
        from game.player import Player
        from game.skins import reset_skin_progress, set_selected_skin, unlock_skin

        reset_skin_progress()
        unlock_skin("blackbeard")
        set_selected_skin("blackbeard")

        player = Player(0, 0)
        assert player.is_blackbeard

    def test_normal_player_is_blackbeard_flag_false(self):
        """Normal player should not have is_blackbeard flag."""
        from game.player import Player
        from game.skins import reset_skin_progress, set_selected_skin

        reset_skin_progress()
        set_selected_skin("default")

        player = Player(0, 0)
        assert not player.is_blackbeard

    def test_blackbeard_reload_skin_updates_flag(self):
        """Reloading skin should update is_blackbeard flag."""
        from game.player import Player
        from game.skins import reset_skin_progress, set_selected_skin, unlock_skin

        reset_skin_progress()
        player = Player(0, 0)
        assert not player.is_blackbeard

        # Switch to blackbeard
        unlock_skin("blackbeard")
        set_selected_skin("blackbeard")
        player.reload_skin()

        assert player.is_blackbeard


class TestNoblePirateSkin:
    """Tests for Noble Pirate skin functionality."""

    def test_is_noble_pirate_active_when_selected(self):
        """is_noble_pirate_active should return True when noble skin selected."""
        from game.skins import (
            is_noble_pirate_active,
            reset_skin_progress,
            set_selected_skin,
            unlock_skin,
        )

        reset_skin_progress()
        unlock_skin("noble")
        set_selected_skin("noble")

        assert is_noble_pirate_active()

    def test_is_noble_pirate_active_when_not_selected(self):
        """is_noble_pirate_active should return False for other skins."""
        from game.skins import (
            is_noble_pirate_active,
            reset_skin_progress,
            set_selected_skin,
        )

        reset_skin_progress()
        set_selected_skin("default")

        assert not is_noble_pirate_active()

    def test_noble_pirate_player_has_flag_set(self):
        """Player should have is_noble_pirate flag when skin is active."""
        from game.player import Player
        from game.skins import reset_skin_progress, set_selected_skin, unlock_skin

        reset_skin_progress()
        unlock_skin("noble")
        set_selected_skin("noble")

        player = Player(0, 0)
        assert player.is_noble_pirate

    def test_normal_player_is_noble_pirate_flag_false(self):
        """Normal player should not have is_noble_pirate flag."""
        from game.player import Player
        from game.skins import reset_skin_progress, set_selected_skin

        reset_skin_progress()
        set_selected_skin("default")

        player = Player(0, 0)
        assert not player.is_noble_pirate

    def test_noble_pirate_reload_skin_updates_flag(self):
        """Reloading skin should update is_noble_pirate flag."""
        from game.player import Player
        from game.skins import reset_skin_progress, set_selected_skin, unlock_skin

        reset_skin_progress()
        player = Player(0, 0)
        assert not player.is_noble_pirate

        # Switch to noble
        unlock_skin("noble")
        set_selected_skin("noble")
        player.reload_skin()

        assert player.is_noble_pirate
