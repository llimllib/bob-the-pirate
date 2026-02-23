"""UI elements: HUD, menus, etc."""

import pygame
from game.settings import (
    SCREEN_WIDTH, WHITE, RED, YELLOW, BLACK
)


class HUD:
    """Heads-up display showing health, score, etc."""

    def __init__(self):
        self.font = None
        self.small_font = None
        self._init_fonts()

    def _init_fonts(self) -> None:
        """Initialize fonts (must be called after pygame.init)."""
        try:
            self.font = pygame.font.Font(None, 36)
            self.small_font = pygame.font.Font(None, 24)
        except:
            pass

    def draw(self, surface: pygame.Surface, player, level, score: int = 0) -> None:
        """Draw the HUD."""
        if not self.font:
            self._init_fonts()
        
        # Health hearts
        self._draw_health(surface, player)
        
        # Lives
        self._draw_lives(surface, player)
        
        # Treasure counter
        self._draw_treasure(surface, level)
        
        # Score
        self._draw_score(surface, score)
        
        # Power-up indicators
        powerup_y = 70
        if player.has_parrot:
            self._draw_powerup(surface, "PARROT", player.parrot_timer, 600, powerup_y)
            powerup_y += 35
        if player.has_grog:
            self._draw_powerup(surface, "GROG RAGE", player.grog_timer, 300, powerup_y)
            powerup_y += 35
        if player.has_shield:
            self._draw_powerup_static(surface, "SHIELD", powerup_y)

    def _draw_health(self, surface: pygame.Surface, player) -> None:
        """Draw health hearts."""
        heart_size = 24
        padding = 10
        
        for i in range(player.max_health):
            x = padding + i * (heart_size + 5)
            y = padding
            
            if i < player.health:
                color = RED
            else:
                color = (60, 60, 60)
            
            # Draw heart shape (simplified as circle)
            pygame.draw.circle(surface, color, (x + heart_size // 2, y + heart_size // 2), heart_size // 2)

    def _draw_lives(self, surface: pygame.Surface, player) -> None:
        """Draw remaining lives."""
        if not self.small_font:
            return
        
        text = self.small_font.render(f"x{player.lives}", True, WHITE)
        surface.blit(text, (10, 45))

    def _draw_treasure(self, surface: pygame.Surface, level) -> None:
        """Draw treasure collection counter."""
        if not self.font:
            return
        
        text = self.font.render(
            f"Treasure: {level.treasure_collected}/{level.treasure_total}",
            True, YELLOW
        )
        surface.blit(text, (SCREEN_WIDTH - 200, 10))

    def _draw_score(self, surface: pygame.Surface, score: int) -> None:
        """Draw score."""
        if not self.small_font:
            return
        
        text = self.small_font.render(f"Score: {score}", True, WHITE)
        surface.blit(text, (SCREEN_WIDTH - 200, 45))

    def _draw_powerup(self, surface: pygame.Surface, name: str, timer: int, 
                      max_timer: int, y_pos: int) -> None:
        """Draw active power-up indicator with timer bar."""
        if not self.small_font:
            return
        
        # Draw power-up name
        text = self.small_font.render(name, True, WHITE)
        surface.blit(text, (10, y_pos))
        
        # Timer bar
        bar_width = 100
        bar_height = 8
        fill_width = int((timer / max_timer) * bar_width)
        
        pygame.draw.rect(surface, (60, 60, 60), (10, y_pos + 18, bar_width, bar_height))
        pygame.draw.rect(surface, (0, 200, 0), (10, y_pos + 18, fill_width, bar_height))

    def _draw_powerup_static(self, surface: pygame.Surface, name: str, y_pos: int) -> None:
        """Draw power-up indicator without timer (like shield)."""
        if not self.small_font:
            return
        
        text = self.small_font.render(name, True, (100, 200, 255))
        surface.blit(text, (10, y_pos))


def draw_text_centered(surface: pygame.Surface, text: str, y: int, 
                       font: pygame.font.Font, color: tuple = WHITE) -> None:
    """Draw text centered horizontally."""
    text_surface = font.render(text, True, color)
    x = (SCREEN_WIDTH - text_surface.get_width()) // 2
    surface.blit(text_surface, (x, y))
