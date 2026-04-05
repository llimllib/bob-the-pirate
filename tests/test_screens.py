"""Tests for the screens module (menus, transitions, overlays)."""

import pygame
import pytest

from game.screens import (
    GameOverScreen,
    LevelCompleteScreen,
    LevelIntroCard,
    PauseMenu,
    ScreenTransition,
    TitleScreen,
    VictoryScreen,
)


@pytest.fixture(autouse=True)
def init_pygame():
    """Initialize pygame for all tests."""
    pygame.init()
    yield
    pygame.quit()


class TestScreenTransition:
    """Tests for screen transition effects."""

    def test_transition_initial_state(self):
        """Transition should start inactive."""
        transition = ScreenTransition()
        assert not transition.active
        assert transition.is_complete

    def test_fade_out_activates_transition(self):
        """Starting fade out should activate transition."""
        transition = ScreenTransition(duration=10)
        transition.start_fade_out()

        assert transition.active
        assert not transition.fade_in
        assert transition.timer == 0

    def test_fade_in_activates_transition(self):
        """Starting fade in should activate transition."""
        transition = ScreenTransition(duration=10)
        transition.start_fade_in()

        assert transition.active
        assert transition.fade_in
        assert transition.timer == 0

    def test_transition_completes_after_duration(self):
        """Transition should complete after duration frames."""
        transition = ScreenTransition(duration=5)
        transition.start_fade_out()

        for _ in range(5):
            assert transition.active
            transition.update()

        assert not transition.active
        assert transition.is_complete

    def test_transition_calls_callback_on_complete(self):
        """Transition should call callback when fade out completes."""
        transition = ScreenTransition(duration=3)
        callback_called = [False]

        def callback():
            callback_called[0] = True

        transition.start_fade_out(callback)

        for _ in range(3):
            transition.update()

        assert callback_called[0]

    def test_draw_does_not_crash(self):
        """Draw should not crash when active or inactive."""
        transition = ScreenTransition(duration=10)
        surface = pygame.Surface((800, 600))

        # Inactive
        transition.draw(surface)

        # Active fade out
        transition.start_fade_out()
        transition.draw(surface)

        # Active fade in
        transition.start_fade_in()
        transition.draw(surface)


class TestLevelIntroCard:
    """Tests for level intro card display."""

    def test_intro_initial_state(self):
        """Intro card should start inactive."""
        intro = LevelIntroCard()
        assert not intro.active

    def test_start_activates_intro(self):
        """Starting intro should set it active with level info."""
        intro = LevelIntroCard()
        intro.start("Port Town", "Tutorial Level")

        assert intro.active
        assert intro.level_name == "Port Town"
        assert intro.level_subtitle == "Tutorial Level"
        assert intro.timer == 0

    def test_update_advances_timer(self):
        """Update should advance the timer."""
        intro = LevelIntroCard()
        intro.start("Test")

        intro.update()
        assert intro.timer == 1

        intro.update()
        assert intro.timer == 2

    def test_intro_completes_after_duration(self):
        """Intro should complete after duration."""
        intro = LevelIntroCard()
        intro.start("Test")

        # Run for full duration
        for _ in range(intro.duration):
            result = intro.update()

        assert not result
        assert not intro.active

    def test_draw_does_not_crash(self):
        """Draw should not crash when active or inactive."""
        intro = LevelIntroCard()
        surface = pygame.Surface((800, 600))

        # Inactive
        intro.draw(surface)

        # Active
        intro.start("Test Level", "Subtitle")
        intro.draw(surface)


class TestTitleScreen:
    """Tests for the title screen."""

    def test_title_screen_has_levels(self):
        """Title screen should have available levels."""
        title = TitleScreen()
        assert len(title.levels) >= 6  # All levels

    def test_level_selection_starts_at_zero(self):
        """Selected level should start at 0."""
        title = TitleScreen()
        assert title.selected_level == 0

    def test_up_key_changes_selection(self):
        """UP key should change selection."""
        title = TitleScreen()
        title.selected_level = 2

        result = title.handle_input(pygame.K_UP)

        assert result is None  # No level selected yet
        assert title.selected_level == 1

    def test_down_key_changes_selection(self):
        """DOWN key should change selection."""
        title = TitleScreen()

        result = title.handle_input(pygame.K_DOWN)

        assert result is None
        assert title.selected_level == 1

    def test_selection_wraps_around(self):
        """Selection should wrap from top to bottom (including Skins option)."""
        title = TitleScreen()
        title.selected_level = 0

        title.handle_input(pygame.K_UP)

        # Now wraps to include the Skins option at the end
        assert title.selected_level == len(title.levels)  # Skins is after all levels

    def test_enter_returns_level_info(self):
        """ENTER should return selected level file and music."""
        title = TitleScreen()
        title.selected_level = 0

        result = title.handle_input(pygame.K_RETURN)

        assert result is not None
        assert result[0] == "levels/level1.json"
        assert result[1] == "level1.ogg"

    def test_update_advances_animation(self):
        """Update should advance animation frame."""
        title = TitleScreen()
        initial_frame = title.frame

        title.update()

        assert title.frame == initial_frame + 1

    def test_draw_does_not_crash(self):
        """Draw should not crash."""
        title = TitleScreen()
        surface = pygame.Surface((800, 600))

        title.draw(surface)


