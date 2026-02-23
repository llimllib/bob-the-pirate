"""Camera system for scrolling levels."""

import pygame
from game.settings import SCREEN_WIDTH, SCREEN_HEIGHT


class Camera:
    """Camera that follows the player with smooth scrolling."""

    def __init__(self, level_width: int, level_height: int):
        self.x = 0
        self.y = 0
        self.level_width = level_width
        self.level_height = level_height
        
        # Smooth follow settings
        self.smoothing = 0.1
        self.dead_zone_x = SCREEN_WIDTH // 4
        self.dead_zone_y = SCREEN_HEIGHT // 4

    def update(self, target_rect: pygame.Rect) -> None:
        """Update camera position to follow target."""
        # Target position (center player on screen)
        target_x = target_rect.centerx - SCREEN_WIDTH // 2
        target_y = target_rect.centery - SCREEN_HEIGHT // 2
        
        # Smooth follow
        self.x += (target_x - self.x) * self.smoothing
        self.y += (target_y - self.y) * self.smoothing
        
        # Clamp to level bounds
        self.x = max(0, min(self.x, self.level_width - SCREEN_WIDTH))
        self.y = max(0, min(self.y, self.level_height - SCREEN_HEIGHT))
        
        # If level is smaller than screen, center it
        if self.level_width < SCREEN_WIDTH:
            self.x = (self.level_width - SCREEN_WIDTH) // 2
        if self.level_height < SCREEN_HEIGHT:
            self.y = (self.level_height - SCREEN_HEIGHT) // 2

    def get_offset(self) -> tuple[int, int]:
        """Get the camera offset for drawing."""
        return (int(self.x), int(self.y))

    def set_bounds(self, width: int, height: int) -> None:
        """Update level bounds."""
        self.level_width = width
        self.level_height = height
