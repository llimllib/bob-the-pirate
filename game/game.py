"""Main game class and game loop."""

import pygame
from game.settings import (
    SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE,
    SKY_BLUE, BLACK, WHITE
)
from game.player import Player
from game.level import Level
from game.camera import Camera
from game.ui import HUD


class GameState:
    """Enum for game states."""
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    LEVEL_COMPLETE = "level_complete"


class Game:
    """Main game class."""

    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        
        self.state = GameState.MENU
        self.running = True
        
        # Game objects
        self.player = None
        self.level = None
        self.camera = None
        self.hud = HUD()
        
        # Fonts
        self.title_font = pygame.font.Font(None, 72)
        self.menu_font = pygame.font.Font(None, 36)

    def new_game(self) -> None:
        """Start a new game."""
        self.level = Level()
        self.level.create_test_level()
        
        self.player = Player(*self.level.player_start)
        self.camera = Camera(self.level.width, self.level.height)
        
        self.state = GameState.PLAYING

    def handle_events(self) -> None:
        """Process pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            
            elif event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU:
                    if event.key == pygame.K_RETURN:
                        self.new_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False
                
                elif self.state == GameState.PLAYING:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.PAUSED
                    elif event.key == pygame.K_q:
                        self.player.attack()
                
                elif self.state == GameState.PAUSED:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_q:
                        self.state = GameState.MENU
                
                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_RETURN:
                        self.new_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.state = GameState.MENU
                
                elif self.state == GameState.LEVEL_COMPLETE:
                    if event.key == pygame.K_RETURN:
                        # TODO: Load next level
                        self.state = GameState.MENU

    def update(self) -> None:
        """Update game state."""
        if self.state != GameState.PLAYING:
            return
        
        # Get input
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)
        
        # Update player position (split into x and y for collision)
        old_x = self.player.rect.x
        old_y = self.player.rect.y
        
        # Apply gravity and update timers
        self.player.velocity_y += 0.8  # Gravity
        if self.player.velocity_y > 15:
            self.player.velocity_y = 15
        
        # Move X
        self.player.rect.x += int(self.player.velocity_x)
        self.level.check_collision_x(self.player)
        
        # Move Y
        self.player.rect.y += int(self.player.velocity_y)
        self.level.check_collision_y(self.player)
        
        # Update player timers
        if self.player.attacking:
            self.player.attack_timer -= 1
            if self.player.attack_timer <= 0:
                self.player.attacking = False
        if self.player.attack_cooldown > 0:
            self.player.attack_cooldown -= 1
        if self.player.invincible:
            self.player.invincibility_timer -= 1
            if self.player.invincibility_timer <= 0:
                self.player.invincible = False
        if self.player.has_parrot:
            self.player.parrot_timer -= 1
            if self.player.parrot_timer <= 0:
                self.player.has_parrot = False
        
        # Update level
        self.level.update(self.player)
        
        # Check collectibles
        self.level.collect_item(self.player)
        
        # Check enemy collisions
        for enemy in self.level.enemies:
            if self.player.rect.colliderect(enemy.rect):
                self.player.take_damage()
        
        # Check projectile collisions
        for projectile in self.level.projectiles:
            if self.player.rect.colliderect(projectile.rect):
                if self.player.take_damage(projectile.damage):
                    projectile.kill()
        
        # Check attack hits
        if self.player.attacking:
            attack_box = self.player.get_attack_hitbox()
            if attack_box:
                for enemy in self.level.enemies:
                    if attack_box.colliderect(enemy.rect):
                        enemy.take_damage(1)
        
        # Check death (fell off level)
        if self.player.rect.top > self.level.height + 100:
            self.player.take_damage(self.player.health)  # Instant death
        
        # Check game over
        if self.player.lives <= 0:
            self.state = GameState.GAME_OVER
        
        # Update camera
        self.camera.update(self.player.rect)

    def draw(self) -> None:
        """Render the game."""
        if self.state == GameState.MENU:
            self._draw_menu()
        elif self.state == GameState.PLAYING:
            self._draw_game()
        elif self.state == GameState.PAUSED:
            self._draw_game()
            self._draw_pause_overlay()
        elif self.state == GameState.GAME_OVER:
            self._draw_game_over()
        elif self.state == GameState.LEVEL_COMPLETE:
            self._draw_level_complete()
        
        pygame.display.flip()

    def _draw_menu(self) -> None:
        """Draw the main menu."""
        self.screen.fill(SKY_BLUE)
        
        title = self.title_font.render("BOB THE PIRATE", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 150))
        self.screen.blit(title, title_rect)
        
        subtitle = self.menu_font.render("A Pirate's Quest for Treasure", True, (50, 50, 50))
        sub_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 220))
        self.screen.blit(subtitle, sub_rect)
        
        start_text = self.menu_font.render("Press ENTER to Start", True, WHITE)
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, 350))
        self.screen.blit(start_text, start_rect)
        
        quit_text = self.menu_font.render("Press ESC to Quit", True, WHITE)
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, 400))
        self.screen.blit(quit_text, quit_rect)
        
        # Controls
        controls = [
            "Controls:",
            "Arrow Keys / WASD - Move",
            "Space / W / Up - Jump",
            "Q - Attack",
        ]
        for i, line in enumerate(controls):
            text = self.menu_font.render(line, True, (30, 30, 30))
            self.screen.blit(text, (50, 480 + i * 30))

    def _draw_game(self) -> None:
        """Draw the gameplay screen."""
        self.screen.fill(SKY_BLUE)
        
        offset = self.camera.get_offset()
        
        # Draw level
        self.level.draw(self.screen, offset)
        
        # Draw player
        self.player.draw(self.screen, offset)
        
        # Draw HUD
        self.hud.draw(self.screen, self.player, self.level)

    def _draw_pause_overlay(self) -> None:
        """Draw pause menu overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.fill(BLACK)
        overlay.set_alpha(128)
        self.screen.blit(overlay, (0, 0))
        
        pause_text = self.title_font.render("PAUSED", True, WHITE)
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(pause_text, pause_rect)
        
        resume_text = self.menu_font.render("Press ESC to Resume", True, WHITE)
        resume_rect = resume_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 20))
        self.screen.blit(resume_text, resume_rect)
        
        quit_text = self.menu_font.render("Press Q to Quit to Menu", True, WHITE)
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
        self.screen.blit(quit_text, quit_rect)

    def _draw_game_over(self) -> None:
        """Draw game over screen."""
        self.screen.fill((50, 0, 0))
        
        text = self.title_font.render("GAME OVER", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(text, text_rect)
        
        retry = self.menu_font.render("Press ENTER to Retry", True, WHITE)
        retry_rect = retry.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(retry, retry_rect)
        
        menu = self.menu_font.render("Press ESC for Menu", True, WHITE)
        menu_rect = menu.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 70))
        self.screen.blit(menu, menu_rect)

    def _draw_level_complete(self) -> None:
        """Draw level complete screen."""
        self.screen.fill((0, 50, 0))
        
        text = self.title_font.render("LEVEL COMPLETE!", True, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 50))
        self.screen.blit(text, text_rect)
        
        cont = self.menu_font.render("Press ENTER to Continue", True, WHITE)
        cont_rect = cont.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(cont, cont_rect)

    def run(self) -> None:
        """Main game loop."""
        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()
        
        pygame.quit()
