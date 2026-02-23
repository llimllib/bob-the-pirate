"""Audio system for sound effects and music."""

import os
from typing import Optional

import pygame


class AudioManager:
    """Manages sound effects and music playback with volume control."""

    def __init__(self):
        """Initialize the audio manager."""
        # Ensure mixer is initialized
        if not pygame.mixer.get_init():
            pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)

        # Volume settings (0.0 to 1.0)
        self.sfx_volume = 0.7
        self.music_volume = 0.5
        self.master_volume = 1.0

        # Sound effect cache
        self.sounds: dict[str, pygame.mixer.Sound] = {}

        # Current music track
        self.current_music: Optional[str] = None

        # Load all sounds
        self._load_sounds()

    def _load_sounds(self) -> None:
        """Load all sound effects from assets/sounds/."""
        sound_dir = "assets/sounds"
        if not os.path.exists(sound_dir):
            return

        for filename in os.listdir(sound_dir):
            if filename.endswith(".wav"):
                name = filename[:-4]  # Remove .wav extension
                path = os.path.join(sound_dir, filename)
                try:
                    self.sounds[name] = pygame.mixer.Sound(path)
                except pygame.error:
                    print(f"Warning: Could not load sound {path}")

    def play_sound(self, name: str) -> None:
        """Play a sound effect by name."""
        if name in self.sounds:
            sound = self.sounds[name]
            sound.set_volume(self.sfx_volume * self.master_volume)
            sound.play()

    def play_music(self, music_file: str, loop: bool = True) -> None:
        """Play background music."""
        music_path = f"assets/music/{music_file}"
        if not os.path.exists(music_path):
            return

        if self.current_music == music_file:
            return  # Already playing

        try:
            pygame.mixer.music.load(music_path)
            pygame.mixer.music.set_volume(self.music_volume * self.master_volume)
            pygame.mixer.music.play(-1 if loop else 0)
            self.current_music = music_file
        except pygame.error:
            print(f"Warning: Could not load music {music_path}")

    def stop_music(self) -> None:
        """Stop the current music."""
        pygame.mixer.music.stop()
        self.current_music = None

    def pause_music(self) -> None:
        """Pause the current music."""
        pygame.mixer.music.pause()

    def unpause_music(self) -> None:
        """Unpause the music."""
        pygame.mixer.music.unpause()

    def set_sfx_volume(self, volume: float) -> None:
        """Set sound effects volume (0.0 to 1.0)."""
        self.sfx_volume = max(0.0, min(1.0, volume))

    def set_music_volume(self, volume: float) -> None:
        """Set music volume (0.0 to 1.0)."""
        self.music_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume * self.master_volume)

    def set_master_volume(self, volume: float) -> None:
        """Set master volume (0.0 to 1.0)."""
        self.master_volume = max(0.0, min(1.0, volume))
        pygame.mixer.music.set_volume(self.music_volume * self.master_volume)


# Global audio manager instance (lazy initialization)
_audio_manager: Optional[AudioManager] = None


def get_audio_manager() -> AudioManager:
    """Get the global audio manager instance."""
    global _audio_manager
    if _audio_manager is None:
        _audio_manager = AudioManager()
    return _audio_manager


def play_sound(name: str) -> None:
    """Convenience function to play a sound effect."""
    get_audio_manager().play_sound(name)


def play_music(music_file: str, loop: bool = True) -> None:
    """Convenience function to play background music."""
    get_audio_manager().play_music(music_file, loop)


def stop_music() -> None:
    """Convenience function to stop music."""
    get_audio_manager().stop_music()
