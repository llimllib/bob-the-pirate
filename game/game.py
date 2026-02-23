"""Main game class and game loop."""

import pygame

from game.camera import Camera
from game.level import Level
from game.player import Player
from game.powerups import GhostShield, Parrot
from game.settings import BLACK, FPS, SCREEN_HEIGHT, SCREEN_WIDTH, SKY_BLUE, TITLE, WHITE
from game.tiles import get_background_layers
from game.ui import HUD


class GameState:
    """Enum for game states."""
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    LEVEL_COMPLETE = "level_complete"
    BOSS_DEFEATED = "boss_defeated"


class Game:
    """Main game class."""

    def __init__(self, debug: bool = False):
        pygame.init()
        pygame.mixer.init()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()

        self.state = GameState.MENU
        self.running = True
        self.debug = debug
        self.frame_count = 0

        # Game objects
        self.player = None
        self.level = None
        self.camera = None
        self.hud = HUD()

        # Score tracking
        self.score = 0

        # Power-up entities
        self.parrot = None
        self.shield = None

        # Background layers (loaded lazily)
        self.backgrounds = None

        # Fonts
        self.title_font = pygame.font.Font(None, 72)
        self.menu_font = pygame.font.Font(None, 36)

        # Level selection for menu
        self.available_levels = [
            ("levels/level1.json", "1 - Port Town"),
            ("levels/level2.json", "2 - HMS Revenge"),
            ("levels/boss_arena.json", "B - Boss Arena"),
        ]
        self.selected_level = 0

    def _try_damage_player(self, amount: int = 1) -> bool:
        """
        Try to damage the player, checking for shield first.
        Returns True if damage was processed (blocked or applied).
        """
        if self.player.invincible:
            return False

        # Check shield first
        if self.shield and self.player.has_shield:
            if self.shield.absorb_hit():
                self.player.has_shield = False
                self.shield = None
                return True

        return self.player.take_damage(amount)

    def _spawn_boss_minions(self) -> None:
        """Spawn sailors when the boss summons."""
        from game.enemies import Sailor

        boss = self.level.boss
        # Spawn 2 sailors on either side of boss
        spawn_positions = [
            (boss.rect.x - 100, boss.rect.bottom - 44),
            (boss.rect.x + 100, boss.rect.bottom - 44),
        ]

        for x, y in spawn_positions:
            # Make sure spawn is in bounds
            x = max(boss.arena_left, min(x, boss.arena_right - 28))
            sailor = Sailor(x, y, patrol_distance=50)
            self.level.enemies.add(sailor)

    def new_game(self, level_file: str = "levels/level1.json") -> None:
        """Start a new game."""
        self.level = Level()
        self.level.load_from_file(level_file)

        self.player = Player(*self.level.player_start)
        self.camera = Camera(self.level.width, self.level.height)
        self.score = 0
        self.parrot = None
        self.shield = None

        # Load background layers (lazy init) and set type based on level
        self.backgrounds = get_background_layers()
        self.backgrounds.set_background_type(self.level.background_type)

        self.state = GameState.PLAYING

    def handle_events(self) -> None:
        """Process pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU:
                    if event.key == pygame.K_RETURN:
                        level_file = self.available_levels[self.selected_level][0]
                        self.new_game(level_file)
                    elif event.key == pygame.K_UP:
                        self.selected_level = (self.selected_level - 1) % len(self.available_levels)
                    elif event.key == pygame.K_DOWN:
                        self.selected_level = (self.selected_level + 1) % len(self.available_levels)
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

                elif self.state == GameState.BOSS_DEFEATED:
                    if event.key == pygame.K_RETURN:
                        self.state = GameState.MENU

    def update(self) -> None:
        """Update game state."""
        if self.state != GameState.PLAYING:
            return

        # Get input
        keys = pygame.key.get_pressed()
        self.player.handle_input(keys)

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
        if self.player.hurt_timer > 0:
            self.player.hurt_timer -= 1
        if self.player.invincible:
            self.player.invincibility_timer -= 1
            if self.player.invincibility_timer <= 0:
                self.player.invincible = False
        if self.player.has_parrot:
            self.player.parrot_timer -= 1
            if self.player.parrot_timer <= 0:
                self.player.has_parrot = False
        if self.player.has_grog:
            self.player.grog_timer -= 1
            if self.player.grog_timer <= 0:
                self.player.has_grog = False
                self.player.damage_multiplier = 1

        # Update player animation
        self.player._update_animation_state()
        self.player.sprite.update()
        self.player.image = self.player.sprite.get_frame()

        # Update level
        self.level.update(self.player)

        # Check collectibles
        collected = self.level.collect_item(self.player)
        for item in collected:
            if "points" in item:
                self.score += item["points"]
            if item.get("powerup") == "parrot":
                self.parrot = Parrot(self.player)
            if item.get("powerup") == "shield":
                self.shield = GhostShield(self.player)

        # Update parrot companion
        if self.parrot:
            if self.player.has_parrot:
                self.parrot.update(self.level.enemies)
            else:
                self.parrot = None

        # Update shield
        if self.shield:
            if self.player.has_shield:
                self.shield.update()
            else:
                self.shield = None

        # Check enemy collisions
        for enemy in self.level.enemies:
            if self.player.rect.colliderect(enemy.rect):
                if self._try_damage_player(1):
                    pass  # Damage was applied or blocked

            # Check Officer sword attacks
            if hasattr(enemy, 'get_attack_hitbox') and hasattr(enemy, 'attacking'):
                attack_box = enemy.get_attack_hitbox()
                if attack_box and self.player.rect.colliderect(attack_box):
                    self._try_damage_player(1)

        # Check boss-specific attacks and death
        if self.level.boss:
            boss = self.level.boss

            if boss.active:
                attack_box = boss.get_attack_hitbox()
                if attack_box and self.player.rect.colliderect(attack_box):
                    # Boss charge does 2 damage
                    damage = 2 if boss.state == boss.STATE_CHARGE else 1
                    self._try_damage_player(damage)

                # Handle boss summon
                if boss.summon_pending:
                    self._spawn_boss_minions()
                    boss.summon_pending = False
            else:
                # Boss is dead!
                self.state = GameState.BOSS_DEFEATED
                self.score += 1000  # Boss bonus

        # Check projectile collisions
        for projectile in self.level.projectiles:
            if self.player.rect.colliderect(projectile.rect):
                if self._try_damage_player(projectile.damage):
                    projectile.kill()

        # Check attack hits
        if self.player.attacking:
            attack_box = self.player.get_attack_hitbox()
            if attack_box:
                for enemy in self.level.enemies:
                    if attack_box.colliderect(enemy.rect):
                        damage = 1 * self.player.damage_multiplier
                        enemy.take_damage(damage)

        # Check death (fell off level)
        if self.player.rect.top > self.level.height + 100:
            self.player.take_damage(self.player.health)  # Instant death

        # Check game over
        if self.player.lives <= 0:
            self.state = GameState.GAME_OVER

        # Check level complete (touching unlocked exit)
        if self.level.exit_door and not self.level.exit_door.locked:
            if self.player.rect.colliderect(self.level.exit_door.rect):
                self.state = GameState.LEVEL_COMPLETE

        # Update camera
        self.camera.update(self.player.rect)

        # Update background animations
        if self.backgrounds:
            self.backgrounds.update()

        # Debug output
        self.frame_count += 1
        if self.debug and self.frame_count % 30 == 0:
            self._print_debug_info()

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
        elif self.state == GameState.BOSS_DEFEATED:
            self._draw_boss_defeated()

        pygame.display.flip()

    def _draw_menu(self) -> None:
        """Draw the main menu."""
        self.screen.fill(SKY_BLUE)

        title = self.title_font.render("BOB THE PIRATE", True, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 100))
        self.screen.blit(title, title_rect)

        subtitle = self.menu_font.render("A Pirate's Quest for Treasure", True, (50, 50, 50))
        sub_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 160))
        self.screen.blit(subtitle, sub_rect)

        # Level selection
        level_title = self.menu_font.render("Select Level (UP/DOWN):", True, BLACK)
        self.screen.blit(level_title, (SCREEN_WIDTH // 2 - 130, 210))

        for i, (_, name) in enumerate(self.available_levels):
            color = (255, 215, 0) if i == self.selected_level else WHITE
            prefix = "> " if i == self.selected_level else "  "
            level_text = self.menu_font.render(f"{prefix}{name}", True, color)
            self.screen.blit(level_text, (SCREEN_WIDTH // 2 - 100, 250 + i * 35))

        start_text = self.menu_font.render("Press ENTER to Start", True, WHITE)
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, 400))
        self.screen.blit(start_text, start_rect)

        quit_text = self.menu_font.render("Press ESC to Quit", True, WHITE)
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, 440))
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
        offset = self.camera.get_offset()
        camera_x = offset[0]

        # Draw background layers (parallax)
        if self.backgrounds:
            self.backgrounds.draw(
                self.screen, camera_x, SCREEN_WIDTH, SCREEN_HEIGHT
            )
        else:
            # Fallback to solid color
            self.screen.fill(SKY_BLUE)

        # Draw level (tiles, collectibles, enemies)
        self.level.draw(self.screen, offset)

        # Draw player
        self.player.draw(self.screen, offset)

        # Draw shield effect
        if self.shield and self.player.has_shield:
            self.shield.draw(self.screen, offset)

        # Draw parrot companion
        if self.parrot and self.player.has_parrot:
            self.parrot.draw(self.screen, offset)

        # Draw HUD
        self.hud.draw(self.screen, self.player, self.level, self.score)

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

    def _draw_boss_defeated(self) -> None:
        """Draw boss defeated victory screen."""
        self.screen.fill((50, 30, 0))

        # Victory title
        text = self.title_font.render("VICTORY!", True, (255, 215, 0))
        text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 80))
        self.screen.blit(text, text_rect)

        # Boss name
        boss_text = self.menu_font.render("Admiral Blackwood Defeated!", True, WHITE)
        boss_rect = boss_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
        self.screen.blit(boss_text, boss_rect)

        # Score
        score_text = self.menu_font.render(f"Final Score: {self.score}", True, (255, 215, 0))
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
        self.screen.blit(score_text, score_rect)

        # Continue prompt
        cont = self.menu_font.render("Press ENTER for Menu", True, WHITE)
        cont_rect = cont.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 90))
        self.screen.blit(cont, cont_rect)

    def _print_debug_info(self) -> None:
        """Print debug information to console."""
        if not self.player:
            return

        # Player position and physics
        pos = f"pos=({self.player.rect.x}, {self.player.rect.y})"
        vel = f"vel=({self.player.velocity_x}, {self.player.velocity_y:.1f})"
        ground = f"on_ground={self.player.on_ground}"

        # Animation state
        anim_name = self.player.sprite.current_animation or "none"
        anim = self.player.sprite.animations.get(anim_name)
        if anim:
            anim_info = f"anim={anim_name}[{anim.current_frame}/{len(anim.frames)}] timer={anim.timer}/{anim.frame_duration}"
        else:
            anim_info = f"anim={anim_name}"

        # Combat state
        combat = []
        if self.player.attacking:
            combat.append(f"attacking({self.player.attack_timer})")
        if self.player.invincible:
            combat.append(f"invincible({self.player.invincibility_timer})")
        if self.player.hurt_timer > 0:
            combat.append(f"hurt({self.player.hurt_timer})")
        combat_str = " ".join(combat) if combat else "idle"

        # Power-ups
        powerups = []
        if self.player.has_parrot:
            powerups.append(f"parrot({self.player.parrot_timer})")
        if self.player.has_shield:
            powerups.append("shield")
        if self.player.has_grog:
            powerups.append(f"grog({self.player.grog_timer})")
        powerup_str = " ".join(powerups) if powerups else "none"

        print(f"[{self.frame_count:>5}] {pos} {vel} {ground} | {anim_info} | {combat_str} | powerups: {powerup_str}")

    def run(self) -> None:
        """Main game loop."""
        if self.debug:
            print("Debug mode enabled. Outputting player state every 30 frames (0.5s).")
            print("Format: [frame] position velocity on_ground | animation | combat | powerups")
            print("-" * 100)

        while self.running:
            self.clock.tick(FPS)
            self.handle_events()
            self.update()
            self.draw()

        pygame.quit()
