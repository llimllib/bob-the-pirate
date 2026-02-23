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
        """Menu should allow level selection."""
        game = Game()

        assert game.state == GameState.MENU
        assert game.selected_level == 0
        assert len(game.available_levels) >= 3

    def test_boss_defeated_returns_to_menu(self):
        """BOSS_DEFEATED state should allow return to menu."""
        game = Game()
        game.state = GameState.BOSS_DEFEATED

        # Simulate ENTER key
        event = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RETURN)
        pygame.event.post(event)
        game.handle_events()

        assert game.state == GameState.MENU