class TestPauseMenu:
    """Tests for pause menu."""

    def test_pause_menu_options(self):
        """Pause menu should have resume and quit options."""
        pause = PauseMenu()
        assert "Resume" in pause.options
        assert "Quit to Menu" in pause.options

    def test_escape_returns_resume(self):
        """ESC key should resume game."""
        pause = PauseMenu()
        result = pause.handle_input(pygame.K_ESCAPE)
        assert result == "resume"

    def test_enter_on_resume_returns_resume(self):
        """ENTER on Resume should return 'resume'."""
        pause = PauseMenu()
        pause.selected = 0  # Resume

        result = pause.handle_input(pygame.K_RETURN)
        assert result == "resume"

    def test_enter_on_quit_returns_quit(self):
        """ENTER on Quit should return 'quit'."""
        pause = PauseMenu()
        pause.selected = 2  # Quit (now at index 2 after adding Skins)

        result = pause.handle_input(pygame.K_RETURN)
        assert result == "quit"

    def test_enter_on_skins_returns_skins(self):
        """ENTER on Skins should return 'skins'."""
        pause = PauseMenu()
        pause.selected = 1  # Skins

        result = pause.handle_input(pygame.K_RETURN)
        assert result == "skins"

    def test_reset_resets_selection(self):
        """Reset should return selection to 0."""
        pause = PauseMenu()
        pause.selected = 1

        pause.reset()

        assert pause.selected == 0

    def test_draw_does_not_crash(self):
        """Draw should not crash."""
        pause = PauseMenu()
        surface = pygame.Surface((800, 600))

        pause.draw(surface)


class TestGameOverScreen:
    """Tests for game over screen."""

    def test_game_over_options(self):
        """Game over should have retry and quit options."""
        screen = GameOverScreen()
        assert "Retry Level" in screen.options
        assert "Quit to Menu" in screen.options

    def test_set_score(self):
        """Should be able to set score to display."""
        screen = GameOverScreen()
        screen.set_score(1500)

        assert screen.score == 1500

    def test_enter_on_retry_returns_retry(self):
        """ENTER on Retry should return 'retry'."""
        screen = GameOverScreen()
        screen.selected = 0

        result = screen.handle_input(pygame.K_RETURN)
        assert result == "retry"

    def test_escape_returns_quit(self):
        """ESC should return 'quit'."""
        screen = GameOverScreen()
        result = screen.handle_input(pygame.K_ESCAPE)
        assert result == "quit"

    def test_update_advances_animation(self):
        """Update should advance animation frame."""
        screen = GameOverScreen()
        screen.update()
        assert screen.frame == 1

    def test_draw_does_not_crash(self):
        """Draw should not crash."""
        screen = GameOverScreen()
        surface = pygame.Surface((800, 600))

        screen.draw(surface)


class TestLevelCompleteScreen:
    """Tests for level complete screen."""

    def test_set_stats(self):
        """Should be able to set completion stats."""
        screen = LevelCompleteScreen()
        screen.set_stats(500, 3, 3)

        assert screen.score == 500
        assert screen.treasures_collected == 3
        assert screen.treasures_total == 3

    def test_enter_returns_continue(self):
        """ENTER should return 'continue'."""
        screen = LevelCompleteScreen()
        result = screen.handle_input(pygame.K_RETURN)
        assert result == "continue"

    def test_space_returns_continue(self):
        """SPACE should also return 'continue'."""
        screen = LevelCompleteScreen()
        result = screen.handle_input(pygame.K_SPACE)
        assert result == "continue"

    def test_escape_returns_quit(self):
        """ESC should return 'quit'."""
        screen = LevelCompleteScreen()
        result = screen.handle_input(pygame.K_ESCAPE)
        assert result == "quit"

    def test_draw_does_not_crash(self):
        """Draw should not crash."""
        screen = LevelCompleteScreen()
        surface = pygame.Surface((800, 600))

        screen.draw(surface)


class TestVictoryScreen:
    """Tests for boss victory screen."""

    def test_set_score(self):
        """Should be able to set final score."""
        screen = VictoryScreen()
        screen.set_score(5000)

        assert screen.score == 5000

    def test_enter_returns_continue(self):
        """ENTER should return 'continue'."""
        screen = VictoryScreen()
        result = screen.handle_input(pygame.K_RETURN)
        assert result == "continue"

    def test_update_advances_animation(self):
        """Update should advance animation frame."""
        screen = VictoryScreen()
        screen.update()
        assert screen.frame == 1

    def test_draw_does_not_crash(self):
        """Draw should not crash."""
        screen = VictoryScreen()
        surface = pygame.Surface((800, 600))

        screen.draw(surface)

    def test_score_counting_animation(self):
        """Score should animate counting up."""
        screen = VictoryScreen()
        screen.set_score(1000)

        # At frame 0, displayed should be 0
        assert screen.frame == 0

        # After updates, displayed score should increase
        for _ in range(10):
            screen.update()

        # Frame * 20 = displayed score (capped at actual score)
        # At frame 10, displayed = min(1000, 200) = 200
        assert screen.frame == 10
