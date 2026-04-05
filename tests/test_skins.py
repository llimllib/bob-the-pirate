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
