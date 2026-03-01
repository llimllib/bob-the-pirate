"""Enemy classes for British naval forces."""

import math
import os
import random

import pygame

from game.animation import AnimatedSprite, Animation, SpriteSheet, create_placeholder_frames
from game.settings import (
    ADMIRAL_ATTACK_COOLDOWN,
    ADMIRAL_CHARGE_SPEED,
    ADMIRAL_HEALTH,
    ADMIRAL_HEIGHT,
    ADMIRAL_PHASE_2_THRESHOLD,
    ADMIRAL_PHASE_3_THRESHOLD,
    ADMIRAL_SPEED,
    ADMIRAL_SUMMON_COOLDOWN,
    ADMIRAL_SWORD_FRAME_WIDTH,
    ADMIRAL_WIDTH,
    BLUE,
    BOSUN_ATTACK_COOLDOWN,
    BOSUN_CHARGE_SPEED,
    BOSUN_HEALTH,
    BOSUN_HEIGHT,
    BOSUN_SPEED,
    BOSUN_STOMP_DAMAGE,
    BOSUN_WIDTH,
    CANNON_SHOOT_COOLDOWN,
    CANNONBALL_GRAVITY,
    CANNONBALL_SPEED,
    MUSKETEER_HEALTH,
    MUSKETEER_SHOOT_COOLDOWN,
    OFFICER_HEALTH,
    OFFICER_SPEED,
    PROJECTILE_SPEED,
    SAILOR_HEALTH,
    SAILOR_SPEED,
    WHITE,
    YELLOW,
)

# Enemy sprite dimensions (larger for better visibility)
SAILOR_WIDTH = 36
SAILOR_HEIGHT = 56
MUSKETEER_WIDTH = 36
MUSKETEER_HEIGHT = 56
OFFICER_WIDTH = 40
OFFICER_HEIGHT = 60
CANNON_SIZE = 40

# Stun duration after being hit (prevents enemy from damaging player)
ENEMY_HIT_STUN_FRAMES = 30  # 0.5 seconds at 60 FPS

# Sprite sheet layout info
ENEMIES_SPRITE_PATH = "assets/sprites/enemies.png"
PROJECTILES_SPRITE_PATH = "assets/sprites/projectiles.png"

# Cached sprite sheet
_enemy_sheet: SpriteSheet | None = None
_projectile_sheet: SpriteSheet | None = None


def get_enemy_sheet() -> SpriteSheet | None:
    """Get cached enemy sprite sheet, loading if necessary."""
    global _enemy_sheet
    if _enemy_sheet is None and os.path.exists(ENEMIES_SPRITE_PATH):
        _enemy_sheet = SpriteSheet(ENEMIES_SPRITE_PATH)
    return _enemy_sheet


def get_projectile_sheet() -> SpriteSheet | None:
    """Get cached projectile sprite sheet, loading if necessary."""
    global _projectile_sheet
    if _projectile_sheet is None and os.path.exists(PROJECTILES_SPRITE_PATH):
        _projectile_sheet = SpriteSheet(PROJECTILES_SPRITE_PATH)
    return _projectile_sheet


class Enemy(pygame.sprite.Sprite):
    """Base class for all enemies."""

    def __init__(self, x: int, y: int, width: int, height: int, health: int, color: tuple):
        super().__init__()
        self.image = pygame.Surface((width, height))
        self.image.fill(color)
        self.rect = self.image.get_rect(topleft=(x, y))

        self.health = health
        self.max_health = health
        self.velocity_x = 0
        self.velocity_y = 0
        self.facing_right = True
        self.active = True

        # Stun timer - when > 0, enemy cannot damage the player
        self.hit_stun_timer = 0

    def take_damage(self, amount: int = 1) -> bool:
        """Take damage. Returns True if enemy died."""
        self.health -= amount
        self.hit_stun_timer = ENEMY_HIT_STUN_FRAMES  # Stun on hit
        if self.health <= 0:
            self.die()
            return True
        return False

    def can_damage_player(self) -> bool:
        """Check if enemy can currently damage the player."""
        return self.hit_stun_timer <= 0

    def update_stun(self) -> None:
        """Update stun timer. Call this in subclass update methods."""
        if self.hit_stun_timer > 0:
            self.hit_stun_timer -= 1

    def die(self) -> None:
        """Handle enemy death."""
        self.active = False
        self.kill()

    def update(self, player_rect: pygame.Rect = None) -> None:
        """Update enemy state. Override in subclasses."""
        pass

    def draw(self, surface: pygame.Surface, camera_offset: tuple[int, int] = (0, 0)) -> None:
        """Draw the enemy."""
        if not self.active:
            return
        draw_rect = self.rect.move(-camera_offset[0], -camera_offset[1])
        surface.blit(self.image, draw_rect)


class Sailor(Enemy):
    """Basic patrol enemy - walks back and forth."""

    def __init__(self, x: int, y: int, patrol_distance: int = 100):
        super().__init__(x, y, SAILOR_WIDTH, SAILOR_HEIGHT, SAILOR_HEALTH, BLUE)
        self.start_x = x
        self.patrol_distance = patrol_distance
        self.velocity_x = SAILOR_SPEED

        # Set up animated sprite
        self.sprite = AnimatedSprite()
        self._load_animations()
        self.sprite.play("walk")

        # Hurt state
        self.hurt_timer = 0

    def _load_animations(self) -> None:
        """Load Sailor animations from sprite sheet or use placeholders."""
        sheet = get_enemy_sheet()

        if sheet:
            # Row 0: Walk (2 frames @ 28px), Hurt (1 frame @ 28px)
            walk_frames = sheet.get_strip(0, SAILOR_WIDTH, SAILOR_HEIGHT, 2)
            self.sprite.add_animation("walk", Animation(walk_frames, frame_duration=10, loop=True))

            hurt_frames = sheet.get_strip(0, SAILOR_WIDTH, SAILOR_HEIGHT, 1, x_start=SAILOR_WIDTH * 2)
            self.sprite.add_animation("hurt", Animation(hurt_frames, frame_duration=1, loop=False))
        else:
            # Placeholder animations
            walk_frames = create_placeholder_frames(SAILOR_WIDTH, SAILOR_HEIGHT, BLUE, 2, "walk")
            self.sprite.add_animation("walk", Animation(walk_frames, frame_duration=10, loop=True))

            hurt_frames = create_placeholder_frames(SAILOR_WIDTH, SAILOR_HEIGHT, (100, 100, 200), 1, "hurt")
            self.sprite.add_animation("hurt", Animation(hurt_frames, frame_duration=1, loop=False))

    def take_damage(self, amount: int = 1) -> bool:
        """Take damage with hurt animation."""
        self.hurt_timer = 15
        self.sprite.play("hurt", force_restart=True)
        return super().take_damage(amount)

    def update(self, player_rect: pygame.Rect = None) -> None:
        """Patrol back and forth."""
        self.update_stun()

        # Update hurt timer
        if self.hurt_timer > 0:
            self.hurt_timer -= 1
            if self.hurt_timer <= 0:
                self.sprite.play("walk")

        self.rect.x += self.velocity_x

        # Reverse at patrol boundaries
        if self.rect.x > self.start_x + self.patrol_distance:
            self.velocity_x = -SAILOR_SPEED
            self.facing_right = False
        elif self.rect.x < self.start_x:
            self.velocity_x = SAILOR_SPEED
            self.facing_right = True

        # Update animation
        self.sprite.facing_right = self.facing_right
        self.sprite.update()
        self.image = self.sprite.get_frame()


