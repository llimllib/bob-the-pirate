"""Tests for game logic."""

import pygame
import pytest

from game.enemies import Sailor
from game.game import Game, GameState


@pytest.fixture(autouse=True)
def init_pygame():
    """Initialize pygame for all tests."""
    pygame.init()
    yield
    pygame.quit()


class TestGameBossInteraction:
    """Tests for boss-related game logic."""

    def test_game_loads_boss_level(self):
        """Game should properly load boss level."""
        game = Game()
        game.new_game("levels/boss_arena.json")

        assert game.level.is_boss_level
        assert game.level.boss is not None
        assert game.state == GameState.PLAYING

    def test_boss_defeated_state(self):
        """Game should transition to BOSS_DEFEATED when boss dies."""
        game = Game()
        game.new_game("levels/boss_arena.json")

        # Kill the boss
        boss = game.level.boss
        boss.take_damage(boss.health)

        # Run update to detect death
        game.update()

        assert game.state == GameState.BOSS_DEFEATED

    def test_boss_defeat_gives_bonus_score(self):
        """Defeating boss should give bonus score."""
        game = Game()
        game.new_game("levels/boss_arena.json")

        initial_score = game.score

        # Kill the boss
        boss = game.level.boss
        boss.take_damage(boss.health)
        game.update()

        assert game.score > initial_score
        assert game.score == initial_score + 1000  # Boss bonus

    def test_boss_summon_spawns_sailors(self):
        """Boss summon should spawn sailor enemies."""
        game = Game()
        game.new_game("levels/boss_arena.json")

        initial_enemy_count = len(game.level.enemies)

        # Trigger summon
        boss = game.level.boss
        boss.summon_pending = True
        game.update()

        # Should have more enemies now
        assert len(game.level.enemies) > initial_enemy_count

        # New enemies should be sailors
        sailors = [e for e in game.level.enemies if isinstance(e, Sailor)]
        assert len(sailors) >= 2


class TestOfficerCombat:
    """Tests for Officer combat in game context."""

    def test_officer_attack_damages_player(self):
        """Officer attack should damage player."""
        game = Game()
        game.new_game("levels/level2.json")

        # Find an officer
        from game.enemies import Officer
        officers = [e for e in game.level.enemies if isinstance(e, Officer)]
        assert len(officers) > 0

        officer = officers[0]

        # Position player in attack range
        game.player.rect.x = officer.rect.x + 20
        game.player.rect.y = officer.rect.y

        # Make officer attack
        officer.attacking = True
        officer.attack_timer = 15
        officer.facing_right = False  # Face toward player

        initial_health = game.player.health
        game.player.invincible = False

        game.update()

        # Player should have taken damage or be invincible now
        assert game.player.health < initial_health or game.player.invincible


class TestGameStates:
    """Tests for game state transitions."""

    def test_menu_level_selection(self):
        """Menu should allow level selection via title screen."""
        game = Game()

        assert game.state == GameState.MENU
        assert game.title_screen.selected_level == 0
        assert len(game.title_screen.levels) >= 3

    def test_boss_defeated_returns_to_menu(self):
        """BOSS_DEFEATED state should allow return to menu via transition."""
        game = Game()
        game.state = GameState.BOSS_DEFEATED
        game.victory_screen.frame = 100  # Past the wait period

        # Simulate ENTER key
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        pygame.event.post(event)
        game.handle_events()

        # Should start transition (fade out then go to menu)
        # The actual menu state happens after transition completes
        assert game.transition.active or game.state == GameState.MENU

        # Complete the transition
        while game.transition.active:
            game.transition.update()

        assert game.state == GameState.MENU


class TestPlayerAnimationInGame:
    """Tests for player animation updates in game loop.

    These tests verify that the game loop properly updates the player's
    animation state. This was a bug where the game.update() method
    manually handled player physics but forgot to call the animation update.
    """

    def test_game_update_calls_animation_update(self):
        """Game update loop should update player animation state and image.

        This test catches a bug where game.update() manually handled player
        physics but forgot to call the animation update methods.
        """
        game = Game()
        game.new_game("levels/level1.json")

        # Force player into a known falling state
        game.player.on_ground = False
        game.player.velocity_y = 5

        # Set animation state
        game.player.sprite.play("fall")

        # Run game update
        game.update()

        # Animation state should be set correctly
        assert game.player.sprite.current_animation == "fall"

        # Image should be from the animation (32x48, not 1x1)
        assert game.player.image.get_width() == 32
        assert game.player.image.get_height() == 48

    def test_game_update_changes_animation_on_jump(self):
        """Game should switch to jump animation when player jumps."""
        game = Game()
        game.new_game("levels/level1.json")

        # Set player to jumping state (negative velocity = going up)
        game.player.velocity_y = -10
        game.player.on_ground = False

        game.update()

        # Should be jump animation (rising)
        assert game.player.sprite.current_animation == "jump"

    def test_game_update_changes_animation_on_fall(self):
        """Game should switch to fall animation when player falls."""
        game = Game()
        game.new_game("levels/level1.json")

        # Set player to falling state (positive velocity = going down)
        game.player.velocity_y = 10
        game.player.on_ground = False

        game.update()

        # Should be fall animation
        assert game.player.sprite.current_animation == "fall"

    def test_game_update_refreshes_player_image(self):
        """Game update should refresh player image from animation."""
        game = Game()
        game.new_game("levels/level1.json")

        # Run multiple updates
        for _ in range(10):
            game.update()

        # Image should have been refreshed (new surface object)
        # Note: might be same object if frame didn't change, so we check it exists
        assert game.player.image is not None
        assert game.player.image.get_size() == (32, 48)

    def test_animation_frame_advances_over_time(self):
        """Animation frame should advance over multiple game updates."""
        game = Game()
        game.new_game("levels/level1.json")

        # Track frames seen across many updates
        frames_seen = set()
        current_anims = set()

        for _ in range(60):  # One second of game time
            game.update()
            anim_name = game.player.sprite.current_animation
            current_anims.add(anim_name)
            if anim_name:
                frames_seen.add(
                    (anim_name, game.player.sprite.animations[anim_name].current_frame)
                )

        # Should have seen multiple frame states
        assert len(frames_seen) > 1, f"Only saw: {frames_seen}"
