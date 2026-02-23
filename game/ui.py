"""UI elements: HUD, menus, etc."""

import pygame

from game.settings import RED, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE, YELLOW


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
        except pygame.error:
            pass

    def draw(self, surface: pygame.Surface, player, level, score: int = 0) -> None:
        """Draw the HUD."""
        if not self.font:
            self._init_fonts()

        # Health hearts
        self._draw_health(surface, player)

        # Lives
        self._draw_lives(surface, player)

        # Treasure counter (not shown in boss levels)
        if not level.is_boss_level:
            self._draw_treasure(surface, level)

        # Score
        self._draw_score(surface, score)

        # Power-up indicators
        powerup_y = 70
        if player.has_parrot:
            self._draw_powerup(surface, "PARROT", player.parrot_timer, 600, powerup_y)
            powerup_y += 30
        if player.has_monkey:
            self._draw_powerup(surface, "MONKEY", player.monkey_timer, 720, powerup_y)
            powerup_y += 30
        if player.has_grog:
            self._draw_powerup(surface, "GROG RAGE", player.grog_timer, 300, powerup_y)
            powerup_y += 30
        if player.has_cutlass_fury:
            self._draw_powerup(surface, "FURY", player.cutlass_fury_timer, 600, powerup_y)
            powerup_y += 30
        if player.has_double_jump:
            self._draw_powerup(surface, "DBL JUMP", player.double_jump_timer, 1200, powerup_y)
            powerup_y += 30
        if player.has_magnet:
            self._draw_powerup(surface, "MAGNET", player.magnet_timer, 1800, powerup_y)
            powerup_y += 30
        if player.has_shield:
            self._draw_powerup_static(surface, "SHIELD", powerup_y)
            powerup_y += 25
        if player.has_cannon_shot:
            self._draw_powerup_ammo(surface, "CANNON", player.cannon_ammo, powerup_y)

        # Boss health bar
        if level.is_boss_level and level.boss and level.boss.active:
            self._draw_boss_health(surface, level.boss)

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

    def _draw_powerup_ammo(self, surface: pygame.Surface, name: str, ammo: int, y_pos: int) -> None:
        """Draw power-up indicator with ammo count (like cannon shot)."""
        if not self.small_font:
            return

        text = self.small_font.render(f"{name} x{ammo}", True, (255, 200, 100))
        surface.blit(text, (10, y_pos))

    def _draw_boss_health(self, surface: pygame.Surface, boss) -> None:
        """Draw boss health bar at bottom of screen."""
        if not self.font:
            return

        # Bar dimensions
        bar_width = 400
        bar_height = 24
        bar_x = (SCREEN_WIDTH - bar_width) // 2
        bar_y = SCREEN_HEIGHT - 50

        # Background
        pygame.draw.rect(surface, (40, 40, 40), (bar_x - 4, bar_y - 4, bar_width + 8, bar_height + 8))
        pygame.draw.rect(surface, (80, 80, 80), (bar_x, bar_y, bar_width, bar_height))

        # Health fill
        health_ratio = boss.health / boss.max_health
        fill_width = int(bar_width * health_ratio)

        # Color changes based on phase
        if boss.phase == 3:
            bar_color = (200, 50, 50)  # Red - dangerous!
        elif boss.phase == 2:
            bar_color = (200, 150, 50)  # Orange - getting aggressive
        else:
            bar_color = (180, 0, 0)  # Dark red - normal

        pygame.draw.rect(surface, bar_color, (bar_x, bar_y, fill_width, bar_height))

        # Border
        pygame.draw.rect(surface, (200, 180, 100), (bar_x - 4, bar_y - 4, bar_width + 8, bar_height + 8), 3)

        # Boss name with shadow for readability
        name_text = self.font.render("VICE-ADMIRAL GARP", True, (200, 180, 100))
        name_rect = name_text.get_rect(centerx=SCREEN_WIDTH // 2, bottom=bar_y - 8)
        # Draw shadow/outline for readability against any background
        shadow_color = (0, 0, 0)
        for dx, dy in [(-2, -2), (-2, 2), (2, -2), (2, 2), (-2, 0), (2, 0), (0, -2), (0, 2)]:
            shadow_text = self.font.render("VICE-ADMIRAL GARP", True, shadow_color)
            surface.blit(shadow_text, (name_rect.x + dx, name_rect.y + dy))
        surface.blit(name_text, name_rect)

        # Phase indicator
        phase_text = self.small_font.render(f"Phase {boss.phase}", True, WHITE)
        phase_rect = phase_text.get_rect(right=bar_x + bar_width, bottom=bar_y - 4)
        surface.blit(phase_text, phase_rect)


def draw_text_centered(surface: pygame.Surface, text: str, y: int,
                       font: pygame.font.Font, color: tuple = WHITE) -> None:
    """Draw text centered horizontally."""
    text_surface = font.render(text, True, color)
    x = (SCREEN_WIDTH - text_surface.get_width()) // 2
    surface.blit(text_surface, (x, y))