class Musketeer(Enemy):
    """Ranged enemy - stands still and shoots."""

    # Shooting animation timing
    SHOOT_WIND_UP = 20  # Frames before firing
    SHOOT_FOLLOW_THROUGH = 15  # Frames after firing

    def __init__(self, x: int, y: int, projectile_group: pygame.sprite.Group):
        super().__init__(x, y, MUSKETEER_WIDTH, MUSKETEER_HEIGHT, MUSKETEER_HEALTH, (150, 0, 0))
        self.projectile_group = projectile_group
        self.shoot_cooldown = MUSKETEER_SHOOT_COOLDOWN
        self.shoot_timer = self.shoot_cooldown

        # Shooting state
        self.shooting = False
        self.shoot_anim_timer = 0
        self.fired_shot = False

        # Set up animated sprite
        self.sprite = AnimatedSprite()
        self._load_animations()
        self.sprite.play("idle")

    def _load_animations(self) -> None:
        """Load Musketeer animations from sprite sheet or use placeholders."""
        sheet = get_enemy_sheet()

        if sheet:
            # Row 1 (y=44): Idle (28px), Shoot frame 0 (28px), Shoot frame 1 with flash (36px)
            row_y = SAILOR_HEIGHT  # Row 1 starts after sailor row

            idle_frames = sheet.get_strip(row_y, MUSKETEER_WIDTH, MUSKETEER_HEIGHT, 1)
            self.sprite.add_animation("idle", Animation(idle_frames, frame_duration=1, loop=False))

            # Shoot animation: aim then fire with flash (10px wider)
            shoot_flash_width = MUSKETEER_WIDTH + 10
            shoot_frame_0 = sheet.get_frame(MUSKETEER_WIDTH, row_y, MUSKETEER_WIDTH, MUSKETEER_HEIGHT)
            shoot_frame_1 = sheet.get_frame(MUSKETEER_WIDTH * 2, row_y, shoot_flash_width, MUSKETEER_HEIGHT)
            shoot_frames = [shoot_frame_0, shoot_frame_1]
            self.sprite.add_animation("shoot", Animation(shoot_frames, frame_duration=15, loop=False))
        else:
            # Placeholder animations
            idle_frames = create_placeholder_frames(MUSKETEER_WIDTH, MUSKETEER_HEIGHT, (150, 0, 0), 1, "idle")
            self.sprite.add_animation("idle", Animation(idle_frames, frame_duration=1, loop=False))

            shoot_frames = create_placeholder_frames(MUSKETEER_WIDTH, MUSKETEER_HEIGHT, (200, 50, 0), 2, "shoot")
            self.sprite.add_animation("shoot", Animation(shoot_frames, frame_duration=15, loop=False))

    def update(self, player_rect: pygame.Rect = None) -> None:
        """Face player and shoot periodically."""
        self.update_stun()

        if player_rect:
            self.facing_right = player_rect.centerx > self.rect.centerx

        # Handle shooting animation state
        if self.shooting:
            self.shoot_anim_timer -= 1

            # Fire the actual projectile at the right moment
            if not self.fired_shot and self.shoot_anim_timer <= self.SHOOT_FOLLOW_THROUGH:
                self._fire_projectile()
                self.fired_shot = True

            # End shooting animation
            if self.shoot_anim_timer <= 0:
                self.shooting = False
                self.sprite.play("idle")
        else:
            self.shoot_timer -= 1
            if self.shoot_timer <= 0:
                self.shoot()
                self.shoot_timer = self.shoot_cooldown

        # Update animation
        self.sprite.facing_right = self.facing_right
        self.sprite.update()
        self.image = self.sprite.get_frame()

    def shoot(self) -> None:
        """Start shooting animation."""
        self.shooting = True
        self.shoot_anim_timer = self.SHOOT_WIND_UP + self.SHOOT_FOLLOW_THROUGH
        self.fired_shot = False
        self.sprite.play("shoot", force_restart=True)

    def _fire_projectile(self) -> None:
        """Fire a musket ball."""
        direction = 1 if self.facing_right else -1
        ball = MusketBall(
            self.rect.centerx,
            self.rect.centery,
            direction
        )
        self.projectile_group.add(ball)

    def draw(self, surface: pygame.Surface, camera_offset: tuple[int, int] = (0, 0)) -> None:
        """Draw musketeer, handling wider shooting sprite."""
        if not self.active:
            return

        draw_x = self.rect.x - camera_offset[0]
        draw_y = self.rect.y - camera_offset[1]

        frame = self.sprite.get_frame()

        # Handle wider shooting sprite offset when facing left
        if self.shooting and frame.get_width() > MUSKETEER_WIDTH:
            extra_width = frame.get_width() - MUSKETEER_WIDTH
            if not self.facing_right:
                draw_x -= extra_width

        surface.blit(frame, (draw_x, draw_y))


class Officer(Enemy):
    """Aggressive enemy - chases and attacks player with sword."""

    # Attack frame widths: wind-up (32px), slash (48px)
    ATTACK_FRAME_WIDTHS = [32, 48]

    def __init__(self, x: int, y: int):
        super().__init__(x, y, OFFICER_WIDTH, OFFICER_HEIGHT, OFFICER_HEALTH, (0, 0, 150))
        self.chase_range = 250
        self.attack_range = 45
        self.attacking = False
        self.attack_timer = 0
        self.attack_cooldown = 0
        self.attack_duration = 20
        self.cooldown_duration = 40

        # Set up animated sprite
        self.sprite = AnimatedSprite()
        self._load_animations()
        self.sprite.play("walk")

    def _load_animations(self) -> None:
        """Load Officer animations from sprite sheet or use placeholders."""
        sheet = get_enemy_sheet()

        if sheet:
            # Row 2 (y=88): Walk (2 frames @ 32px), Attack wind-up (32px), Attack slash (48px)
            row_y = SAILOR_HEIGHT + MUSKETEER_HEIGHT  # Row 2

            walk_frames = sheet.get_strip(row_y, OFFICER_WIDTH, OFFICER_HEIGHT, 2)
            self.sprite.add_animation("walk", Animation(walk_frames, frame_duration=10, loop=True))

            # Attack frames: wind-up + slash (20px wider for sword)
            attack_slash_width = OFFICER_WIDTH + 20
            attack_frame_0 = sheet.get_frame(OFFICER_WIDTH * 2, row_y, OFFICER_WIDTH, OFFICER_HEIGHT)
            attack_frame_1 = sheet.get_frame(OFFICER_WIDTH * 3, row_y, attack_slash_width, OFFICER_HEIGHT)
            attack_frames = [attack_frame_0, attack_frame_1]
            self.sprite.add_animation("attack", Animation(attack_frames, frame_duration=10, loop=False))

            # Idle uses first walk frame
            idle_frames = [walk_frames[0]]
            self.sprite.add_animation("idle", Animation(idle_frames, frame_duration=1, loop=False))
        else:
            # Placeholder animations
            walk_frames = create_placeholder_frames(OFFICER_WIDTH, OFFICER_HEIGHT, (0, 0, 150), 2, "walk")
            self.sprite.add_animation("walk", Animation(walk_frames, frame_duration=10, loop=True))

            attack_frames = create_placeholder_frames(OFFICER_WIDTH, OFFICER_HEIGHT, (100, 0, 200), 2, "attack")
            self.sprite.add_animation("attack", Animation(attack_frames, frame_duration=10, loop=False))

            idle_frames = [walk_frames[0]]
            self.sprite.add_animation("idle", Animation(idle_frames, frame_duration=1, loop=False))

    def update(self, player_rect: pygame.Rect = None) -> None:
        """Chase player if in range, attack when close."""
        self.update_stun()

        if not player_rect:
            return

        # Update attack timers
        if self.attacking:
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.attacking = False
                self.attack_cooldown = self.cooldown_duration
                self.sprite.play("idle")
        elif self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        distance_x = player_rect.centerx - self.rect.centerx
        distance_y = abs(player_rect.centery - self.rect.centery)
        distance = abs(distance_x)

        # Face player
        self.facing_right = distance_x > 0

        # Only chase if player is roughly at same height
        if distance_y > 100:
            self.velocity_x = 0
            if not self.attacking:
                self.sprite.play("idle")
            self._update_animation()
            return

        if distance < self.attack_range and not self.attacking and self.attack_cooldown <= 0:
            # Attack!
            self.attacking = True
            self.attack_timer = self.attack_duration
            self.velocity_x = 0
            self.sprite.play("attack", force_restart=True)
        elif distance < self.chase_range and distance > self.attack_range - 10:
            # Chase player
            if distance_x > 0:
                self.velocity_x = OFFICER_SPEED
            else:
                self.velocity_x = -OFFICER_SPEED
            self.rect.x += self.velocity_x
            if not self.attacking:
                self.sprite.play("walk")
        else:
            self.velocity_x = 0
            if not self.attacking:
                self.sprite.play("idle")

        self._update_animation()

    def _update_animation(self) -> None:
        """Update animation state."""
        self.sprite.facing_right = self.facing_right
        self.sprite.update()
        self.image = self.sprite.get_frame()

    def get_attack_hitbox(self) -> pygame.Rect | None:
        """Get the attack hitbox when attacking."""
        if not self.attacking:
            return None

        # Only active during the slash frame (second half of attack)
        if self.attack_timer > self.attack_duration // 2:
            return None

        if self.facing_right:
            return pygame.Rect(self.rect.right, self.rect.top + 10, 35, 30)
        else:
            return pygame.Rect(self.rect.left - 35, self.rect.top + 10, 35, 30)

    def draw(self, surface: pygame.Surface, camera_offset: tuple[int, int] = (0, 0)) -> None:
        """Draw the officer with attack animation and indicator."""
        if not self.active:
            return

        draw_x = self.rect.x - camera_offset[0]
        draw_y = self.rect.y - camera_offset[1]

        frame = self.sprite.get_frame()

        # Handle wider attack sprite offset when facing left
        if self.attacking and frame.get_width() > OFFICER_WIDTH:
            extra_width = frame.get_width() - OFFICER_WIDTH
            if not self.facing_right:
                draw_x -= extra_width

        surface.blit(frame, (draw_x, draw_y))


