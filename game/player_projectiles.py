"""Player projectile classes (for skin abilities like Skeleton Pirate's bone throw)."""

import os

import pygame

from game.animation import AnimatedSprite, Animation, SpriteSheet, create_placeholder_frames
from game.settings import (
    SKELETON_BONE_DAMAGE,
    SKELETON_BONE_RANGE,
    SKELETON_BONE_SIZE,
    SKELETON_BONE_SPEED,
)


class BoneProjectile(pygame.sprite.Sprite):
    """
    Spinning bone projectile thrown by Skeleton Pirate.

    - Travels in a straight line
    - Has 8-frame spinning animation
    - Deals damage on contact with enemies
    - Despawns after traveling max range or hitting an enemy
    """

    def __init__(self, x: int, y: int, direction: int):
        """
        Create a bone projectile.

        Args:
            x: Starting x position
            y: Starting y position
            direction: 1 for right, -1 for left
        """
        super().__init__()

        self.direction = direction
        self.speed = SKELETON_BONE_SPEED
        self.damage = SKELETON_BONE_DAMAGE
        self.start_x = x
        self.max_range = SKELETON_BONE_RANGE

        # Set up animated sprite
        self.sprite = AnimatedSprite()
        self._load_animations()
        self.sprite.play("spin")

        # Visual
        self.image = self.sprite.get_frame()
        self.rect = self.image.get_rect(center=(x, y))

        self.active = True

    def _load_animations(self) -> None:
        """Load bone spinning animation from sprite sheet or use placeholders."""
        sprite_path = "assets/sprites/bone_projectile.png"

        if os.path.exists(sprite_path):
            sheet = SpriteSheet(sprite_path)
            # 8 frames in a horizontal strip
            spin_frames = sheet.get_strip(0, SKELETON_BONE_SIZE, SKELETON_BONE_SIZE, 8)
            self.sprite.add_animation("spin", Animation(spin_frames, frame_duration=2, loop=True))
        else:
            # Placeholder - white bone-colored rectangles
            bone_color = (230, 220, 200)  # Off-white bone color
            spin_frames = create_placeholder_frames(
                SKELETON_BONE_SIZE, SKELETON_BONE_SIZE, bone_color, 8, "bone"
            )
            self.sprite.add_animation("spin", Animation(spin_frames, frame_duration=2, loop=True))

    def update(self) -> None:
        """Update bone position and animation."""
        if not self.active:
            return

        # Move
        self.rect.x += self.speed * self.direction

        # Update animation
        self.sprite.update()
        self.image = self.sprite.get_frame()

        # Check if traveled too far
        if abs(self.rect.centerx - self.start_x) > self.max_range:
            self.kill()

    def draw(self, surface: pygame.Surface, camera_offset: tuple[int, int] = (0, 0)) -> None:
        """Draw the bone projectile."""
        if not self.active:
            return
        draw_rect = self.rect.move(-camera_offset[0], -camera_offset[1])
        surface.blit(self.image, draw_rect)
