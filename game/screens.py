"""Screen rendering for menus, transitions, and overlays."""

import math
from typing import Callable, Optional

import pygame

from game.settings import BLACK, SCREEN_HEIGHT, SCREEN_WIDTH, WHITE

# Pirate-themed color palette
GOLD = (255, 215, 0)
DARK_GOLD = (184, 134, 11)
PARCHMENT = (253, 245, 230)
DARK_RED = (139, 0, 0)
NAVY_BLUE = (0, 0, 128)
OCEAN_DARK = (0, 65, 106)
OCEAN_LIGHT = (0, 105, 148)
WOOD_BROWN = (101, 67, 33)
WOOD_LIGHT = (139, 90, 43)


class ScreenTransition:
    """Handles fade in/out transitions between screens."""

    def __init__(self, duration: int = 30):
        """
        Initialize transition.

        Args:
            duration: Number of frames for the transition
        """
        self.duration = duration
        self.timer = 0
        self.active = False
        self.fade_in = True  # True = fading in (black to clear), False = fading out
        self.on_complete: Optional[Callable[[], None]] = None

    def start_fade_out(self, on_complete: Optional[Callable[[], None]] = None) -> None:
        """Start fading to black."""
        self.active = True
        self.fade_in = False
        self.timer = 0
        self.on_complete = on_complete

    def start_fade_in(self) -> None:
        """Start fading from black to clear."""
        self.active = True
        self.fade_in = True
        self.timer = 0
        self.on_complete = None

    def update(self) -> None:
        """Update transition state."""
        if not self.active:
            return

        self.timer += 1
        if self.timer >= self.duration:
            self.active = False
            if self.on_complete:
                self.on_complete()
                self.on_complete = None

    def draw(self, surface: pygame.Surface) -> None:
        """Draw transition overlay."""
        if not self.active:
            return

        progress = self.timer / self.duration
        if self.fade_in:
            alpha = int(255 * (1 - progress))  # Black to clear
        else:
            alpha = int(255 * progress)  # Clear to black

        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(alpha)
        surface.blit(overlay, (0, 0))

    @property
    def is_complete(self) -> bool:
        """Check if transition is complete."""
        return not self.active