class Cannon(Enemy):
    """Stationary cannon that fires arcing cannonballs."""

    # Firing animation timing
    FIRE_DURATION = 20

    def __init__(self, x: int, y: int, projectile_group: pygame.sprite.Group, faces_right: bool = True):
        super().__init__(x, y, CANNON_SIZE, CANNON_SIZE, 2, (50, 50, 50))
        self.projectile_group = projectile_group
        self.faces_right = faces_right
        self.facing_right = faces_right
        self.shoot_cooldown = CANNON_SHOOT_COOLDOWN
        self.shoot_timer = self.shoot_cooldown

        # Firing animation state
        self.firing = False
        self.fire_timer = 0
        self.fired_shot = False

        # Set up animated sprite
        self.sprite = AnimatedSprite()
        self._load_animations()
        self.sprite.play("static")

    def _load_animations(self) -> None:
        """Load Cannon animations from sprite sheet or use placeholders."""
        sheet = get_enemy_sheet()

        if sheet:
            # Row 3 (y=136): Static (32px), Fire frame 0 (40px), Fire frame 1 (40px)
            row_y = SAILOR_HEIGHT + MUSKETEER_HEIGHT + OFFICER_HEIGHT  # Row 3

            static_frames = sheet.get_strip(row_y, CANNON_SIZE, CANNON_SIZE, 1)
            self.sprite.add_animation("static", Animation(static_frames, frame_duration=1, loop=False))

            # Fire animation (wider frames with effects, 10px wider)
            fire_width = CANNON_SIZE + 10
            fire_frame_0 = sheet.get_frame(CANNON_SIZE, row_y, fire_width, CANNON_SIZE)
            fire_frame_1 = sheet.get_frame(CANNON_SIZE + fire_width, row_y, fire_width, CANNON_SIZE)
            fire_frames = [fire_frame_0, fire_frame_1]
            self.sprite.add_animation("fire", Animation(fire_frames, frame_duration=10, loop=False))
        else:
            # Placeholder animations
            static_frames = create_placeholder_frames(CANNON_SIZE, CANNON_SIZE, (50, 50, 50), 1, "static")
            self.sprite.add_animation("static", Animation(static_frames, frame_duration=1, loop=False))

            fire_frames = create_placeholder_frames(CANNON_SIZE, CANNON_SIZE, (100, 50, 0), 2, "fire")
            self.sprite.add_animation("fire", Animation(fire_frames, frame_duration=10, loop=False))

    def update(self, player_rect: pygame.Rect = None) -> None:
        """Fire cannonballs periodically."""
        self.update_stun()

        # Handle firing animation
        if self.firing:
            self.fire_timer -= 1

            # Fire the actual projectile at the start
            if not self.fired_shot and self.fire_timer == self.FIRE_DURATION - 2:
                self._fire_projectile()
                self.fired_shot = True

            # End firing animation
            if self.fire_timer <= 0:
                self.firing = False
                self.sprite.play("static")
        else:
            self.shoot_timer -= 1
            if self.shoot_timer <= 0:
                self.shoot()
                self.shoot_timer = self.shoot_cooldown

        # Update animation
        self.sprite.facing_right = self.facing_right
        self.sprite.update()
        self.image = self.sprite.get_frame()

    def shoot(self) -> None:
        """Start firing animation."""
        self.firing = True
        self.fire_timer = self.FIRE_DURATION
        self.fired_shot = False
        self.sprite.play("fire", force_restart=True)

    def _fire_projectile(self) -> None:
        """Fire a cannonball with arc."""
        direction = 1 if self.faces_right else -1
        ball = Cannonball(
            self.rect.centerx,
            self.rect.centery - 5,
            direction
        )
        self.projectile_group.add(ball)

    def draw(self, surface: pygame.Surface, camera_offset: tuple[int, int] = (0, 0)) -> None:
        """Draw cannon, handling wider firing sprite."""
        if not self.active:
            return

        draw_x = self.rect.x - camera_offset[0]
        draw_y = self.rect.y - camera_offset[1]

        frame = self.sprite.get_frame()

        # Handle wider firing sprite offset when facing left
        if self.firing and frame.get_width() > CANNON_SIZE:
            extra_width = frame.get_width() - CANNON_SIZE
            if not self.facing_right:
                draw_x -= extra_width

        surface.blit(frame, (draw_x, draw_y))


