"""UI elements: HUD, menus, etc."""

import math

import pygame

from game.settings import SCREEN_HEIGHT, SCREEN_WIDTH, WHITE

# UI Colors
GOLD = (255, 215, 0)
DARK_GOLD = (184, 134, 11)
HUD_BG = (20, 20, 30, 180)  # Semi-transparent dark
HEALTH_RED = (220, 50, 50)
HEALTH_EMPTY = (60, 40, 40)
BAR_BG = (40, 40, 50)
BAR_BORDER = (80, 80, 100)


class HUD:
    """Heads-up display showing health, score, etc."""

    def __init__(self):
        self.font = None
        self.small_font = None
        self.tiny_font = None
        self._init_fonts()
        self.frame = 0  # For animations

    def _init_fonts(self) -> None:
        """Initialize fonts (must be called after pygame.init)."""
        try:
            self.font = pygame.font.Font(None, 36)
            self.small_font = pygame.font.Font(None, 24)
            self.tiny_font = pygame.font.Font(None, 18)
        except pygame.error:
            pass

    def draw(self, surface: pygame.Surface, player, level, score: int = 0) -> None:
        """Draw the HUD."""
        if not self.font:
            self._init_fonts()

        self.frame += 1

        # Draw HUD panel backgrounds
        self._draw_hud_panels(surface, level)

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
            self._draw_powerup(surface, "PARROT", player.parrot_timer, 600, powerup_y, (100, 200, 100))
            powerup_y += 28
        if player.has_monkey:
            self._draw_powerup(surface, "MONKEY", player.monkey_timer, 720, powerup_y, (180, 130, 80))
            powerup_y += 28
        if player.has_grog:
            self._draw_powerup(surface, "GROG RAGE", player.grog_timer, 300, powerup_y, (200, 50, 50))
            powerup_y += 28
        if player.has_cutlass_fury:
            self._draw_powerup(surface, "FURY", player.cutlass_fury_timer, 600, powerup_y, (255, 150, 50))
            powerup_y += 28
        if player.has_double_jump:
            self._draw_powerup(surface, "DBL JUMP", player.double_jump_timer, 1200, powerup_y, (150, 150, 255))
            powerup_y += 28
        if player.has_magnet:
            self._draw_powerup(surface, "MAGNET", player.magnet_timer, 1800, powerup_y, (200, 100, 200))
            powerup_y += 28
        if player.has_shield:
            self._draw_powerup_static(surface, "SHIELD", powerup_y, (100, 200, 255))
            powerup_y += 25
        if player.has_cannon_shot:
            self._draw_powerup_ammo(surface, "CANNON", player.cannon_ammo, powerup_y)

        # Boss health bar
        if level.is_boss_level and level.boss and level.boss.active:
            self._draw_boss_health(surface, level.boss)

    def _draw_hud_panels(self, surface: pygame.Surface, level) -> None:
        """Draw semi-transparent background panels for HUD elements."""
        # Top-left panel (health, lives, powerups)
        panel = pygame.Surface((130, 65), pygame.SRCALPHA)
        panel.fill((20, 20, 30, 150))
        pygame.draw.rect(panel, (60, 60, 80), (0, 0, 130, 65), 2)
        surface.blit(panel, (5, 5))

        # Top-right panel (treasure, score)
        if not level.is_boss_level:
            panel2 = pygame.Surface((190, 55), pygame.SRCALPHA)
            panel2.fill((20, 20, 30, 150))
            pygame.draw.rect(panel2, (60, 60, 80), (0, 0, 190, 55), 2)
            surface.blit(panel2, (SCREEN_WIDTH - 195, 5))

    def _draw_health(self, surface: pygame.Surface, player) -> None:
        """Draw health hearts with pixel-art style."""
        heart_size = 20
        padding = 12
        spacing = 4

        for i in range(player.max_health):
            x = padding + i * (heart_size + spacing)
            y = padding

            if i < player.health:
                # Full heart - draw pixel art style heart
                self._draw_heart(surface, x, y, heart_size, HEALTH_RED, True)
            else:
                # Empty heart
                self._draw_heart(surface, x, y, heart_size, HEALTH_EMPTY, False)

    def _draw_heart(self, surface: pygame.Surface, x: int, y: int, size: int,
                    color: tuple, filled: bool) -> None:
        """Draw a pixel-art style heart."""
        # Simple heart shape using rectangles for pixel-art feel
        s = size // 5  # Base unit

        if filled:
            # Main color
            pygame.draw.rect(surface, color, (x + s, y, s * 3, s * 4))
            pygame.draw.rect(surface, color, (x, y + s, s * 5, s * 2))
            pygame.draw.rect(surface, color, (x + s * 2, y + s * 3, s, s))

            # Highlight
            highlight = (min(255, color[0] + 60), min(255, color[1] + 60), min(255, color[2] + 60))
            pygame.draw.rect(surface, highlight, (x + s, y + s, s, s))
        else:
            # Empty heart outline
            pygame.draw.rect(surface, color, (x + s, y, s * 3, s), 1)
            pygame.draw.rect(surface, color, (x, y + s, s, s * 2), 1)
            pygame.draw.rect(surface, color, (x + s * 4, y + s, s, s * 2), 1)
            pygame.draw.rect(surface, color, (x + s, y + s * 3, s, s), 1)
            pygame.draw.rect(surface, color, (x + s * 3, y + s * 3, s, s), 1)
            pygame.draw.rect(surface, color, (x + s * 2, y + s * 4, s, s), 1)

    def _draw_lives(self, surface: pygame.Surface, player) -> None:
        """Draw remaining lives with icon."""
        if not self.small_font:
            return

        # Small skull/bob icon
        icon_x = 14
        icon_y = 42
        pygame.draw.circle(surface, (200, 180, 150), (icon_x + 6, icon_y + 5), 5)

        # Lives text
        text = self.small_font.render(f"x{player.lives}", True, WHITE)
        shadow = self.small_font.render(f"x{player.lives}", True, (0, 0, 0))
        surface.blit(shadow, (icon_x + 15, icon_y - 1))
        surface.blit(text, (icon_x + 14, icon_y - 2))

    def _draw_treasure(self, surface: pygame.Surface, level) -> None:
        """Draw treasure collection counter with chest icon."""
        if not self.font:
            return

        # Chest icon
        chest_x = SCREEN_WIDTH - 188
        chest_y = 14
        pygame.draw.rect(surface, DARK_GOLD, (chest_x, chest_y, 16, 12))
        pygame.draw.rect(surface, GOLD, (chest_x + 2, chest_y + 2, 12, 8))
        pygame.draw.rect(surface, (100, 70, 30), (chest_x, chest_y + 10, 16, 4))

        # Treasure text
        collected = level.treasure_collected
        total = level.treasure_total

        # Pulsing effect when all collected
        if collected >= total:
            pulse = int(155 + 100 * math.sin(self.frame * 0.15))
            color = (255, pulse, 0)
        else:
            color = GOLD

        text = self.font.render(f"{collected}/{total}", True, color)
        shadow = self.font.render(f"{collected}/{total}", True, (0, 0, 0))
        surface.blit(shadow, (chest_x + 22, chest_y - 2))
        surface.blit(text, (chest_x + 20, chest_y - 3))

    def _draw_score(self, surface: pygame.Surface, score: int) -> None:
        """Draw score with coin icon."""
        if not self.small_font:
            return

        # Coin icon (spinning effect)
        coin_x = SCREEN_WIDTH - 188
        coin_y = 38
        coin_width = int(8 + 4 * abs(math.sin(self.frame * 0.1)))
        pygame.draw.ellipse(surface, GOLD, (coin_x + (12 - coin_width) // 2, coin_y, coin_width, 12))
        pygame.draw.ellipse(surface, DARK_GOLD, (coin_x + (12 - coin_width) // 2, coin_y, coin_width, 12), 1)

        # Score text
        text = self.small_font.render(f"{score:,}", True, WHITE)
        shadow = self.small_font.render(f"{score:,}", True, (0, 0, 0))
        surface.blit(shadow, (coin_x + 19, coin_y - 1))
        surface.blit(text, (coin_x + 18, coin_y - 2))

    def _draw_powerup(self, surface: pygame.Surface, name: str, timer: int,
                      max_timer: int, y_pos: int, color: tuple) -> None:
        """Draw active power-up indicator with styled timer bar."""
        if not self.small_font:
            return

        # Background panel
        panel = pygame.Surface((120, 24), pygame.SRCALPHA)
        panel.fill((20, 20, 30, 150))
        pygame.draw.rect(panel, (60, 60, 80), (0, 0, 120, 24), 1)
        surface.blit(panel, (8, y_pos - 2))

        # Power-up name
        text = self.tiny_font.render(name, True, color)
        surface.blit(text, (12, y_pos))

        # Timer bar
        bar_x = 12
        bar_y = y_pos + 12
        bar_width = 108
        bar_height = 6
        fill_ratio = max(0, min(1, timer / max_timer))
        fill_width = int(fill_ratio * bar_width)

        # Bar background
        pygame.draw.rect(surface, BAR_BG, (bar_x, bar_y, bar_width, bar_height))

        # Bar fill with gradient effect
        if fill_width > 0:
            # Main fill
            pygame.draw.rect(surface, color, (bar_x, bar_y, fill_width, bar_height))
            # Highlight on top
            highlight = (min(255, color[0] + 50), min(255, color[1] + 50), min(255, color[2] + 50))
            pygame.draw.rect(surface, highlight, (bar_x, bar_y, fill_width, 2))

        # Bar border
        pygame.draw.rect(surface, BAR_BORDER, (bar_x, bar_y, bar_width, bar_height), 1)

        # Flash warning when low
        if fill_ratio < 0.2 and self.frame % 20 < 10:
            pygame.draw.rect(surface, (255, 100, 100), (bar_x, bar_y, bar_width, bar_height), 1)

    def _draw_powerup_static(self, surface: pygame.Surface, name: str, y_pos: int,
                             color: tuple) -> None:
        """Draw power-up indicator without timer (like shield)."""
        if not self.small_font:
            return

        # Background panel
        panel = pygame.Surface((120, 20), pygame.SRCALPHA)
        panel.fill((20, 20, 30, 150))
        pygame.draw.rect(panel, color, (0, 0, 120, 20), 1)
        surface.blit(panel, (8, y_pos - 2))

        # Pulsing effect
        pulse = int(200 + 55 * math.sin(self.frame * 0.1))
        glow_color = (min(255, color[0] + 30), min(255, color[1] + 30), pulse)

        text = self.small_font.render(name, True, glow_color)
        surface.blit(text, (12, y_pos))

    def _draw_powerup_ammo(self, surface: pygame.Surface, name: str, ammo: int, y_pos: int) -> None:
        """Draw power-up indicator with ammo count (like cannon shot)."""
        if not self.small_font:
            return

        color = (255, 200, 100)

        # Background panel
        panel = pygame.Surface((120, 20), pygame.SRCALPHA)
        panel.fill((20, 20, 30, 150))
        pygame.draw.rect(panel, (60, 60, 80), (0, 0, 120, 20), 1)
        surface.blit(panel, (8, y_pos - 2))

        # Ammo display with bullets
        text = self.small_font.render(f"{name}", True, color)
        surface.blit(text, (12, y_pos))

        # Draw ammo bullets
        bullet_x = 75
        for i in range(ammo):
            pygame.draw.circle(surface, color, (bullet_x + i * 6, y_pos + 8), 2)

    def _draw_boss_health(self, surface: pygame.Surface, boss) -> None:
        """Draw boss health bar at bottom of screen."""
        if not self.font:
            return

        # Bar dimensions
        bar_width = 400
        bar_height = 24
        bar_x = (SCREEN_WIDTH - bar_width) // 2
        bar_y = SCREEN_HEIGHT - 50

        # Outer frame with shadow
        pygame.draw.rect(surface, (20, 20, 20),
                        (bar_x - 6, bar_y - 6, bar_width + 12, bar_height + 12))

        # Inner frame (metallic look)
        pygame.draw.rect(surface, (60, 50, 40),
                        (bar_x - 4, bar_y - 4, bar_width + 8, bar_height + 8))
        pygame.draw.rect(surface, (100, 90, 70),
                        (bar_x - 2, bar_y - 2, bar_width + 4, bar_height + 4))

        # Background
        pygame.draw.rect(surface, (40, 30, 30), (bar_x, bar_y, bar_width, bar_height))

        # Health fill
        health_ratio = boss.health / boss.max_health
        fill_width = int(bar_width * health_ratio)

        # Color changes based on phase with gradient
        if boss.phase == 3:
            bar_color = (200, 50, 50)  # Red - dangerous!
            bar_highlight = (255, 100, 100)
        elif boss.phase == 2:
            bar_color = (200, 150, 50)  # Orange - getting aggressive
            bar_highlight = (255, 200, 100)
        else:
            bar_color = (180, 50, 50)  # Dark red - normal
            bar_highlight = (220, 80, 80)

        if fill_width > 0:
            pygame.draw.rect(surface, bar_color, (bar_x, bar_y, fill_width, bar_height))
            # Gradient highlight
            pygame.draw.rect(surface, bar_highlight, (bar_x, bar_y, fill_width, bar_height // 3))

        # Border with gold trim
        pygame.draw.rect(surface, GOLD, (bar_x - 4, bar_y - 4, bar_width + 8, bar_height + 8), 2)

        # Boss name with shadow for readability
        name_text = self.font.render("VICE-ADMIRAL GARP", True, GOLD)
        name_rect = name_text.get_rect(centerx=SCREEN_WIDTH // 2, bottom=bar_y - 10)

        # Draw shadow/outline for readability against any background
        shadow_color = (0, 0, 0)
        for dx, dy in [(-2, 0), (2, 0), (0, -2), (0, 2), (-1, -1), (1, 1), (-1, 1), (1, -1)]:
            shadow_text = self.font.render("VICE-ADMIRAL GARP", True, shadow_color)
            surface.blit(shadow_text, (name_rect.x + dx, name_rect.y + dy))
        surface.blit(name_text, name_rect)

        # Phase indicator with icon
        phase_colors = {1: (150, 150, 150), 2: (255, 200, 100), 3: (255, 100, 100)}
        phase_color = phase_colors.get(boss.phase, WHITE)

        phase_text = self.small_font.render(f"Phase {boss.phase}", True, phase_color)
        phase_rect = phase_text.get_rect(right=bar_x + bar_width, bottom=bar_y - 6)

        # Phase indicator shadow
        phase_shadow = self.small_font.render(f"Phase {boss.phase}", True, (0, 0, 0))
        surface.blit(phase_shadow, (phase_rect.x + 1, phase_rect.y + 1))
        surface.blit(phase_text, phase_rect)


def draw_text_centered(surface: pygame.Surface, text: str, y: int,
                       font: pygame.font.Font, color: tuple = WHITE) -> None:
    """Draw text centered horizontally."""
    text_surface = font.render(text, True, color)
    x = (SCREEN_WIDTH - text_surface.get_width()) // 2
    surface.blit(text_surface, (x, y))