class LevelIntroCard:
    """Displays level name before gameplay starts."""

    def __init__(self):
        self.active = False
        self.timer = 0
        self.duration = 120  # 2 seconds
        self.level_name = ""
        self.level_subtitle = ""
        self.fade_duration = 20

    def start(self, level_name: str, subtitle: str = "") -> None:
        """Start showing the level intro card."""
        self.active = True
        self.timer = 0
        self.level_name = level_name
        self.level_subtitle = subtitle

    def update(self) -> bool:
        """
        Update the intro card.

        Returns:
            True if still showing, False if complete
        """
        if not self.active:
            return False

        self.timer += 1
        if self.timer >= self.duration:
            self.active = False
            return False
        return True

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the level intro card."""
        if not self.active:
            return

        # Calculate alpha for fade in/out
        if self.timer < self.fade_duration:
            # Fade in
            alpha = int(255 * (self.timer / self.fade_duration))
        elif self.timer > self.duration - self.fade_duration:
            # Fade out
            remaining = self.duration - self.timer
            alpha = int(255 * (remaining / self.fade_duration))
        else:
            alpha = 255

        # Dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((20, 20, 40))
        overlay.set_alpha(min(200, alpha))
        surface.blit(overlay, (0, 0))

        # Level name
        title_font = pygame.font.Font(None, 72)
        subtitle_font = pygame.font.Font(None, 36)

        # Draw with shadow effect
        title_surface = title_font.render(self.level_name, True, GOLD)
        title_shadow = title_font.render(self.level_name, True, BLACK)
        title_rect = title_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))

        title_surface.set_alpha(alpha)
        title_shadow.set_alpha(alpha)

        surface.blit(title_shadow, (title_rect.x + 3, title_rect.y + 3))
        surface.blit(title_surface, title_rect)

        # Subtitle
        if self.level_subtitle:
            sub_surface = subtitle_font.render(self.level_subtitle, True, PARCHMENT)
            sub_surface.set_alpha(alpha)
            sub_rect = sub_surface.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
            surface.blit(sub_surface, sub_rect)


class TitleScreen:
    """Animated title screen with pirate theme."""

    def __init__(self):
        self.frame = 0
        self.selected_level = 0
        self.title_font = pygame.font.Font(None, 80)
        self.subtitle_font = pygame.font.Font(None, 36)
        self.menu_font = pygame.font.Font(None, 32)
        self.small_font = pygame.font.Font(None, 24)

        # Wave animation for ocean
        self.wave_offset = 0

        # Available levels
        self.levels = [
            ("levels/level1.json", "Port Town", "Tutorial", "level1.ogg"),
            ("levels/level2.json", "HMS Revenge", "Ship Combat", "level2.ogg"),
            ("levels/level3.json", "Cliff Fortress", "Vertical Climb", "level3.ogg"),
            ("levels/level4.json", "The Armory", "Miniboss", "level4.ogg"),
            ("levels/level5.json", "Governor's Mansion", "Challenge", "level5.ogg"),
            ("levels/boss_arena.json", "Admiral's Quarters", "Final Boss", "boss.ogg"),
        ]

    def update(self) -> None:
        """Update animations."""
        self.frame += 1
        self.wave_offset = math.sin(self.frame * 0.05) * 5

    def handle_input(self, key: int) -> Optional[tuple[str, str]]:
        """
        Handle menu input.

        Returns:
            Tuple of (level_file, music_file) if level selected, None otherwise
        """
        if key == pygame.K_UP:
            self.selected_level = (self.selected_level - 1) % len(self.levels)
            return None
        elif key == pygame.K_DOWN:
            self.selected_level = (self.selected_level + 1) % len(self.levels)
            return None
        elif key == pygame.K_RETURN:
            level = self.levels[self.selected_level]
            return (level[0], level[3])  # file, music
        return None

    def draw(self, surface: pygame.Surface) -> None:
        """Draw the title screen."""
        # Sky gradient
        for y in range(SCREEN_HEIGHT // 2):
            ratio = y / (SCREEN_HEIGHT // 2)
            r = int(135 + (200 - 135) * (1 - ratio))
            g = int(206 + (220 - 206) * (1 - ratio))
            b = int(235 + (255 - 235) * (1 - ratio))
            pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))

        # Ocean with animated waves
        ocean_top = SCREEN_HEIGHT // 2 + 50
        for y in range(ocean_top, SCREEN_HEIGHT):
            depth = (y - ocean_top) / (SCREEN_HEIGHT - ocean_top)
            r = int(OCEAN_LIGHT[0] * (1 - depth * 0.5))
            g = int(OCEAN_LIGHT[1] * (1 - depth * 0.5))
            b = int(OCEAN_LIGHT[2] * (1 - depth * 0.3))
            pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))

        # Animated wave line
        wave_y = ocean_top
        for x in range(0, SCREEN_WIDTH, 4):
            wave_height = math.sin((x + self.frame * 2) * 0.03) * 8 + self.wave_offset
            pygame.draw.circle(surface, (150, 200, 255),
                             (x, int(wave_y + wave_height)), 4)

        # Title with shadow and glow effect
        title_text = "BOB THE PIRATE"

        # Outer glow
        glow_surface = self.title_font.render(title_text, True, DARK_GOLD)
        glow_rect = glow_surface.get_rect(center=(SCREEN_WIDTH // 2, 80))
        for offset in [(0, -2), (0, 2), (-2, 0), (2, 0)]:
            surface.blit(glow_surface, (glow_rect.x + offset[0], glow_rect.y + offset[1]))

        # Shadow
        shadow_surface = self.title_font.render(title_text, True, BLACK)
        surface.blit(shadow_surface, (glow_rect.x + 4, glow_rect.y + 4))

        # Main title
        title_surface = self.title_font.render(title_text, True, GOLD)
        surface.blit(title_surface, glow_rect)

        # Subtitle
        subtitle = "A Pirate's Quest for Treasure"
        sub_surface = self.subtitle_font.render(subtitle, True, PARCHMENT)
        sub_rect = sub_surface.get_rect(center=(SCREEN_WIDTH // 2, 130))
        # Shadow
        sub_shadow = self.subtitle_font.render(subtitle, True, (50, 50, 50))
        surface.blit(sub_shadow, (sub_rect.x + 2, sub_rect.y + 2))
        surface.blit(sub_surface, sub_rect)

        # Level selection box (parchment style)
        box_x = SCREEN_WIDTH // 2 - 200
        box_y = 165
        box_width = 400
        box_height = 220

        # Box shadow
        pygame.draw.rect(surface, (30, 30, 30),
                        (box_x + 5, box_y + 5, box_width, box_height))
        # Box background
        pygame.draw.rect(surface, WOOD_BROWN,
                        (box_x, box_y, box_width, box_height))
        pygame.draw.rect(surface, WOOD_LIGHT,
                        (box_x + 4, box_y + 4, box_width - 8, box_height - 8))
        # Inner parchment
        pygame.draw.rect(surface, PARCHMENT,
                        (box_x + 10, box_y + 10, box_width - 20, box_height - 20))

        # "Select Level" header
        header = self.menu_font.render("SELECT LEVEL", True, DARK_RED)
        header_rect = header.get_rect(center=(SCREEN_WIDTH // 2, box_y + 30))
        surface.blit(header, header_rect)

        # Level list
        for i, (_, name, subtitle, _) in enumerate(self.levels):
            y_pos = box_y + 55 + i * 28

            if i == self.selected_level:
                # Highlight bar
                pygame.draw.rect(surface, GOLD,
                               (box_x + 15, y_pos - 2, box_width - 30, 24))
                text_color = DARK_RED
                # Selection indicator (skull emoji alternative: arrow)
                indicator = self.menu_font.render("►", True, DARK_RED)
                surface.blit(indicator, (box_x + 20, y_pos))
            else:
                text_color = (80, 60, 40)

            # Level number and name
            level_text = f"{i + 1}. {name}"
            text_surface = self.menu_font.render(level_text, True, text_color)
            surface.blit(text_surface, (box_x + 45, y_pos))

            # Subtitle (smaller, right-aligned)
            sub_text = self.small_font.render(subtitle, True, (120, 100, 80))
            sub_rect = sub_text.get_rect(right=box_x + box_width - 20, centery=y_pos + 10)
            surface.blit(sub_text, sub_rect)

        # Instructions at bottom
        instructions = [
            ("↑↓", "Select Level"),
            ("ENTER", "Start Game"),
            ("ESC", "Quit"),
        ]

        inst_y = SCREEN_HEIGHT - 120
        inst_x = 50
        for key, action in instructions:
            # Key box
            key_surface = self.small_font.render(key, True, WHITE)
            key_rect = key_surface.get_rect()
            box_rect = pygame.Rect(inst_x, inst_y, key_rect.width + 16, 24)
            pygame.draw.rect(surface, (60, 60, 80), box_rect)
            pygame.draw.rect(surface, (100, 100, 120), box_rect, 2)
            surface.blit(key_surface, (inst_x + 8, inst_y + 4))

            # Action text
            action_surface = self.small_font.render(action, True, WHITE)
            surface.blit(action_surface, (inst_x + box_rect.width + 10, inst_y + 4))

            inst_x += box_rect.width + 100

        # Controls help at bottom
        controls_y = SCREEN_HEIGHT - 70
        controls = [
            "Controls: Arrow Keys/WASD = Move | Space = Jump | Q = Attack | E = Cannon",
            "Double-tap ←/→ = Barrel Roll | ↓ (air) = Anchor Slam | ESC = Pause"
        ]
        for i, line in enumerate(controls):
            text = self.small_font.render(line, True, (200, 200, 220))
            rect = text.get_rect(center=(SCREEN_WIDTH // 2, controls_y + i * 20))
            surface.blit(text, rect)


class PauseMenu:
    """Pause menu overlay with options."""

    def __init__(self):
        self.selected = 0
        self.options = ["Resume", "Quit to Menu"]
        self.title_font = pygame.font.Font(None, 64)
        self.menu_font = pygame.font.Font(None, 36)

    def handle_input(self, key: int) -> Optional[str]:
        """
        Handle menu input.

        Returns:
            'resume', 'quit', or None
        """
        if key == pygame.K_UP:
            self.selected = (self.selected - 1) % len(self.options)
            return None
        elif key == pygame.K_DOWN:
            self.selected = (self.selected + 1) % len(self.options)
            return None
        elif key == pygame.K_RETURN:
            if self.selected == 0:
                return "resume"
            else:
                return "quit"
        elif key == pygame.K_ESCAPE:
            return "resume"
        return None

    def reset(self) -> None:
        """Reset selection to default."""
        self.selected = 0

    def draw(self, surface: pygame.Surface) -> None:
        """Draw pause menu overlay."""
        # Semi-transparent dark overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill((0, 0, 20))
        overlay.set_alpha(180)
        surface.blit(overlay, (0, 0))

        # Title
        title = self.title_font.render("PAUSED", True, GOLD)
        title_shadow = self.title_font.render("PAUSED", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        surface.blit(title_shadow, (title_rect.x + 3, title_rect.y + 3))
        surface.blit(title, title_rect)

        # Menu options
        for i, option in enumerate(self.options):
            y = SCREEN_HEIGHT // 2 - 10 + i * 50

            if i == self.selected:
                color = GOLD
                text = f"► {option} ◄"
            else:
                color = WHITE
                text = option

            option_surface = self.menu_font.render(text, True, color)
            option_rect = option_surface.get_rect(center=(SCREEN_WIDTH // 2, y))

            # Shadow for selected
            if i == self.selected:
                shadow = self.menu_font.render(text, True, BLACK)
                surface.blit(shadow, (option_rect.x + 2, option_rect.y + 2))

            surface.blit(option_surface, option_rect)

        # Help text
        help_font = pygame.font.Font(None, 24)
        help_text = help_font.render("↑↓ Select  |  ENTER Confirm  |  ESC Resume", True, (150, 150, 150))
        help_rect = help_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 100))
        surface.blit(help_text, help_rect)


class GameOverScreen:
    """Game over screen with retry options."""

    def __init__(self):
        self.selected = 0
        self.options = ["Retry Level", "Quit to Menu"]
        self.title_font = pygame.font.Font(None, 80)
        self.menu_font = pygame.font.Font(None, 36)
        self.score_font = pygame.font.Font(None, 48)
        self.score = 0
        self.frame = 0

    def set_score(self, score: int) -> None:
        """Set the final score to display."""
        self.score = score

    def reset(self) -> None:
        """Reset selection."""
        self.selected = 0
        self.frame = 0

    def update(self) -> None:
        """Update animations."""
        self.frame += 1

    def handle_input(self, key: int) -> Optional[str]:
        """
        Handle menu input.

        Returns:
            'retry', 'quit', or None
        """
        if key == pygame.K_UP:
            self.selected = (self.selected - 1) % len(self.options)
            return None
        elif key == pygame.K_DOWN:
            self.selected = (self.selected + 1) % len(self.options)
            return None
        elif key == pygame.K_RETURN:
            return "retry" if self.selected == 0 else "quit"
        elif key == pygame.K_ESCAPE:
            return "quit"
        return None

    def draw(self, surface: pygame.Surface) -> None:
        """Draw game over screen."""
        # Dark red gradient background
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(80 * (1 - ratio * 0.5))
            g = int(20 * (1 - ratio * 0.5))
            b = int(20 * (1 - ratio * 0.5))
            pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))

        # Skull and crossbones pattern (subtle)
        pattern_color = (60, 10, 10)
        for x in range(0, SCREEN_WIDTH, 100):
            for y in range(0, SCREEN_HEIGHT, 100):
                offset_x = (y // 100 % 2) * 50
                pygame.draw.circle(surface, pattern_color, (x + offset_x + 25, y + 25), 8)
                pygame.draw.line(surface, pattern_color, (x + offset_x + 10, y + 35),
                               (x + offset_x + 40, y + 35), 3)

        # Title with shake effect
        shake_x = math.sin(self.frame * 0.3) * 2 if self.frame < 60 else 0
        shake_y = math.cos(self.frame * 0.4) * 2 if self.frame < 60 else 0

        title = self.title_font.render("GAME OVER", True, DARK_RED)
        title_glow = self.title_font.render("GAME OVER", True, (200, 50, 50))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2 + shake_x, 150 + shake_y))

        # Glow effect
        for offset in [(-2, 0), (2, 0), (0, -2), (0, 2)]:
            surface.blit(title_glow, (title_rect.x + offset[0], title_rect.y + offset[1]))
        surface.blit(title, title_rect)

        # Score display
        score_text = f"Final Score: {self.score}"
        score_surface = self.score_font.render(score_text, True, GOLD)
        score_shadow = self.score_font.render(score_text, True, BLACK)
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, 230))
        surface.blit(score_shadow, (score_rect.x + 2, score_rect.y + 2))
        surface.blit(score_surface, score_rect)

        # Menu options
        for i, option in enumerate(self.options):
            y = 320 + i * 50

            if i == self.selected:
                color = GOLD
                text = f"► {option} ◄"
            else:
                color = WHITE
                text = option

            option_surface = self.menu_font.render(text, True, color)
            option_rect = option_surface.get_rect(center=(SCREEN_WIDTH // 2, y))

            if i == self.selected:
                shadow = self.menu_font.render(text, True, BLACK)
                surface.blit(shadow, (option_rect.x + 2, option_rect.y + 2))

            surface.blit(option_surface, option_rect)


class LevelCompleteScreen:
    """Level complete celebration screen."""

    def __init__(self):
        self.title_font = pygame.font.Font(None, 72)
        self.menu_font = pygame.font.Font(None, 36)
        self.score_font = pygame.font.Font(None, 48)
        self.score = 0
        self.treasures_collected = 0
        self.treasures_total = 0
        self.frame = 0

    def set_stats(self, score: int, collected: int, total: int) -> None:
        """Set level completion stats."""
        self.score = score
        self.treasures_collected = collected
        self.treasures_total = total

    def reset(self) -> None:
        """Reset animation state."""
        self.frame = 0

    def update(self) -> None:
        """Update animations."""
        self.frame += 1

    def handle_input(self, key: int) -> Optional[str]:
        """Handle input, returns 'continue' or None."""
        if key in (pygame.K_RETURN, pygame.K_SPACE):
            return "continue"
        elif key == pygame.K_ESCAPE:
            return "quit"
        return None

    def draw(self, surface: pygame.Surface) -> None:
        """Draw level complete screen."""
        # Green gradient background
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(20 + 30 * ratio)
            g = int(80 - 30 * ratio)
            b = int(20 + 20 * ratio)
            pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))

        # Animated coins/sparkles in background
        for i in range(10):
            x = (i * 97 + self.frame * 2) % (SCREEN_WIDTH + 40) - 20
            y = 100 + i * 50 + math.sin(self.frame * 0.1 + i) * 20
            size = 4 + math.sin(self.frame * 0.2 + i * 0.5) * 2
            pygame.draw.circle(surface, GOLD, (int(x), int(y)), int(size))

        # Title with bounce effect
        bounce = abs(math.sin(self.frame * 0.1)) * 10 if self.frame < 60 else 0

        title = self.title_font.render("LEVEL COMPLETE!", True, GOLD)
        title_shadow = self.title_font.render("LEVEL COMPLETE!", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 120 - bounce))

        surface.blit(title_shadow, (title_rect.x + 3, title_rect.y + 3))
        surface.blit(title, title_rect)

        # Stats box
        box_x = SCREEN_WIDTH // 2 - 150
        box_y = 180
        box_width = 300
        box_height = 150

        pygame.draw.rect(surface, WOOD_BROWN, (box_x, box_y, box_width, box_height))
        pygame.draw.rect(surface, PARCHMENT, (box_x + 5, box_y + 5, box_width - 10, box_height - 10))
        pygame.draw.rect(surface, DARK_GOLD, (box_x, box_y, box_width, box_height), 3)

        # Stats
        stats = [
            f"Treasures: {self.treasures_collected}/{self.treasures_total}",
            f"Score: {self.score}",
        ]

        for i, stat in enumerate(stats):
            stat_surface = self.menu_font.render(stat, True, (60, 40, 20))
            stat_rect = stat_surface.get_rect(center=(SCREEN_WIDTH // 2, box_y + 50 + i * 50))
            surface.blit(stat_surface, stat_rect)

        # Continue prompt (pulsing)
        alpha = int(155 + 100 * math.sin(self.frame * 0.1))
        continue_text = "Press ENTER to Continue"
        continue_surface = self.menu_font.render(continue_text, True, WHITE)
        continue_surface.set_alpha(alpha)
        continue_rect = continue_surface.get_rect(center=(SCREEN_WIDTH // 2, 400))
        surface.blit(continue_surface, continue_rect)


class VictoryScreen:
    """Final boss victory screen."""

    def __init__(self):
        self.title_font = pygame.font.Font(None, 80)
        self.subtitle_font = pygame.font.Font(None, 48)
        self.menu_font = pygame.font.Font(None, 36)
        self.score = 0
        self.frame = 0

    def set_score(self, score: int) -> None:
        """Set final score."""
        self.score = score

    def reset(self) -> None:
        """Reset animation state."""
        self.frame = 0

    def update(self) -> None:
        """Update animations."""
        self.frame += 1

    def handle_input(self, key: int) -> Optional[str]:
        """Handle input, returns 'continue' or None."""
        if key in (pygame.K_RETURN, pygame.K_SPACE, pygame.K_ESCAPE):
            return "continue"
        return None

    def draw(self, surface: pygame.Surface) -> None:
        """Draw victory screen."""
        # Golden gradient background
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            r = int(60 + 40 * (1 - ratio))
            g = int(40 + 30 * (1 - ratio))
            b = int(10 + 10 * (1 - ratio))
            pygame.draw.line(surface, (r, g, b), (0, y), (SCREEN_WIDTH, y))

        # Fireworks/sparkles
        for i in range(15):
            t = (self.frame + i * 20) % 120
            if t < 60:
                x = 100 + (i * 73) % 600
                y = 50 + (i * 37) % 200
                # Exploding outward
                for j in range(8):
                    angle = j * math.pi / 4 + i * 0.3
                    dist = t * 2
                    px = x + math.cos(angle) * dist
                    py = y + math.sin(angle) * dist
                    size = max(1, 4 - t // 15)
                    color = [(255, 215, 0), (255, 100, 100), (100, 255, 100), WHITE][i % 4]
                    if 0 <= px < SCREEN_WIDTH and 0 <= py < SCREEN_HEIGHT:
                        pygame.draw.circle(surface, color, (int(px), int(py)), size)

        # "VICTORY!" with glow
        scale = 1.0 + 0.05 * math.sin(self.frame * 0.1)
        victory_font = pygame.font.Font(None, int(80 * scale))

        title = victory_font.render("VICTORY!", True, GOLD)
        title_glow = victory_font.render("VICTORY!", True, (255, 255, 200))
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 120))

        # Glow
        for dx, dy in [(-3, 0), (3, 0), (0, -3), (0, 3), (-2, -2), (2, 2), (-2, 2), (2, -2)]:
            surface.blit(title_glow, (title_rect.x + dx, title_rect.y + dy))
        # Shadow
        shadow = victory_font.render("VICTORY!", True, BLACK)
        surface.blit(shadow, (title_rect.x + 4, title_rect.y + 4))
        surface.blit(title, title_rect)

        # Boss defeated message
        boss_text = "Vice-Admiral Garp Defeated!"
        boss_surface = self.subtitle_font.render(boss_text, True, WHITE)
        boss_shadow = self.subtitle_font.render(boss_text, True, BLACK)
        boss_rect = boss_surface.get_rect(center=(SCREEN_WIDTH // 2, 200))
        surface.blit(boss_shadow, (boss_rect.x + 2, boss_rect.y + 2))
        surface.blit(boss_surface, boss_rect)

        # Final score with animated counting effect
        displayed_score = min(self.score, self.frame * 20)
        score_text = f"Final Score: {displayed_score}"
        score_surface = self.subtitle_font.render(score_text, True, GOLD)
        score_shadow = self.subtitle_font.render(score_text, True, BLACK)
        score_rect = score_surface.get_rect(center=(SCREEN_WIDTH // 2, 280))
        surface.blit(score_shadow, (score_rect.x + 2, score_rect.y + 2))
        surface.blit(score_surface, score_rect)

        # Congratulations message
        congrats = [
            "The seas are free once more!",
            "Captain Bob's legend grows...",
        ]
        for i, line in enumerate(congrats):
            line_surface = self.menu_font.render(line, True, PARCHMENT)
            line_rect = line_surface.get_rect(center=(SCREEN_WIDTH // 2, 360 + i * 35))
            surface.blit(line_surface, line_rect)

        # Continue prompt
        if self.frame > 60:  # Wait a moment before showing
            alpha = int(155 + 100 * math.sin(self.frame * 0.1))
            continue_text = "Press ENTER to Return to Menu"
            continue_surface = self.menu_font.render(continue_text, True, WHITE)
            continue_surface.set_alpha(alpha)
            continue_rect = continue_surface.get_rect(center=(SCREEN_WIDTH // 2, 480))
            surface.blit(continue_surface, continue_rect)
