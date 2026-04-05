"""Animation system for sprite sheets."""

import pygame


class Animation:
    """
    Handles a single animation sequence from a sprite sheet.

    Animations can loop continuously or play once (one-shot).
    """

    def __init__(
        self,
        frames: list[pygame.Surface],
        frame_duration: int = 6,
        loop: bool = True
    ):
        """
        Initialize an animation.

        Args:
            frames: List of pygame Surfaces, one per frame
            frame_duration: How many game frames each animation frame lasts
            loop: Whether to loop or stop on last frame
        """
        self.frames = frames
        self.frame_duration = frame_duration
        self.loop = loop

        self.current_frame = 0
        self.timer = 0
        self.finished = False

    def reset(self) -> None:
        """Reset animation to the beginning."""
        self.current_frame = 0
        self.timer = 0
        self.finished = False

    def update(self) -> None:
        """Advance the animation by one game frame."""
        if self.finished:
            return

        self.timer += 1
        if self.timer >= self.frame_duration:
            self.timer = 0
            self.current_frame += 1

            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.current_frame = len(self.frames) - 1
                    self.finished = True

    def get_frame(self) -> pygame.Surface:
        """Get the current frame's surface."""
        return self.frames[self.current_frame]

    @property
    def is_finished(self) -> bool:
        """Check if a one-shot animation has completed."""
        return self.finished


class SpriteSheet:
    """
    Loads and slices a sprite sheet image into individual frames.

    Supports horizontal strips (single row) or grids.
    """

    def __init__(self, path: str):
        """
        Load a sprite sheet from file.

        Args:
            path: Path to the sprite sheet image
        """
        self.sheet = pygame.image.load(path).convert_alpha()

    def get_frame(
        self,
        x: int,
        y: int,
        width: int,
        height: int
    ) -> pygame.Surface:
        """
        Extract a single frame from the sheet.

        Args:
            x: X position in pixels
            y: Y position in pixels
            width: Frame width in pixels
            height: Frame height in pixels

        Returns:
            Surface containing the frame
        """
        frame = pygame.Surface((width, height), pygame.SRCALPHA)
        frame.blit(self.sheet, (0, 0), (x, y, width, height))
        return frame

    def get_strip(
        self,
        y: int,
        frame_width: int,
        frame_height: int,
        frame_count: int,
        x_start: int = 0
    ) -> list[pygame.Surface]:
        """
        Extract a horizontal strip of frames.

        Args:
            y: Y position of the strip
            frame_width: Width of each frame
            frame_height: Height of each frame
            frame_count: Number of frames to extract
            x_start: Starting X position (default 0)

        Returns:
            List of frame Surfaces
        """
        frames = []
        for i in range(frame_count):
            x = x_start + i * frame_width
            frames.append(self.get_frame(x, y, frame_width, frame_height))
        return frames

    def get_grid(
        self,
        frame_width: int,
        frame_height: int,
        columns: int,
        rows: int,
        x_start: int = 0,
        y_start: int = 0
    ) -> list[pygame.Surface]:
        """
        Extract frames from a grid, row by row.

        Args:
            frame_width: Width of each frame
            frame_height: Height of each frame
            columns: Number of columns in the grid
            rows: Number of rows in the grid
            x_start: Starting X position (default 0)
            y_start: Starting Y position (default 0)

        Returns:
            List of frame Surfaces (left-to-right, top-to-bottom)
        """
        frames = []
        for row in range(rows):
            for col in range(columns):
                x = x_start + col * frame_width
                y = y_start + row * frame_height
                frames.append(self.get_frame(x, y, frame_width, frame_height))
        return frames


class AnimatedSprite:
    """
    Manages multiple animations for a game entity.

    Typical usage:
        sprite = AnimatedSprite()
        sprite.add_animation("idle", Animation(idle_frames, 10))
        sprite.add_animation("run", Animation(run_frames, 6))
        sprite.play("idle")

        # In update loop:
        sprite.update()
        image = sprite.get_frame()
    """

    def __init__(self):
        """Initialize with no animations."""
        self.animations: dict[str, Animation] = {}
        self.current_animation: str | None = None
        self.facing_right = True
        self._flipped_cache: dict[str, list[pygame.Surface]] = {}

    def add_animation(self, name: str, animation: Animation) -> None:
        """
        Add a named animation.

        Args:
            name: Name to reference this animation
            animation: The Animation object
        """
        self.animations[name] = animation

    def play(self, name: str, force_restart: bool = False) -> None:
        """
        Start playing an animation.

        Args:
            name: Name of the animation to play
            force_restart: If True, restart even if already playing this animation
        """
        if name not in self.animations:
            return

        if self.current_animation != name or force_restart:
            self.current_animation = name
            self.animations[name].reset()

    def update(self) -> None:
        """Update the current animation."""
        if self.current_animation:
            self.animations[self.current_animation].update()

    def get_frame(self) -> pygame.Surface:
        """
        Get the current frame, flipped based on facing direction.

        Returns:
            The current animation frame (flipped if facing left)
        """
        if not self.current_animation:
            # Return empty surface if no animation
            return pygame.Surface((1, 1), pygame.SRCALPHA)

        frame = self.animations[self.current_animation].get_frame()

        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)

        return frame

    def is_finished(self) -> bool:
        """Check if the current animation has finished (for one-shot animations)."""
        if not self.current_animation:
            return True
        return self.animations[self.current_animation].is_finished

    def get_current_frame_index(self) -> int:
        """Get the current frame index of the playing animation."""
        if not self.current_animation:
            return 0
        return self.animations[self.current_animation].current_frame

    @property
    def current(self) -> Animation | None:
        """Get the current Animation object."""
        if self.current_animation:
            return self.animations[self.current_animation]
        return None


def create_placeholder_frames(
    width: int,
    height: int,
    color: tuple[int, int, int],
    frame_count: int,
    label: str = ""
) -> list[pygame.Surface]:
    """
    Create placeholder animation frames for testing.

    Each frame has a slightly different shade and frame number.

    Args:
        width: Frame width
        height: Frame height
        color: Base RGB color
        frame_count: Number of frames to create
        label: Optional text label

    Returns:
        List of placeholder frame Surfaces
    """
    frames = []
    for i in range(frame_count):
        surface = pygame.Surface((width, height), pygame.SRCALPHA)

        # Vary the color slightly per frame
        shade = 1.0 - (i * 0.1)
        frame_color = (
            int(color[0] * shade),
            int(color[1] * shade),
            int(color[2] * shade)
        )
        surface.fill(frame_color)

        # Draw border
        pygame.draw.rect(surface, (255, 255, 255), (0, 0, width, height), 1)

        # Draw frame number
        try:
            font = pygame.font.Font(None, min(width, height) // 2)
            text = font.render(f"{i + 1}", True, (255, 255, 255))
            text_rect = text.get_rect(center=(width // 2, height // 2))
            surface.blit(text, text_rect)
        except pygame.error:
            pass  # Font not available

        frames.append(surface)

    return frames
