"""Tests for the audio system."""

import os

import pygame
import pytest


@pytest.fixture(scope="module", autouse=True)
def init_pygame():
    """Initialize pygame for all tests in this module."""
    pygame.init()
    pygame.mixer.init()
    yield
    pygame.quit()


class TestAudioManager:
    """Tests for the AudioManager class."""

    def test_audio_manager_initializes(self):
        """Test that AudioManager initializes without error."""
        from game.audio import AudioManager
        manager = AudioManager()
        assert manager is not None

    def test_audio_manager_has_default_volumes(self):
        """Test that AudioManager has sensible default volumes."""
        from game.audio import AudioManager
        manager = AudioManager()
        assert 0.0 <= manager.sfx_volume <= 1.0
        assert 0.0 <= manager.music_volume <= 1.0
        assert 0.0 <= manager.master_volume <= 1.0

    def test_audio_manager_loads_sounds(self):
        """Test that AudioManager loads sound files from assets/sounds."""
        from game.audio import AudioManager
        manager = AudioManager()
        # Should have loaded sounds if assets/sounds exists
        if os.path.exists("assets/sounds"):
            assert len(manager.sounds) > 0

    def test_play_sound_nonexistent_doesnt_crash(self):
        """Test that playing a nonexistent sound doesn't crash."""
        from game.audio import AudioManager
        manager = AudioManager()
        # Should not raise an exception
        manager.play_sound("nonexistent_sound_12345")

    def test_set_sfx_volume_clamps(self):
        """Test that volume is clamped to 0.0-1.0 range."""
        from game.audio import AudioManager
        manager = AudioManager()
        manager.set_sfx_volume(2.0)
        assert manager.sfx_volume == 1.0
        manager.set_sfx_volume(-1.0)
        assert manager.sfx_volume == 0.0

    def test_set_music_volume_clamps(self):
        """Test that music volume is clamped to 0.0-1.0 range."""
        from game.audio import AudioManager
        manager = AudioManager()
        manager.set_music_volume(1.5)
        assert manager.music_volume == 1.0
        manager.set_music_volume(-0.5)
        assert manager.music_volume == 0.0

    def test_set_master_volume_clamps(self):
        """Test that master volume is clamped to 0.0-1.0 range."""
        from game.audio import AudioManager
        manager = AudioManager()
        manager.set_master_volume(5.0)
        assert manager.master_volume == 1.0
        manager.set_master_volume(-2.0)
        assert manager.master_volume == 0.0


class TestGlobalAudioFunctions:
    """Tests for the global audio convenience functions."""

    def test_get_audio_manager_returns_instance(self):
        """Test that get_audio_manager returns an AudioManager."""
        from game.audio import AudioManager, get_audio_manager
        manager = get_audio_manager()
        assert isinstance(manager, AudioManager)

    def test_get_audio_manager_returns_same_instance(self):
        """Test that get_audio_manager is a singleton."""
        from game.audio import get_audio_manager
        manager1 = get_audio_manager()
        manager2 = get_audio_manager()
        assert manager1 is manager2

    def test_play_sound_doesnt_crash(self):
        """Test that play_sound convenience function works."""
        from game.audio import play_sound
        # Should not crash even with nonexistent sound
        play_sound("jump")

    def test_play_music_doesnt_crash(self):
        """Test that play_music convenience function works."""
        from game.audio import play_music, stop_music
        # Should not crash even with nonexistent file
        play_music("nonexistent.wav")
        stop_music()

    def test_stop_music_doesnt_crash(self):
        """Test that stop_music doesn't crash."""
        from game.audio import stop_music
        # Should not crash even if no music playing
        stop_music()


class TestSoundFilesExist:
    """Tests to verify all expected sound files were generated."""

    def test_sounds_directory_exists(self):
        """Test that assets/sounds directory exists."""
        assert os.path.exists("assets/sounds")

    def test_music_directory_exists(self):
        """Test that assets/music directory exists."""
        assert os.path.exists("assets/music")

    @pytest.mark.parametrize("sound_name", [
        "jump", "land", "slash", "hit", "hurt", "death",
        "coin", "treasure", "powerup", "health", "extra_life",
        "enemy_death", "shoot", "cannon", "parrot_attack",
        "shield_hit", "boss_hit", "boss_death",
        "door_unlock", "menu_select", "menu_confirm",
        "level_complete", "game_over"
    ])
    def test_sound_file_exists(self, sound_name: str):
        """Test that each expected sound file exists."""
        filepath = f"assets/sounds/{sound_name}.ogg"
        assert os.path.exists(filepath), f"Sound file missing: {filepath}"

    @pytest.mark.parametrize("music_name", [
        "menu", "level1", "level2", "level3", "level4",
        "level5", "boss", "victory"
    ])
    def test_music_file_exists(self, music_name: str):
        """Test that each expected music file exists."""
        filepath = f"assets/music/{music_name}.ogg"
        assert os.path.exists(filepath), f"Music file missing: {filepath}"

    def test_sound_files_are_valid_ogg(self):
        """Test that sound files can be loaded by pygame."""
        import pygame
        for filename in os.listdir("assets/sounds"):
            if filename.endswith(".ogg"):
                filepath = f"assets/sounds/{filename}"
                # Should not raise an exception
                sound = pygame.mixer.Sound(filepath)
                assert sound is not None