class Bosun(Enemy):
    """
    Miniboss enemy - The ship's Bosun, a tough disciplinarian.

    Attacks:
    - Melee whip attack (short range)
    - Ground stomp (shockwave)
    - Charge attack

    Has a health bar displayed above.
    """

    # States
    STATE_IDLE = "idle"
    STATE_WALK = "walk"
    STATE_WHIP_ATTACK = "whip"
    STATE_STOMP = "stomp"
    STATE_CHARGE = "charge"
    STATE_STUNNED = "stunned"

    def __init__(self, x: int, y: int):
        super().__init__(x, y, BOSUN_WIDTH, BOSUN_HEIGHT, BOSUN_HEALTH, (100, 60, 40))

        # AI state
        self.state = self.STATE_IDLE
        self.state_timer = 60
        self.attack_cooldown = 0

        # Charge attack
        self.charge_direction = 0

        # Arena bounds (set by level or defaults)
        self.arena_left = x - 200
        self.arena_right = x + 200

        # Damage flash
        self.damage_flash = 0

        # Set up animations
        self.sprite = AnimatedSprite()
        self._load_animations()
        self.sprite.play("idle")
        self.image = self.sprite.get_frame()

    def _load_animations(self) -> None:
        """Load Bosun animations from sprite sheet or placeholders."""
        sprite_path = "assets/sprites/bosun.png"

        if os.path.exists(sprite_path):
            sheet = SpriteSheet(sprite_path)

            # Row 0: Idle (2 frames)
            idle_frames = sheet.get_strip(0, BOSUN_WIDTH, BOSUN_HEIGHT, 2)
            self.sprite.add_animation("idle", Animation(idle_frames, frame_duration=20, loop=True))

            # Row 1: Walk (4 frames)
            walk_frames = sheet.get_strip(BOSUN_HEIGHT, BOSUN_WIDTH, BOSUN_HEIGHT, 4)
            self.sprite.add_animation("walk", Animation(walk_frames, frame_duration=10, loop=True))

            # Row 2: Charge (2 frames)
            charge_frames = sheet.get_strip(BOSUN_HEIGHT * 2, BOSUN_WIDTH, BOSUN_HEIGHT, 2)
            self.sprite.add_animation("charge", Animation(charge_frames, frame_duration=6, loop=True))

            # Row 3: Axe Attack (3 frames)
            attack_frames = sheet.get_strip(BOSUN_HEIGHT * 3, BOSUN_WIDTH, BOSUN_HEIGHT, 3)
            self.sprite.add_animation("attack", Animation(attack_frames, frame_duration=8, loop=False))

            # Row 4: Stomp (2 frames)
            stomp_frames = sheet.get_strip(BOSUN_HEIGHT * 4, BOSUN_WIDTH, BOSUN_HEIGHT, 2)
            self.sprite.add_animation("stomp", Animation(stomp_frames, frame_duration=12, loop=False))

            # Row 5: Hurt (1 frame)
            hurt_frames = sheet.get_strip(BOSUN_HEIGHT * 5, BOSUN_WIDTH, BOSUN_HEIGHT, 1)
            self.sprite.add_animation("hurt", Animation(hurt_frames, frame_duration=10, loop=False))
        else:
            self._load_placeholder_animations()

    def _load_placeholder_animations(self) -> None:
        """Create placeholder animations for Bosun."""
        color = (100, 60, 40)  # Dark brown

        idle_frames = create_placeholder_frames(BOSUN_WIDTH, BOSUN_HEIGHT, color, 2, "idle")
        self.sprite.add_animation("idle", Animation(idle_frames, frame_duration=20, loop=True))

        walk_frames = create_placeholder_frames(BOSUN_WIDTH, BOSUN_HEIGHT, color, 4, "walk")
        self.sprite.add_animation("walk", Animation(walk_frames, frame_duration=10, loop=True))

        charge_frames = create_placeholder_frames(BOSUN_WIDTH, BOSUN_HEIGHT, (150, 60, 40), 2, "chrg")
        self.sprite.add_animation("charge", Animation(charge_frames, frame_duration=6, loop=True))

        attack_frames = create_placeholder_frames(BOSUN_WIDTH, BOSUN_HEIGHT, (150, 80, 40), 3, "atk")
        self.sprite.add_animation("attack", Animation(attack_frames, frame_duration=8, loop=False))

        stomp_frames = create_placeholder_frames(BOSUN_WIDTH, BOSUN_HEIGHT, (120, 60, 60), 2, "stmp")
        self.sprite.add_animation("stomp", Animation(stomp_frames, frame_duration=12, loop=False))

        hurt_frames = create_placeholder_frames(BOSUN_WIDTH, BOSUN_HEIGHT, (180, 80, 80), 1, "hurt")
        self.sprite.add_animation("hurt", Animation(hurt_frames, frame_duration=10, loop=False))

    def _update_animation(self) -> None:
        """Update which animation should be playing based on state."""
        if self.damage_flash > 0:
            self.sprite.play("hurt")
        elif self.state == self.STATE_CHARGE:
            self.sprite.play("charge")
        elif self.state == self.STATE_WHIP_ATTACK:
            self.sprite.play("attack")
        elif self.state == self.STATE_STOMP:
            self.sprite.play("stomp")
        elif self.state == self.STATE_WALK:
            self.sprite.play("walk")
        else:
            self.sprite.play("idle")

        self.sprite.facing_right = self.facing_right
        self.sprite.update()
        self.image = self.sprite.get_frame()

    def set_arena_bounds(self, left: int, right: int) -> None:
        """Set the arena boundaries for the miniboss."""
        self.arena_left = left
        self.arena_right = right

    def take_damage(self, amount: int = 1) -> bool:
        """Take damage with brief stun."""
        result = super().take_damage(amount)
        if not result:
            self.damage_flash = 10
            # Brief stun when hit
            if self.state != self.STATE_STUNNED:
                self.state = self.STATE_STUNNED
                self.state_timer = 20
        return result

    def update(self, player_rect: pygame.Rect = None) -> None:
        """Update miniboss AI."""
        self.update_stun()

        if not player_rect:
            return

        # Update timers
        if self.damage_flash > 0:
            self.damage_flash -= 1
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        self.state_timer -= 1

        # Face player (unless charging)
        if self.state != self.STATE_CHARGE:
            self.facing_right = player_rect.centerx > self.rect.centerx

        # State machine
        if self.state == self.STATE_STUNNED:
            if self.state_timer <= 0:
                self._choose_next_action(player_rect)

        elif self.state == self.STATE_IDLE:
            if self.state_timer <= 0:
                self._choose_next_action(player_rect)

        elif self.state == self.STATE_WALK:
            self._do_walk(player_rect)
            if self.state_timer <= 0:
                self._choose_next_action(player_rect)

        elif self.state == self.STATE_WHIP_ATTACK:
            if self.state_timer <= 0:
                self.state = self.STATE_IDLE
                self.state_timer = 20
                self.attack_cooldown = BOSUN_ATTACK_COOLDOWN

        elif self.state == self.STATE_STOMP:
            if self.state_timer <= 0:
                self.state = self.STATE_IDLE
                self.state_timer = 30
                self.attack_cooldown = BOSUN_ATTACK_COOLDOWN * 2

        elif self.state == self.STATE_CHARGE:
            self._do_charge()
            if self.state_timer <= 0:
                self.state = self.STATE_STUNNED
                self.state_timer = 30  # Recovery after charge
                self.attack_cooldown = BOSUN_ATTACK_COOLDOWN

        # Update animation based on current state
        self._update_animation()

    def _choose_next_action(self, player_rect: pygame.Rect) -> None:
        """Choose next action based on distance to player."""
        distance = abs(player_rect.centerx - self.rect.centerx)

        if self.attack_cooldown > 0:
            self.state = self.STATE_WALK
            self.state_timer = 45
            return

        # Close range: whip attack
        if distance < 60:
            self.state = self.STATE_WHIP_ATTACK
            self.state_timer = 25
            return

        # Medium range: stomp (ground shockwave)
        if distance < 150 and random.random() < 0.3:
            self.state = self.STATE_STOMP
            self.state_timer = 40
            return

        # Far range: charge
        if distance > 100 and random.random() < 0.4:
            self.state = self.STATE_CHARGE
            self.state_timer = 50
            self.charge_direction = 1 if self.facing_right else -1
            return

        # Default: walk toward player
        self.state = self.STATE_WALK
        self.state_timer = 40 + random.randint(0, 20)

    def _do_walk(self, player_rect: pygame.Rect) -> None:
        """Walk toward player."""
        if self.facing_right:
            self.rect.x += BOSUN_SPEED
        else:
            self.rect.x -= BOSUN_SPEED

        # Keep in arena bounds
        self.rect.x = max(self.arena_left, min(self.rect.x, self.arena_right - self.rect.width))

    def _do_charge(self) -> None:
        """Perform charge attack."""
        self.rect.x += BOSUN_CHARGE_SPEED * self.charge_direction

        # Stop at arena edges
        if self.rect.x <= self.arena_left or self.rect.x >= self.arena_right - self.rect.width:
            self.state_timer = 0

    def get_attack_hitbox(self) -> pygame.Rect | None:
        """Get attack hitbox for current attack."""
        if self.state == self.STATE_WHIP_ATTACK and 5 < self.state_timer < 20:
            # Whip has longer reach than sword
            if self.facing_right:
                return pygame.Rect(self.rect.right, self.rect.top + 15, 50, 30)
            else:
                return pygame.Rect(self.rect.left - 50, self.rect.top + 15, 50, 30)

        elif self.state == self.STATE_STOMP and 10 < self.state_timer < 25:
            # Stomp creates shockwave on both sides
            return pygame.Rect(
                self.rect.centerx - 80,
                self.rect.bottom - 20,
                160,
                20
            )

        elif self.state == self.STATE_CHARGE:
            return self.rect.inflate(10, 0)

        return None

    def get_attack_damage(self) -> int:
        """Get damage for current attack."""
        if self.state == self.STATE_STOMP:
            return BOSUN_STOMP_DAMAGE
        return 1

    def draw(self, surface: pygame.Surface, camera_offset: tuple[int, int] = (0, 0)) -> None:
        """Draw the Bosun with health bar and state indicators."""
        if not self.active:
            return

        draw_x = self.rect.x - camera_offset[0]
        draw_y = self.rect.y - camera_offset[1]

        # Flip sprite if facing left
        frame = self.image
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)

        # Flash white when damaged
        if self.damage_flash > 0 and self.damage_flash % 2 == 0:
            flash_surface = frame.copy()
            flash_surface.fill(WHITE)
            surface.blit(flash_surface, (draw_x, draw_y))
        else:
            surface.blit(frame, (draw_x, draw_y))

        # Draw health bar above
        bar_width = 50
        bar_height = 6
        bar_x = draw_x + (BOSUN_WIDTH - bar_width) // 2
        bar_y = draw_y - 12

        # Background
        pygame.draw.rect(surface, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height))
        # Health fill
        health_pct = self.health / self.max_health
        pygame.draw.rect(surface, (200, 50, 50), (bar_x, bar_y, int(bar_width * health_pct), bar_height))
        # Border
        pygame.draw.rect(surface, (0, 0, 0), (bar_x, bar_y, bar_width, bar_height), 1)

        # Draw attack indicators
        if self.state == self.STATE_WHIP_ATTACK and 5 < self.state_timer < 20:
            attack_box = self.get_attack_hitbox()
            if attack_box:
                attack_draw = attack_box.move(-camera_offset[0], -camera_offset[1])
                pygame.draw.rect(surface, (200, 100, 50), attack_draw, 2)

        elif self.state == self.STATE_STOMP and 10 < self.state_timer < 25:
            attack_box = self.get_attack_hitbox()
            if attack_box:
                attack_draw = attack_box.move(-camera_offset[0], -camera_offset[1])
                pygame.draw.rect(surface, (255, 200, 100), attack_draw, 3)

        elif self.state == self.STATE_CHARGE:
            draw_rect = pygame.Rect(draw_x, draw_y, BOSUN_WIDTH, BOSUN_HEIGHT)
            pygame.draw.rect(surface, (255, 100, 0), draw_rect.inflate(4, 4), 2)

        # Draw stunned stars
        if self.state == self.STATE_STUNNED:
            for i in range(2):
                angle = (pygame.time.get_ticks() / 200 + i * 3.14) % (2 * 3.14159)
                star_x = draw_x + BOSUN_WIDTH // 2 + int(15 * math.cos(angle))
                star_y = draw_y - 5 + int(3 * math.sin(angle * 2))
                pygame.draw.circle(surface, YELLOW, (star_x, star_y), 3)


