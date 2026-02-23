"""Tests for the animation system."""

import pygame
import pytest

from game.animation import AnimatedSprite, Animation, create_placeholder_frames


@pytest.fixture(autouse=True)
def init_pygame():
    """Initialize pygame for tests."""
    pygame.init()
    pygame.display.set_mode((1, 1), pygame.HIDDEN)
    yield
    pygame.quit()


class TestAnimation:
    """Tests for the Animation class."""

    def test_init(self):
        """Test animation initialization."""
        frames = create_placeholder_frames(32, 32, (255, 0, 0), 4)
        anim = Animation(frames, frame_duration=6, loop=True)

        assert len(anim.frames) == 4
        assert anim.frame_duration == 6
        assert anim.loop is True
        assert anim.current_frame == 0
        assert anim.timer == 0
        assert anim.finished is False

    def test_update_advances_timer(self):
        """Test that update advances the timer."""
        frames = create_placeholder_frames(32, 32, (255, 0, 0), 4)
        anim = Animation(frames, frame_duration=6)

        anim.update()
        assert anim.timer == 1
        assert anim.current_frame == 0

    def test_update_advances_frame(self):
        """Test that animation advances to next frame."""
        frames = create_placeholder_frames(32, 32, (255, 0, 0), 4)
        anim = Animation(frames, frame_duration=3)

        # Advance through frame_duration ticks
        for _ in range(3):
            anim.update()

        assert anim.current_frame == 1
        assert anim.timer == 0

    def test_loop_animation(self):
        """Test that looping animation wraps around."""
        frames = create_placeholder_frames(32, 32, (255, 0, 0), 2)
        anim = Animation(frames, frame_duration=1, loop=True)

        anim.update()  # Frame 0 -> 1
        assert anim.current_frame == 1

        anim.update()  # Frame 1 -> 0 (loop)
        assert anim.current_frame == 0
        assert anim.finished is False

    def test_oneshot_animation(self):
        """Test that one-shot animation stops at last frame."""
        frames = create_placeholder_frames(32, 32, (255, 0, 0), 2)
        anim = Animation(frames, frame_duration=1, loop=False)

        anim.update()  # Frame 0 -> 1
        assert anim.current_frame == 1
        assert anim.finished is False

        anim.update()  # Stay at frame 1, mark finished
        assert anim.current_frame == 1
        assert anim.finished is True

        # Further updates don't change anything
        anim.update()
        assert anim.current_frame == 1

    def test_reset(self):
        """Test animation reset."""
        frames = create_placeholder_frames(32, 32, (255, 0, 0), 4)
        anim = Animation(frames, frame_duration=1, loop=False)

        # Advance to end
        for _ in range(10):
            anim.update()

        assert anim.current_frame == 3
        assert anim.finished is True

        anim.reset()
        assert anim.current_frame == 0
        assert anim.timer == 0
        assert anim.finished is False

    def test_get_frame(self):
        """Test getting current frame surface."""
        frames = create_placeholder_frames(32, 32, (255, 0, 0), 4)
        anim = Animation(frames, frame_duration=1)

        assert anim.get_frame() is frames[0]

        anim.update()
        assert anim.get_frame() is frames[1]


