"""Main game class and game loop."""

import pygame

from game.audio import get_audio_manager, play_music, play_sound, stop_music
from game.camera import Camera
from game.level import Level
from game.player import Player
from game.powerups import GhostShield, Monkey, Parrot, PlayerCannonball
from game.settings import (
    ANCHOR_SLAM_DAMAGE,
    ANCHOR_SLAM_RADIUS,
    BARREL_ROLL_COOLDOWN,
    BLACK,
    FPS,
    MAGNET_RANGE,
    MAGNET_STRENGTH,
    SCREEN_HEIGHT,
    SCREEN_WIDTH,
    SKY_BLUE,
    TITLE,
    WHITE,
)
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
        self.monkey = None
        self.player_projectiles = pygame.sprite.Group()

        # Background layers (loaded lazily)
        self.backgrounds = None

        # Fonts
        self.title_font = pygame.font.Font(None, 72)
        self.menu_font = pygame.font.Font(None, 36)

        # Level selection for menu
        self.available_levels = [
            ("levels/level1.json", "1 - Port Town", "level1.wav"),
            ("levels/level2.json", "2 - HMS Revenge", "level2.wav"),
            ("levels/level3.json", "3 - Cliff Fortress", "level3.wav"),
            ("levels/level4.json", "4 - The Armory (Miniboss)", "level4.wav"),
            ("levels/level5.json", "5 - Governor's Mansion", "level5.wav"),
            ("levels/boss_arena.json", "B - Admiral's Quarters (Boss)", "boss.wav"),
        ]
        self.selected_level = 0

        # Track player states for sound triggers
        self.was_on_ground = True
        self.was_jumping = False

        # Track key states for double-tap detection
        self.prev_keys: dict[int, bool] = {}

        # Initialize audio manager
        self.audio = get_audio_manager()

        # Play menu music
        play_music("menu.wav")

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
                play_sound("shield_hit")
                return True

        if self.player.take_damage(amount):
            if self.player.health > 0:
                play_sound("hurt")
            else:
                play_sound("death")
            return True
        return False

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
        self.monkey = None
        self.player_projectiles = pygame.sprite.Group()

        # Reset sound state tracking
        self.was_on_ground = True
        self.was_jumping = False

        # Reset key tracking
        self.prev_keys = {}

        # Load background layers (lazy init) and set type based on level
        self.backgrounds = get_background_layers()
        self.backgrounds.set_background_type(self.level.background_type)

        # Find and play appropriate music for this level
        for lf, _, music in self.available_levels:
            if lf == level_file:
                play_music(music)
                break

        # Track projectile count for sound triggers
        self.last_projectile_count = 0

        self.state = GameState.PLAYING

    def handle_events(self) -> None:
        """Process pygame events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            elif event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU:
                    if event.key == pygame.K_RETURN:
                        play_sound("menu_confirm")
                        level_file = self.available_levels[self.selected_level][0]
                        self.new_game(level_file)
                    elif event.key == pygame.K_UP:
                        play_sound("menu_select")
                        self.selected_level = (self.selected_level - 1) % len(self.available_levels)
                    elif event.key == pygame.K_DOWN:
                        play_sound("menu_select")
                        self.selected_level = (self.selected_level + 1) % len(self.available_levels)
                    elif event.key == pygame.K_ESCAPE:
                        self.running = False

                elif self.state == GameState.PLAYING:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.PAUSED
                        self.audio.pause_music()
                    elif event.key == pygame.K_q:
                        if self.player.attack():
                            play_sound("slash")
                    elif event.key == pygame.K_e:
                        # Cannon shot (alternate attack)
                        if self.player.fire_cannon():
                            play_sound("cannon")
                            direction = 1 if self.player.facing_right else -1
                            cannonball = PlayerCannonball(
                                self.player.rect.centerx + direction * 20,
                                self.player.rect.centery,
                                direction
                            )
                            self.player_projectiles.add(cannonball)
                    elif event.key in (pygame.K_SPACE, pygame.K_w, pygame.K_UP):
                        # Double jump (if in air and have power-up)
                        if not self.player.on_ground and self.player.try_double_jump():
                            play_sound("jump")
                    elif event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        # Barrel roll left (double-tap)
                        if self.player.try_barrel_roll(-1, self.frame_count):
                            play_sound("jump")  # Roll sound (reuse jump for now)
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        # Barrel roll right (double-tap)
                        if self.player.try_barrel_roll(1, self.frame_count):
                            play_sound("jump")  # Roll sound (reuse jump for now)
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        # Anchor slam (in air only)
                        if self.player.try_anchor_slam():
                            play_sound("slash")  # Slam start sound

                elif self.state == GameState.PAUSED:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.PLAYING
                        self.audio.unpause_music()
                    elif event.key == pygame.K_q:
                        self.state = GameState.MENU
                        play_music("menu.wav")

                elif self.state == GameState.GAME_OVER:
                    if event.key == pygame.K_RETURN:
                        play_sound("menu_confirm")
                        self.new_game()
                    elif event.key == pygame.K_ESCAPE:
                        self.state = GameState.MENU
                        play_music("menu.wav")

                elif self.state == GameState.LEVEL_COMPLETE:
                    if event.key == pygame.K_RETURN:
                        play_sound("menu_confirm")
                        # TODO: Load next level
                        self.state = GameState.MENU
                        play_music("menu.wav")

                elif self.state == GameState.BOSS_DEFEATED:
                    if event.key == pygame.K_RETURN:
                        play_sound("menu_confirm")
                        self.state = GameState.MENU
                        play_music("menu.wav")

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

        # Check for anchor slam landing
        if self.player.on_ground and self.player.land_anchor_slam():
            play_sound("land")  # Impact sound
            # Damage all enemies in radius
            slam_center = self.player.rect.midbottom
            for enemy in self.level.enemies:
                # Calculate distance from slam center to enemy center
                dx = enemy.rect.centerx - slam_center[0]
                dy = enemy.rect.centery - slam_center[1]
                dist = (dx * dx + dy * dy) ** 0.5
                if dist <= ANCHOR_SLAM_RADIUS:
                    was_alive = enemy.health > 0
                    killed = enemy.take_damage(ANCHOR_SLAM_DAMAGE)
                    if was_alive:
                        if killed:
                            if enemy == self.level.boss:
                                play_sound("boss_hit")
                            else:
                                play_sound("enemy_death")
                        else:
                            if enemy == self.level.boss:
                                play_sound("boss_hit")
                            else:
                                play_sound("hit")

        # Sound: detect jump and landing
        if not self.was_on_ground and self.player.on_ground:
            # Just landed
            play_sound("land")
        if self.player.velocity_y < 0 and not self.was_jumping:
            # Just started jumping
            play_sound("jump")

        # Track states for next frame
        self.was_on_ground = self.player.on_ground
        self.was_jumping = self.player.velocity_y < 0

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

        # Update barrel roll timer
        if self.player.rolling:
            self.player.roll_timer -= 1
            if self.player.roll_timer <= 0:
                self.player.rolling = False
                self.player.roll_cooldown = BARREL_ROLL_COOLDOWN
        if self.player.roll_cooldown > 0:
            self.player.roll_cooldown -= 1

        # Update anchor slam cooldown
        if self.player.slam_cooldown > 0:
            self.player.slam_cooldown -= 1

        # Update player animation
        self.player._update_animation_state()
        self.player.sprite.update()
        self.player.image = self.player.sprite.get_frame()

        # Update level
        self.level.update(self.player)

        # Check for door unlock sound
        if self.level.door_just_unlocked:
            play_sound("door_unlock")
            self.level.door_just_unlocked = False

        # Check for new projectiles (enemy shots)
        current_projectile_count = len(self.level.projectiles)
        if current_projectile_count > self.last_projectile_count:
            # New projectile was fired - play appropriate sound
            # Check what type by looking at the newest projectile
            for proj in self.level.projectiles:
                if proj.__class__.__name__ == "Cannonball":
                    play_sound("cannon")
                    break
                elif proj.__class__.__name__ in ("MusketBall", "AdmiralBullet"):
                    play_sound("shoot")
                    break
        self.last_projectile_count = current_projectile_count

        # Check collectibles
        collected = self.level.collect_item(self.player)
        for item in collected:
            if "points" in item:
                self.score += item["points"]
            if item.get("powerup") == "parrot":
                self.parrot = Parrot(self.player)
                play_sound("powerup")
            if item.get("powerup") == "shield":
                self.shield = GhostShield(self.player)
                play_sound("powerup")
            if item.get("powerup") == "grog":
                play_sound("powerup")
            if item.get("powerup") == "monkey":
                self.monkey = Monkey(self.player, self.player_projectiles)
                play_sound("powerup")
            if item.get("powerup") in ("cannon_shot", "double_jump", "cutlass_fury", "magnet"):
                play_sound("powerup")

            # Play appropriate collection sound
            item_type = item.get("type")
            if item_type == "treasure":
                play_sound("treasure")
            elif item_type == "coin":
                play_sound("coin")
            elif item_type == "health":
                play_sound("health")
            elif item_type == "life":
                play_sound("extra_life")

        # Update parrot companion
        if self.parrot:
            if self.player.has_parrot:
                damaged_enemy = self.parrot.update(self.level.enemies)
                if damaged_enemy:
                    play_sound("parrot_attack")
                    if not damaged_enemy.active:
                        play_sound("enemy_death")
            else:
                self.parrot = None

        # Update shield
        if self.shield:
            if self.player.has_shield:
                self.shield.update()
            else:
                self.shield = None

        # Update monkey companion
        if self.monkey:
            if self.player.has_monkey:
                self.monkey.update(self.level.enemies)
            else:
                self.monkey = None

        # Update player projectiles (cannon shots, coconuts)
        for proj in self.player_projectiles:
            proj.update()
            # Check collision with enemies
            for enemy in self.level.enemies:
                if proj.rect.colliderect(enemy.rect):
                    damage = proj.damage
                    was_alive = enemy.health > 0
                    killed = enemy.take_damage(damage)
                    proj.kill()
                    if was_alive:
                        if killed:
                            if enemy == self.level.boss:
                                play_sound("boss_hit")
                            else:
                                play_sound("enemy_death")
                        else:
                            if enemy == self.level.boss:
                                play_sound("boss_hit")
                            else:
                                play_sound("hit")
                    break
            # Remove off-screen projectiles
            if proj.rect.right < 0 or proj.rect.left > self.level.width:
                proj.kill()

        # Treasure Magnet - pull collectibles toward player
        if self.player.has_magnet:
            import math
            for item in self.level.collectibles:
                if item.collected:
                    continue
                dx = self.player.rect.centerx - item.rect.centerx
                dy = self.player.rect.centery - item.rect.centery
                dist = math.sqrt(dx * dx + dy * dy)
                if dist < MAGNET_RANGE and dist > 0:
                    # Pull toward player
                    pull_x = (dx / dist) * MAGNET_STRENGTH
                    pull_y = (dy / dist) * MAGNET_STRENGTH
                    item.rect.x += int(pull_x)
                    item.rect.y += int(pull_y)

        # Check enemy collisions
        for enemy in self.level.enemies:
            # Skip damage if enemy was recently hit (stunned)
            if not enemy.can_damage_player():
                continue

            if self.player.rect.colliderect(enemy.rect):
                if self._try_damage_player(1):
                    pass  # Damage was applied or blocked

            # Check Officer sword attacks
            if hasattr(enemy, 'get_attack_hitbox') and hasattr(enemy, 'attacking'):
                attack_box = enemy.get_attack_hitbox()
                if attack_box and self.player.rect.colliderect(attack_box):
                    self._try_damage_player(1)

            # Check Bosun attacks (miniboss with variable damage)
            if hasattr(enemy, 'get_attack_hitbox') and hasattr(enemy, 'get_attack_damage'):
                attack_box = enemy.get_attack_hitbox()
                if attack_box and self.player.rect.colliderect(attack_box):
                    damage = enemy.get_attack_damage()
                    self._try_damage_player(damage)

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
                play_sound("boss_death")
                play_music("victory.wav")

        # Check projectile collisions
        for projectile in self.level.projectiles:
            if self.player.rect.colliderect(projectile.rect):
                if self._try_damage_player(projectile.damage):
                    projectile.kill()

        # Check attack hits (each enemy can only be hit once per attack)
        if self.player.attacking:
            attack_box = self.player.get_attack_hitbox()
            if attack_box:
                for enemy in self.level.enemies:
                    enemy_id = id(enemy)
                    if enemy_id not in self.player.enemies_hit_this_attack:
                        if attack_box.colliderect(enemy.rect):
                            damage = int(1 * self.player.damage_multiplier)
                            was_alive = enemy.health > 0
                            killed = enemy.take_damage(damage)
                            self.player.enemies_hit_this_attack.add(enemy_id)
                            if was_alive:
                                if killed:
                                    # Check if it's the boss
                                    if enemy == self.level.boss:
                                        play_sound("boss_hit")  # Boss has separate death sound
                                    else:
                                        play_sound("enemy_death")
                                else:
                                    # Enemy was hit but not killed
                                    if enemy == self.level.boss:
                                        play_sound("boss_hit")
                                    else:
                                        play_sound("hit")

        # Check death (fell off level)
        if self.player.rect.top > self.level.height + 100:
            self.player.take_damage(self.player.health)  # Instant death

        # Check game over
        if self.player.lives <= 0:
            self.state = GameState.GAME_OVER
            play_sound("game_over")
            stop_music()

        # Check level complete (touching unlocked exit)
        if self.level.exit_door and not self.level.exit_door.locked:
            if self.player.rect.colliderect(self.level.exit_door.rect):
                self.state = GameState.LEVEL_COMPLETE
                play_sound("level_complete")
                stop_music()

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
        title_rect = title.get_rect(center=(SCREEN_WIDTH // 2, 60))
        self.screen.blit(title, title_rect)

        subtitle = self.menu_font.render("A Pirate's Quest for Treasure", True, (50, 50, 50))
        sub_rect = subtitle.get_rect(center=(SCREEN_WIDTH // 2, 110))
        self.screen.blit(subtitle, sub_rect)

        # Level selection
        level_title = self.menu_font.render("Select Level (UP/DOWN):", True, BLACK)
        self.screen.blit(level_title, (SCREEN_WIDTH // 2 - 130, 150))

        for i, (_, name, _) in enumerate(self.available_levels):
            color = (255, 215, 0) if i == self.selected_level else WHITE
            prefix = "> " if i == self.selected_level else "  "
            level_text = self.menu_font.render(f"{prefix}{name}", True, color)
            self.screen.blit(level_text, (SCREEN_WIDTH // 2 - 150, 185 + i * 30))

        # Position prompts below level list
        prompt_y = 185 + len(self.available_levels) * 30 + 20

        start_text = self.menu_font.render("Press ENTER to Start", True, WHITE)
        start_rect = start_text.get_rect(center=(SCREEN_WIDTH // 2, prompt_y))
        self.screen.blit(start_text, start_rect)

        quit_text = self.menu_font.render("Press ESC to Quit", True, WHITE)
        quit_rect = quit_text.get_rect(center=(SCREEN_WIDTH // 2, prompt_y + 35))
        self.screen.blit(quit_text, quit_rect)

        # Controls - bottom left
        controls = [
            "Controls:",
            "Arrow Keys / WASD - Move",
            "Space / W / Up - Jump",
            "Q - Attack | E - Cannon (if equipped)",
            "Double-tap Left/Right - Barrel Roll",
            "Down (in air) - Anchor Slam",
        ]
        for i, line in enumerate(controls):
            text = self.menu_font.render(line, True, (30, 30, 30))
            self.screen.blit(text, (50, 430 + i * 25))

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

        # Draw monkey companion
        if self.monkey and self.player.has_monkey:
            self.monkey.draw(self.screen, offset)

        # Draw player projectiles
        for proj in self.player_projectiles:
            if hasattr(proj, 'draw'):
                proj.draw(self.screen, offset)
            else:
                draw_rect = proj.rect.move(-offset[0], -offset[1])
                self.screen.blit(proj.image, draw_rect)

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
        boss_text = self.menu_font.render("Vice-Admiral Garp Defeated!", True, WHITE)
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
        if self.player.rolling:
            combat.append(f"rolling({self.player.roll_timer})")
        if self.player.slamming:
            combat.append("slamming")
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