class Projectile(pygame.sprite.Sprite):
    """Base class for projectiles."""

    def __init__(self, x: int, y: int, velocity_x: float, velocity_y: float,
                 width: int, height: int, color: tuple, damage: int = 1):
        super().__init__()
        self.base_width = width
        self.base_height = height
        self.image = pygame.Surface((width, height), pygame.SRCALPHA)
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))

        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.damage = damage
        self.active = True
        self.facing_right = velocity_x > 0

    def update(self) -> None:
        """Move projectile."""
        self.rect.x += int(self.velocity_x)
        self.rect.y += int(self.velocity_y)

        # Remove if off screen (handled by level)

    def draw(self, surface: pygame.Surface, camera_offset: tuple[int, int] = (0, 0)) -> None:
        """Draw the projectile."""
        draw_rect = self.rect.move(-camera_offset[0], -camera_offset[1])
        frame = self.image
        # Flip if moving left
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)
        surface.blit(frame, draw_rect)


class MusketBall(Projectile):
    """Fast, straight-flying projectile from Musketeers."""

    def __init__(self, x: int, y: int, direction: int):
        super().__init__(
            x, y,
            PROJECTILE_SPEED * direction, 0,
            8, 8, WHITE, 1
        )
        self._load_sprite()

    def _load_sprite(self) -> None:
        """Load musket ball sprite."""
        sheet = get_projectile_sheet()
        if sheet:
            # Musket ball is at x=0, 8x8
            self.image = sheet.get_frame(0, 2, 8, 8)  # y=2 to center in 12px height


class Cannonball(Projectile):
    """Arcing projectile from Cannons."""

    def __init__(self, x: int, y: int, direction: int):
        super().__init__(
            x, y,
            CANNONBALL_SPEED * direction, -8,
            12, 12, (30, 30, 30), 2
        )
        self.gravity = CANNONBALL_GRAVITY
        self._load_sprite()

    def _load_sprite(self) -> None:
        """Load cannonball sprite."""
        sheet = get_projectile_sheet()
        if sheet:
            # Cannonball is at x=12 (after 8px ball + 4px padding), 12x12
            self.image = sheet.get_frame(12, 0, 12, 12)

    def update(self) -> None:
        """Move with gravity arc."""
        self.velocity_y += self.gravity
        super().update()