class TestAnimatedSprite:
    """Tests for the AnimatedSprite class."""

    def test_add_animation(self):
        """Test adding animations."""
        sprite = AnimatedSprite()
        frames = create_placeholder_frames(32, 32, (255, 0, 0), 2)
        anim = Animation(frames)

        sprite.add_animation("idle", anim)
        assert "idle" in sprite.animations

    def test_play_animation(self):
        """Test playing an animation."""
        sprite = AnimatedSprite()
        frames = create_placeholder_frames(32, 32, (255, 0, 0), 2)
        sprite.add_animation("idle", Animation(frames))

        sprite.play("idle")
        assert sprite.current_animation == "idle"

    def test_play_nonexistent_animation(self):
        """Test that playing nonexistent animation does nothing."""
        sprite = AnimatedSprite()
        sprite.play("nonexistent")
        assert sprite.current_animation is None

    def test_play_switches_animation(self):
        """Test switching between animations."""
        sprite = AnimatedSprite()
        sprite.add_animation("idle", Animation(create_placeholder_frames(32, 32, (255, 0, 0), 2)))
        sprite.add_animation("run", Animation(create_placeholder_frames(32, 32, (0, 255, 0), 4)))

        sprite.play("idle")
        assert sprite.current_animation == "idle"

        sprite.play("run")
        assert sprite.current_animation == "run"

    def test_play_same_animation_no_restart(self):
        """Test that playing same animation doesn't restart it."""
        sprite = AnimatedSprite()
        frames = create_placeholder_frames(32, 32, (255, 0, 0), 4)
        sprite.add_animation("idle", Animation(frames, frame_duration=1))

        sprite.play("idle")
        sprite.update()
        sprite.update()
        assert sprite.animations["idle"].current_frame == 2

        # Play same animation - should not restart
        sprite.play("idle")
        assert sprite.animations["idle"].current_frame == 2

    def test_play_force_restart(self):
        """Test force restarting an animation."""
        sprite = AnimatedSprite()
        frames = create_placeholder_frames(32, 32, (255, 0, 0), 4)
        sprite.add_animation("idle", Animation(frames, frame_duration=1))

        sprite.play("idle")
        sprite.update()
        sprite.update()
        assert sprite.animations["idle"].current_frame == 2

        # Force restart
        sprite.play("idle", force_restart=True)
        assert sprite.animations["idle"].current_frame == 0

    def test_update(self):
        """Test updating current animation."""
        sprite = AnimatedSprite()
        frames = create_placeholder_frames(32, 32, (255, 0, 0), 4)
        sprite.add_animation("idle", Animation(frames, frame_duration=1))

        sprite.play("idle")
        sprite.update()

        assert sprite.animations["idle"].current_frame == 1

    def test_get_frame_facing_right(self):
        """Test getting frame when facing right."""
        sprite = AnimatedSprite()
        frames = create_placeholder_frames(32, 32, (255, 0, 0), 2)
        sprite.add_animation("idle", Animation(frames))

        sprite.play("idle")
        sprite.facing_right = True

        frame = sprite.get_frame()
        assert frame.get_size() == (32, 32)

    def test_get_frame_facing_left(self):
        """Test getting frame when facing left (flipped)."""
        sprite = AnimatedSprite()
        frames = create_placeholder_frames(32, 32, (255, 0, 0), 2)
        sprite.add_animation("idle", Animation(frames))

        sprite.play("idle")
        sprite.facing_right = False

        frame = sprite.get_frame()
        assert frame.get_size() == (32, 32)

    def test_is_finished(self):
        """Test checking if animation is finished."""
        sprite = AnimatedSprite()
        frames = create_placeholder_frames(32, 32, (255, 0, 0), 2)
        sprite.add_animation("attack", Animation(frames, frame_duration=1, loop=False))

        sprite.play("attack")
        assert sprite.is_finished() is False

        sprite.update()  # Frame 0 -> 1
        sprite.update()  # Finish
        assert sprite.is_finished() is True

    def test_current_property(self):
        """Test the current animation property."""
        sprite = AnimatedSprite()
        frames = create_placeholder_frames(32, 32, (255, 0, 0), 2)
        anim = Animation(frames)
        sprite.add_animation("idle", anim)

        assert sprite.current is None

        sprite.play("idle")
        assert sprite.current is anim


class TestCreatePlaceholderFrames:
    """Tests for the placeholder frame creation utility."""

    def test_creates_correct_count(self):
        """Test that correct number of frames are created."""
        frames = create_placeholder_frames(32, 48, (255, 0, 0), 5)
        assert len(frames) == 5

    def test_creates_correct_size(self):
        """Test that frames have correct dimensions."""
        frames = create_placeholder_frames(32, 48, (255, 0, 0), 3)
        for frame in frames:
            assert frame.get_size() == (32, 48)

    def test_frames_are_surfaces(self):
        """Test that frames are pygame Surfaces."""
        frames = create_placeholder_frames(32, 32, (255, 0, 0), 2)
        for frame in frames:
            assert isinstance(frame, pygame.Surface)