class Admiral(Enemy):
    """Boss enemy - Vice-Admiral Garp with multiple attack phases."""

    # Attack states
    STATE_IDLE = "idle"
    STATE_WALK = "walk"
    STATE_SWORD_ATTACK = "sword"
    STATE_PISTOL_SHOT = "pistol"
    STATE_CHARGE = "charge"
    STATE_SUMMON = "summon"
    STATE_STUNNED = "stunned"

    def __init__(self, x: int, y: int, projectile_group: pygame.sprite.Group):
        super().__init__(x, y, ADMIRAL_WIDTH, ADMIRAL_HEIGHT, ADMIRAL_HEALTH, (139, 0, 0))
        self.projectile_group = projectile_group

        # Set up animated sprite
        self.sprite = AnimatedSprite()
        self._load_animations()
        self.sprite.play("idle")

        # AI state
        self.state = self.STATE_IDLE
        self.state_timer = 60  # Start with brief idle
        self.phase = 1

        # Attack cooldowns
        self.attack_cooldown = 0
        self.summon_cooldown = ADMIRAL_SUMMON_COOLDOWN

        # Movement
        self.start_x = x
        self.arena_left = x - 200
        self.arena_right = x + 200

        # Charge attack
        self.charge_direction = 0

        # Track if we need to spawn sailors (handled by game)
        self.summon_pending = False

        # For invincibility flash
        self.damage_flash = 0

    def _load_animations(self) -> None:
        """Load Admiral animations from sprite sheet or use placeholders."""
        sprite_path = "assets/sprites/admiral.png"

        if os.path.exists(sprite_path):
            sheet = SpriteSheet(sprite_path)

            # Row 0: Idle (2 frames), Walk (2 frames)
            idle_frames = sheet.get_strip(0, ADMIRAL_WIDTH, ADMIRAL_HEIGHT, 2)
            self.sprite.add_animation("idle", Animation(idle_frames, frame_duration=30, loop=True))

            walk_frames = sheet.get_strip(0, ADMIRAL_WIDTH, ADMIRAL_HEIGHT, 2, x_start=ADMIRAL_WIDTH * 2)
            self.sprite.add_animation("walk", Animation(walk_frames, frame_duration=12, loop=True))

            # Row 1: Sword attack (3 frames with variable widths: 48, 70, 48)
            attack_y = ADMIRAL_HEIGHT
            attack_frame_0 = sheet.sheet.subsurface((0, attack_y, ADMIRAL_WIDTH, ADMIRAL_HEIGHT))
            attack_frame_1 = sheet.sheet.subsurface((ADMIRAL_WIDTH, attack_y, ADMIRAL_SWORD_FRAME_WIDTH, ADMIRAL_HEIGHT))
            attack_frame_2 = sheet.sheet.subsurface((ADMIRAL_WIDTH + ADMIRAL_SWORD_FRAME_WIDTH, attack_y, ADMIRAL_WIDTH, ADMIRAL_HEIGHT))
            sword_frames = [attack_frame_0, attack_frame_1, attack_frame_2]
            self.sprite.add_animation("sword", Animation(sword_frames, frame_duration=8, loop=False))

            # Row 2: Pistol (2 frames), Charge, Stunned
            row2_y = ADMIRAL_HEIGHT * 2
            pistol_frames = sheet.get_strip(row2_y, ADMIRAL_WIDTH, ADMIRAL_HEIGHT, 2)
            self.sprite.add_animation("pistol", Animation(pistol_frames, frame_duration=15, loop=False))

            charge_frames = sheet.get_strip(row2_y, ADMIRAL_WIDTH, ADMIRAL_HEIGHT, 1, x_start=ADMIRAL_WIDTH * 2)
            self.sprite.add_animation("charge", Animation(charge_frames, frame_duration=1, loop=False))

            stunned_frames = sheet.get_strip(row2_y, ADMIRAL_WIDTH, ADMIRAL_HEIGHT, 1, x_start=ADMIRAL_WIDTH * 3)
            self.sprite.add_animation("stunned", Animation(stunned_frames, frame_duration=1, loop=False))

            # Summon uses idle animation
            self.sprite.add_animation("summon", Animation(idle_frames, frame_duration=10, loop=True))
        else:
            self._load_placeholder_animations()

    def _load_placeholder_animations(self) -> None:
        """Load placeholder colored rectangle animations."""
        dark_red = (139, 0, 0)

        idle_frames = create_placeholder_frames(ADMIRAL_WIDTH, ADMIRAL_HEIGHT, dark_red, 2, "idle")
        self.sprite.add_animation("idle", Animation(idle_frames, frame_duration=30, loop=True))

        walk_frames = create_placeholder_frames(ADMIRAL_WIDTH, ADMIRAL_HEIGHT, dark_red, 2, "walk")
        self.sprite.add_animation("walk", Animation(walk_frames, frame_duration=12, loop=True))

        sword_frames = create_placeholder_frames(ADMIRAL_WIDTH, ADMIRAL_HEIGHT, (200, 50, 50), 3, "sword")
        self.sprite.add_animation("sword", Animation(sword_frames, frame_duration=8, loop=False))

        pistol_frames = create_placeholder_frames(ADMIRAL_WIDTH, ADMIRAL_HEIGHT, (150, 100, 50), 2, "pistol")
        self.sprite.add_animation("pistol", Animation(pistol_frames, frame_duration=15, loop=False))

        charge_frames = create_placeholder_frames(ADMIRAL_WIDTH, ADMIRAL_HEIGHT, (255, 100, 0), 1, "charge")
        self.sprite.add_animation("charge", Animation(charge_frames, frame_duration=1, loop=False))

        stunned_frames = create_placeholder_frames(ADMIRAL_WIDTH, ADMIRAL_HEIGHT, (100, 100, 150), 1, "stunned")
        self.sprite.add_animation("stunned", Animation(stunned_frames, frame_duration=1, loop=False))

        self.sprite.add_animation("summon", Animation(idle_frames, frame_duration=10, loop=True))

    def _update_animation_state(self) -> None:
        """Update which animation should be playing based on state."""
        state_to_anim = {
            self.STATE_IDLE: "idle",
            self.STATE_WALK: "walk",
            self.STATE_SWORD_ATTACK: "sword",
            self.STATE_PISTOL_SHOT: "pistol",
            self.STATE_CHARGE: "charge",
            self.STATE_STUNNED: "stunned",
            self.STATE_SUMMON: "summon",
        }
        anim_name = state_to_anim.get(self.state, "idle")
        self.sprite.play(anim_name)
        self.sprite.facing_right = self.facing_right

    @property
    def current_phase(self) -> int:
        """Determine current phase based on health."""
        if self.health <= ADMIRAL_PHASE_3_THRESHOLD:
            return 3
        elif self.health <= ADMIRAL_PHASE_2_THRESHOLD:
            return 2
        return 1

    def take_damage(self, amount: int = 1) -> bool:
        """Take damage with phase change handling."""
        old_phase = self.current_phase
        result = super().take_damage(amount)

        if not result:
            self.damage_flash = 10
            new_phase = self.current_phase

            # Phase change - brief stun and change behavior
            if new_phase != old_phase:
                self.state = self.STATE_STUNNED
                self.state_timer = 60  # 1 second stun on phase change
                self.phase = new_phase

        return result

    def update(self, player_rect: pygame.Rect = None) -> None:
        """Update boss AI based on current phase."""
        if not player_rect:
            return

        # Update timers
        if self.damage_flash > 0:
            self.damage_flash -= 1
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.summon_cooldown > 0:
            self.summon_cooldown -= 1

        # State timer
        self.state_timer -= 1

        # Face player (unless charging)
        if self.state != self.STATE_CHARGE:
            self.facing_right = player_rect.centerx > self.rect.centerx

        # State machine
        if self.state == self.STATE_STUNNED:
            if self.state_timer <= 0:
                self._choose_next_action(player_rect)

        elif self.state == self.STATE_IDLE:
            if self.state_timer <= 0:
                self._choose_next_action(player_rect)

        elif self.state == self.STATE_WALK:
            self._do_walk(player_rect)
            if self.state_timer <= 0:
                self._choose_next_action(player_rect)

        elif self.state == self.STATE_SWORD_ATTACK:
            if self.state_timer <= 0:
                self.state = self.STATE_IDLE
                self.state_timer = 30
                self.attack_cooldown = ADMIRAL_ATTACK_COOLDOWN

        elif self.state == self.STATE_PISTOL_SHOT:
            if self.state_timer == 15:  # Fire at mid-point of animation
                self._fire_pistol()
            if self.state_timer <= 0:
                self.state = self.STATE_IDLE
                self.state_timer = 40
                self.attack_cooldown = ADMIRAL_ATTACK_COOLDOWN

        elif self.state == self.STATE_CHARGE:
            self._do_charge()
            if self.state_timer <= 0:
                self.state = self.STATE_STUNNED
                self.state_timer = 45  # Recovery time after charge
                self.attack_cooldown = ADMIRAL_ATTACK_COOLDOWN * 2

        elif self.state == self.STATE_SUMMON:
            if self.state_timer == 30:  # Summon at mid-point
                self.summon_pending = True
            if self.state_timer <= 0:
                self.state = self.STATE_IDLE
                self.state_timer = 60
                self.summon_cooldown = ADMIRAL_SUMMON_COOLDOWN

        # Update animation
        self._update_animation_state()
        self.sprite.update()
        self.image = self.sprite.get_frame()

    def _choose_next_action(self, player_rect: pygame.Rect) -> None:
        """Choose next action based on phase and distance to player."""
        distance = abs(player_rect.centerx - self.rect.centerx)

        # Can't attack if on cooldown
        if self.attack_cooldown > 0:
            self.state = self.STATE_WALK
            self.state_timer = 60
            return

        # Phase 3: More aggressive, can summon
        if self.phase == 3 and self.summon_cooldown <= 0 and random.random() < 0.3:
            self.state = self.STATE_SUMMON
            self.state_timer = 60
            return

        # Phase 2+: Can charge
        if self.phase >= 2 and distance > 150 and random.random() < 0.4:
            self.state = self.STATE_CHARGE
            self.state_timer = 60
            self.charge_direction = 1 if self.facing_right else -1
            return

        # Close range: sword attack
        if distance < 80:
            self.state = self.STATE_SWORD_ATTACK
            self.state_timer = 25
            return

        # Medium range: pistol shot
        if distance < 250 and random.random() < 0.5:
            self.state = self.STATE_PISTOL_SHOT
            self.state_timer = 30
            return

        # Default: walk toward player
        self.state = self.STATE_WALK
        self.state_timer = 45 + random.randint(0, 30)

    def _do_walk(self, player_rect: pygame.Rect) -> None:
        """Walk toward player."""
        if self.facing_right:
            self.rect.x += ADMIRAL_SPEED
        else:
            self.rect.x -= ADMIRAL_SPEED

        # Keep in arena bounds
        self.rect.x = max(self.arena_left, min(self.rect.x, self.arena_right))

    def _do_charge(self) -> None:
        """Perform charge attack."""
        self.rect.x += ADMIRAL_CHARGE_SPEED * self.charge_direction

        # Stop at arena edges
        if self.rect.x <= self.arena_left or self.rect.x >= self.arena_right:
            self.state_timer = 0  # End charge early

    def _fire_pistol(self) -> None:
        """Fire a pistol shot."""
        direction = 1 if self.facing_right else -1
        bullet = AdmiralBullet(
            self.rect.centerx + (30 * direction),
            self.rect.centery - 5,
            direction
        )
        self.projectile_group.add(bullet)

    def get_attack_hitbox(self) -> pygame.Rect:
        """Get attack hitbox for sword attack or charge."""
        if self.state == self.STATE_SWORD_ATTACK and 5 < self.state_timer < 20:
            if self.facing_right:
                return pygame.Rect(self.rect.right, self.rect.top + 15, 45, 35)
            else:
                return pygame.Rect(self.rect.left - 45, self.rect.top + 15, 45, 35)
        elif self.state == self.STATE_CHARGE:
            # Charge attack uses the body hitbox
            return self.rect.inflate(10, 0)
        return None

    def set_arena_bounds(self, left: int, right: int) -> None:
        """Set the arena boundaries for the boss."""
        self.arena_left = left
        self.arena_right = right

    def draw(self, surface: pygame.Surface, camera_offset: tuple[int, int] = (0, 0)) -> None:
        """Draw the Admiral with animated sprite and state indicators."""
        if not self.active:
            return

        draw_x = self.rect.x - camera_offset[0]
        draw_y = self.rect.y - camera_offset[1]

        # Get current animation frame
        frame = self.sprite.get_frame()

        # Handle wider attack sprite offset (like player)
        if self.state == self.STATE_SWORD_ATTACK and frame.get_width() > ADMIRAL_WIDTH:
            extra_width = frame.get_width() - ADMIRAL_WIDTH
            if not self.facing_right:
                draw_x -= extra_width

        # Flash white when damaged
        if self.damage_flash > 0 and self.damage_flash % 2 == 0:
            flash_surface = frame.copy()
            flash_surface.fill(WHITE)
            surface.blit(flash_surface, (draw_x, draw_y))
        else:
            surface.blit(frame, (draw_x, draw_y))

        # Draw attack effects (sword hitbox indicator)
        if self.state == self.STATE_SWORD_ATTACK and 5 < self.state_timer < 20:
            attack_box = self.get_attack_hitbox()
            if attack_box:
                attack_draw = attack_box.move(-camera_offset[0], -camera_offset[1])
                pygame.draw.rect(surface, (255, 255, 0), attack_draw, 3)

        # Draw charge indicator
        if self.state == self.STATE_CHARGE:
            draw_rect = self.rect.move(-camera_offset[0], -camera_offset[1])
            pygame.draw.rect(surface, (255, 100, 0), draw_rect.inflate(6, 6), 3)

        # Draw stunned indicator
        if self.state == self.STATE_STUNNED:
            draw_rect = self.rect.move(-camera_offset[0], -camera_offset[1])
            # Draw stars
            for i in range(3):
                angle = (pygame.time.get_ticks() / 200 + i * 2.1) % (2 * 3.14159)
                star_x = draw_rect.centerx + int(20 * math.cos(angle))
                star_y = draw_rect.top - 10 + int(5 * math.sin(angle * 2))
                pygame.draw.circle(surface, YELLOW, (star_x, star_y), 4)


class AdmiralBullet(Projectile):
    """Fast pistol shot from the Admiral."""

    def __init__(self, x: int, y: int, direction: int):
        super().__init__(
            x, y,
            PROJECTILE_SPEED * 1.2 * direction, 0,
            10, 10, (200, 150, 50), 1
        )
        self._load_sprite()

    def _load_sprite(self) -> None:
        """Load admiral bullet sprite."""
        sheet = get_projectile_sheet()
        if sheet:
            # Admiral bullet is at x=28 (after 8 + 4 + 12 + 4), 10x10
            self.image = sheet.get_frame(28, 1, 10, 10)  # y=1 to center in 12px height

    def draw(self, surface: pygame.Surface, camera_offset: tuple[int, int] = (0, 0)) -> None:
        """Draw bullet with trail effect."""
        draw_rect = self.rect.move(-camera_offset[0], -camera_offset[1])
        # Trail
        trail_dir = -1 if self.velocity_x > 0 else 1
        pygame.draw.line(
            surface, (255, 200, 100),
            (draw_rect.centerx, draw_rect.centery),
            (draw_rect.centerx + trail_dir * 15, draw_rect.centery),
            3
        )
        # Draw sprite
        frame = self.image
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)
        surface.blit(frame, draw_rect)


class GhostCaptain(Enemy):
    """
    Secret boss - Ghostly Pirate Captain with teleportation abilities.

    Attacks:
    - Spectral Slash - Long-range sword attack
    - Teleport - Disappears and reappears near player
    - Phase Mode - Briefly invulnerable while passing through player

    Very high health, the hardest boss in the game.
    """

    # States
    STATE_IDLE = "idle"
    STATE_WALK = "walk"
    STATE_SLASH = "slash"
    STATE_TELEPORT = "teleport"
    STATE_PHASE = "phase"
    STATE_STUNNED = "stunned"

    # Ghost colors
    GHOST_COLOR = (100, 150, 180)
    GHOST_GLOW = (150, 200, 230)

    def __init__(self, x: int, y: int):
        from game.settings import (
            GHOST_CAPTAIN_ATTACK_COOLDOWN,
            GHOST_CAPTAIN_HEALTH,
            GHOST_CAPTAIN_HEIGHT,
            GHOST_CAPTAIN_PHASE_DURATION,
            GHOST_CAPTAIN_SPEED,
            GHOST_CAPTAIN_TELEPORT_COOLDOWN,
            GHOST_CAPTAIN_WIDTH,
        )

        super().__init__(x, y, GHOST_CAPTAIN_WIDTH, GHOST_CAPTAIN_HEIGHT,
                         GHOST_CAPTAIN_HEALTH, self.GHOST_COLOR)

        self.speed = GHOST_CAPTAIN_SPEED
        self.attack_cooldown_duration = GHOST_CAPTAIN_ATTACK_COOLDOWN
        self.teleport_cooldown_duration = GHOST_CAPTAIN_TELEPORT_COOLDOWN
        self.phase_duration = GHOST_CAPTAIN_PHASE_DURATION

        # AI state
        self.state = self.STATE_IDLE
        self.state_timer = 60
        self.attack_cooldown = 0
        self.teleport_cooldown = self.teleport_cooldown_duration
        self.phase = 1  # Ghost Captain doesn't have phases, but UI expects it
        self.summon_pending = False  # Ghost Captain doesn't summon, but game.py expects it

        # Arena bounds
        self.arena_left = x - 300
        self.arena_right = x + 300
        self.arena_top = 0
        self.arena_bottom = 1200

        # Teleport destination (set when teleporting)
        self.teleport_target_x = x
        self.teleport_target_y = y

        # Visual effects
        self.alpha = 255  # For fading during teleport/phase
        self.damage_flash = 0
        self.float_offset = 0  # Ghostly floating

        # Create ghost sprite
        self._create_ghost_sprite()

    def _create_ghost_sprite(self) -> None:
        """Create the ghostly captain sprite."""
        from game.settings import GHOST_CAPTAIN_HEIGHT, GHOST_CAPTAIN_WIDTH

        w, h = GHOST_CAPTAIN_WIDTH, GHOST_CAPTAIN_HEIGHT
        self.base_image = pygame.Surface((w, h), pygame.SRCALPHA)

        # Ghostly body (translucent)
        body_color = (*self.GHOST_COLOR, 180)
        pygame.draw.ellipse(self.base_image, body_color, (4, 20, w - 8, h - 20))

        # Tattered coat tails (wavy bottom)
        for i in range(5):
            tail_x = 8 + i * 8
            tail_h = 10 + (i % 2) * 5
            pygame.draw.rect(self.base_image, body_color,
                           (tail_x, h - tail_h - 5, 6, tail_h))

        # Head
        head_color = (*self.GHOST_GLOW, 200)
        pygame.draw.circle(self.base_image, head_color, (w // 2, 16), 12)

        # Glowing eyes
        eye_color = (255, 100, 100, 255)
        pygame.draw.circle(self.base_image, eye_color, (w // 2 - 5, 14), 3)
        pygame.draw.circle(self.base_image, eye_color, (w // 2 + 5, 14), 3)

        # Pirate hat
        hat_color = (40, 40, 60, 220)
        pygame.draw.rect(self.base_image, hat_color, (w // 2 - 14, 2, 28, 8))
        pygame.draw.rect(self.base_image, hat_color, (w // 2 - 8, 0, 16, 10))

        # Ghostly sword (always visible)
        sword_color = (*self.GHOST_GLOW, 200)
        pygame.draw.rect(self.base_image, sword_color, (w - 8, 30, 6, 30))
        pygame.draw.rect(self.base_image, (200, 220, 255, 220), (w - 10, 28, 10, 4))

        self.image = self.base_image.copy()

    def set_arena_bounds(self, left: int, right: int, top: int = 0, bottom: int = 1200) -> None:
        """Set the arena boundaries for the ghost captain."""
        self.arena_left = left
        self.arena_right = right
        self.arena_top = top
        self.arena_bottom = bottom

    def take_damage(self, amount: int = 1) -> bool:
        """Take damage - immune during phase mode."""
        if self.state == self.STATE_PHASE:
            return False  # Invulnerable during phase

        if self.state == self.STATE_TELEPORT and self.alpha < 128:
            return False  # Invulnerable while faded out

        self.damage_flash = 15
        self.state = self.STATE_STUNNED
        self.state_timer = 30
        return super().take_damage(amount)

    def can_damage_player(self) -> bool:
        """Check if ghost can damage player."""
        # Can't damage during teleport fade or while stunned
        if self.state == self.STATE_TELEPORT and self.alpha < 200:
            return False
        if self.state == self.STATE_STUNNED:
            return False
        return super().can_damage_player()

    def update(self, player_rect: pygame.Rect = None) -> None:
        """Update ghost captain AI."""
        self.update_stun()

        if not player_rect:
            return

        # Update timers
        if self.damage_flash > 0:
            self.damage_flash -= 1
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.teleport_cooldown > 0:
            self.teleport_cooldown -= 1

        self.state_timer -= 1

        # Floating animation
        self.float_offset = math.sin(pygame.time.get_ticks() * 0.005) * 4

        # Face player (unless teleporting or phasing)
        if self.state not in (self.STATE_TELEPORT, self.STATE_PHASE):
            self.facing_right = player_rect.centerx > self.rect.centerx

        # State machine
        if self.state == self.STATE_STUNNED:
            if self.state_timer <= 0:
                self._choose_next_action(player_rect)

        elif self.state == self.STATE_IDLE:
            if self.state_timer <= 0:
                self._choose_next_action(player_rect)

        elif self.state == self.STATE_WALK:
            self._do_walk(player_rect)
            if self.state_timer <= 0:
                self._choose_next_action(player_rect)

        elif self.state == self.STATE_SLASH:
            if self.state_timer <= 0:
                self.state = self.STATE_IDLE
                self.state_timer = 20
                self.attack_cooldown = self.attack_cooldown_duration

        elif self.state == self.STATE_TELEPORT:
            self._do_teleport()

        elif self.state == self.STATE_PHASE:
            self._do_phase(player_rect)

        # Update visual
        self._update_visuals()

    def _choose_next_action(self, player_rect: pygame.Rect) -> None:
        """Choose next action based on distance to player."""
        distance_x = abs(player_rect.centerx - self.rect.centerx)
        distance_y = abs(player_rect.centery - self.rect.centery)
        distance = math.sqrt(distance_x ** 2 + distance_y ** 2)

        # Teleport if far away or randomly
        if self.teleport_cooldown <= 0 and (distance > 250 or random.random() < 0.2):
            self._start_teleport(player_rect)
            return

        # Phase attack if medium distance
        if self.attack_cooldown <= 0 and 100 < distance < 200 and random.random() < 0.3:
            self.state = self.STATE_PHASE
            self.state_timer = self.phase_duration
            return

        # Slash attack if close
        if self.attack_cooldown <= 0 and distance < 100:
            self.state = self.STATE_SLASH
            self.state_timer = 25
            return

        # Walk toward player
        self.state = self.STATE_WALK
        self.state_timer = 30 + random.randint(0, 20)

    def _start_teleport(self, player_rect: pygame.Rect) -> None:
        """Start teleport - fade out, move, fade in."""
        self.state = self.STATE_TELEPORT
        self.state_timer = 40  # Total teleport time

        # Choose destination near player but not too close
        offset_x = random.choice([-80, 80])
        self.teleport_target_x = player_rect.centerx + offset_x
        self.teleport_target_y = player_rect.centery

        # Clamp to arena
        self.teleport_target_x = max(self.arena_left,
                                     min(self.teleport_target_x, self.arena_right - self.rect.width))
        self.teleport_target_y = max(self.arena_top,
                                     min(self.teleport_target_y, self.arena_bottom - self.rect.height))

        self.teleport_cooldown = self.teleport_cooldown_duration

    def _do_teleport(self) -> None:
        """Execute teleport animation."""
        # First half: fade out
        if self.state_timer > 20:
            self.alpha = max(0, self.alpha - 20)
        # Middle: actually move
        elif self.state_timer == 20:
            self.rect.x = int(self.teleport_target_x)
            self.rect.y = int(self.teleport_target_y)
        # Second half: fade in
        else:
            self.alpha = min(255, self.alpha + 20)

        if self.state_timer <= 0:
            self.state = self.STATE_IDLE
            self.state_timer = 15
            self.alpha = 255

    def _do_phase(self, player_rect: pygame.Rect) -> None:
        """Phase through toward player (invulnerable dash)."""
        # Move toward player
        dx = player_rect.centerx - self.rect.centerx
        dy = player_rect.centery - self.rect.centery
        dist = math.sqrt(dx * dx + dy * dy)
        if dist > 0:
            self.rect.x += int((dx / dist) * 6)
            self.rect.y += int((dy / dist) * 6)

        # Flickering alpha during phase
        self.alpha = 100 + int(50 * math.sin(self.state_timer * 0.5))

        if self.state_timer <= 0:
            self.state = self.STATE_IDLE
            self.state_timer = 30
            self.attack_cooldown = self.attack_cooldown_duration * 2
            self.alpha = 255

    def _do_walk(self, player_rect: pygame.Rect) -> None:
        """Float toward player."""
        # Horizontal movement
        if self.facing_right:
            self.rect.x += self.speed
        else:
            self.rect.x -= self.speed

        # Slight vertical tracking
        if player_rect.centery < self.rect.centery - 20:
            self.rect.y -= 1
        elif player_rect.centery > self.rect.centery + 20:
            self.rect.y += 1

        # Keep in arena bounds
        self.rect.x = max(self.arena_left, min(self.rect.x, self.arena_right - self.rect.width))
        self.rect.y = max(self.arena_top, min(self.rect.y, self.arena_bottom - self.rect.height))

    def _update_visuals(self) -> None:
        """Update the ghost's visual appearance."""
        from game.settings import GHOST_CAPTAIN_HEIGHT, GHOST_CAPTAIN_WIDTH

        # Recreate sprite with current alpha
        self.image = self.base_image.copy()
        self.image.set_alpha(self.alpha)

        # Damage flash
        if self.damage_flash > 0 and self.damage_flash % 2 == 0:
            flash = pygame.Surface((GHOST_CAPTAIN_WIDTH, GHOST_CAPTAIN_HEIGHT), pygame.SRCALPHA)
            flash.fill((255, 255, 255, 150))
            self.image.blit(flash, (0, 0))

    def get_attack_hitbox(self) -> pygame.Rect | None:
        """Get attack hitbox for slash attack."""
        if self.state == self.STATE_SLASH and 5 < self.state_timer < 20:
            # Long spectral slash
            if self.facing_right:
                return pygame.Rect(self.rect.right, self.rect.top + 20, 60, 40)
            else:
                return pygame.Rect(self.rect.left - 60, self.rect.top + 20, 60, 40)

        if self.state == self.STATE_PHASE:
            # Body is dangerous during phase
            return self.rect.inflate(-10, -10)

        return None

    def get_attack_damage(self) -> int:
        """Get damage for current attack."""
        if self.state == self.STATE_SLASH:
            return 2
        if self.state == self.STATE_PHASE:
            return 1
        return 1

    def draw(self, surface: pygame.Surface, camera_offset: tuple[int, int] = (0, 0)) -> None:
        """Draw the ghost captain with effects."""
        if not self.active:
            return

        from game.settings import GHOST_CAPTAIN_HEIGHT, GHOST_CAPTAIN_WIDTH

        # Apply floating offset
        draw_x = self.rect.x - camera_offset[0]
        draw_y = self.rect.y - camera_offset[1] + int(self.float_offset)

        # Draw ghostly glow behind
        if self.alpha > 100:
            glow = pygame.Surface((GHOST_CAPTAIN_WIDTH + 20, GHOST_CAPTAIN_HEIGHT + 20), pygame.SRCALPHA)
            glow_alpha = min(80, self.alpha // 3)
            pygame.draw.ellipse(glow, (*self.GHOST_GLOW, glow_alpha),
                              (0, 10, GHOST_CAPTAIN_WIDTH + 20, GHOST_CAPTAIN_HEIGHT))
            surface.blit(glow, (draw_x - 10, draw_y - 10))

        # Draw sprite (flip if facing left)
        frame = self.image
        if not self.facing_right:
            frame = pygame.transform.flip(frame, True, False)
        surface.blit(frame, (draw_x, draw_y))

        # Draw slash effect
        if self.state == self.STATE_SLASH and 5 < self.state_timer < 20:
            slash_x = draw_x + (GHOST_CAPTAIN_WIDTH if self.facing_right else -50)
            slash_y = draw_y + 25
            # Ghostly slash arc
            slash_surf = pygame.Surface((60, 40), pygame.SRCALPHA)
            pygame.draw.arc(slash_surf, (*self.GHOST_GLOW, 200),
                          (0, 0, 60, 40), 0.5, 2.5, 4)
            if not self.facing_right:
                slash_surf = pygame.transform.flip(slash_surf, True, False)
            surface.blit(slash_surf, (slash_x, slash_y))

        # Draw health bar
        bar_width = 60
        bar_height = 6
        bar_x = draw_x + (GHOST_CAPTAIN_WIDTH - bar_width) // 2
        bar_y = draw_y - 15

        pygame.draw.rect(surface, (40, 40, 60), (bar_x, bar_y, bar_width, bar_height))
        health_pct = self.health / self.max_health
        pygame.draw.rect(surface, (100, 200, 150), (bar_x, bar_y, int(bar_width * health_pct), bar_height))
        pygame.draw.rect(surface, (80, 80, 100), (bar_x, bar_y, bar_width, bar_height), 1)

        # Draw phase effect (swirling ghosts)
        if self.state == self.STATE_PHASE:
            for i in range(3):
                angle = (pygame.time.get_ticks() / 100 + i * 2.1) % (2 * math.pi)
                ghost_x = draw_x + GHOST_CAPTAIN_WIDTH // 2 + int(25 * math.cos(angle))
                ghost_y = draw_y + GHOST_CAPTAIN_HEIGHT // 2 + int(15 * math.sin(angle))
                pygame.draw.circle(surface, (*self.GHOST_GLOW, 100), (ghost_x, ghost_y), 8)
