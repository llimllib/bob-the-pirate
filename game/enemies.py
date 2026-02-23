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
    TILE_SIZE,
    WHITE,
    YELLOW,
)


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

    def take_damage(self, amount: int = 1) -> bool:
        """Take damage. Returns True if enemy died."""
        self.health -= amount
        if self.health <= 0:
            self.die()
            return True
        return False

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
        super().__init__(x, y, 28, 44, SAILOR_HEALTH, BLUE)
        self.start_x = x
        self.patrol_distance = patrol_distance
        self.velocity_x = SAILOR_SPEED

    def update(self, player_rect: pygame.Rect = None) -> None:
        """Patrol back and forth."""
        self.rect.x += self.velocity_x

        # Reverse at patrol boundaries
        if self.rect.x > self.start_x + self.patrol_distance:
            self.velocity_x = -SAILOR_SPEED
            self.facing_right = False
        elif self.rect.x < self.start_x:
            self.velocity_x = SAILOR_SPEED
            self.facing_right = True


class Musketeer(Enemy):
    """Ranged enemy - stands still and shoots."""

    def __init__(self, x: int, y: int, projectile_group: pygame.sprite.Group):
        super().__init__(x, y, 28, 44, MUSKETEER_HEALTH, (150, 0, 0))
        self.projectile_group = projectile_group
        self.shoot_cooldown = MUSKETEER_SHOOT_COOLDOWN
        self.shoot_timer = self.shoot_cooldown

    def update(self, player_rect: pygame.Rect = None) -> None:
        """Face player and shoot periodically."""
        if player_rect:
            self.facing_right = player_rect.centerx > self.rect.centerx

        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            self.shoot()
            self.shoot_timer = self.shoot_cooldown

    def shoot(self) -> None:
        """Fire a musket ball."""
        direction = 1 if self.facing_right else -1
        ball = MusketBall(
            self.rect.centerx,
            self.rect.centery,
            direction
        )
        self.projectile_group.add(ball)


class Officer(Enemy):
    """Aggressive enemy - chases and attacks player with sword."""

    def __init__(self, x: int, y: int):
        super().__init__(x, y, 32, 48, OFFICER_HEALTH, (0, 0, 150))
        self.chase_range = 250
        self.attack_range = 45
        self.attacking = False
        self.attack_timer = 0
        self.attack_cooldown = 0
        self.attack_duration = 20
        self.cooldown_duration = 40

    def update(self, player_rect: pygame.Rect = None) -> None:
        """Chase player if in range, attack when close."""
        if not player_rect:
            return

        # Update attack timers
        if self.attacking:
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.attacking = False
                self.attack_cooldown = self.cooldown_duration
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
            return

        if distance < self.attack_range and not self.attacking and self.attack_cooldown <= 0:
            # Attack!
            self.attacking = True
            self.attack_timer = self.attack_duration
            self.velocity_x = 0
        elif distance < self.chase_range and distance > self.attack_range - 10:
            # Chase player
            if distance_x > 0:
                self.velocity_x = OFFICER_SPEED
            else:
                self.velocity_x = -OFFICER_SPEED
            self.rect.x += self.velocity_x
        else:
            self.velocity_x = 0

    def get_attack_hitbox(self) -> pygame.Rect:
        """Get the attack hitbox when attacking."""
        if not self.attacking:
            return None

        if self.facing_right:
            return pygame.Rect(self.rect.right, self.rect.top + 10, 35, 30)
        else:
            return pygame.Rect(self.rect.left - 35, self.rect.top + 10, 35, 30)

    def draw(self, surface: pygame.Surface, camera_offset: tuple[int, int] = (0, 0)) -> None:
        """Draw the officer with attack indicator."""
        if not self.active:
            return
        super().draw(surface, camera_offset)

        # Draw attack effect
        if self.attacking:
            attack_box = self.get_attack_hitbox()
            if attack_box:
                draw_rect = attack_box.move(-camera_offset[0], -camera_offset[1])
                pygame.draw.rect(surface, (200, 200, 0), draw_rect, 2)


class Cannon(Enemy):
    """Stationary cannon that fires arcing cannonballs."""

    def __init__(self, x: int, y: int, projectile_group: pygame.sprite.Group, faces_right: bool = True):
        super().__init__(x, y, TILE_SIZE, TILE_SIZE, 2, (50, 50, 50))
        self.projectile_group = projectile_group
        self.faces_right = faces_right
        self.facing_right = faces_right
        self.shoot_cooldown = CANNON_SHOOT_COOLDOWN
        self.shoot_timer = self.shoot_cooldown
        # Add visual indicator for direction
        self._draw_barrel()

    def _draw_barrel(self) -> None:
        """Draw cannon with barrel direction."""
        self.image.fill((50, 50, 50))
        # Draw barrel
        if self.faces_right:
            pygame.draw.rect(self.image, (30, 30, 30), (TILE_SIZE - 12, 8, 12, 16))
        else:
            pygame.draw.rect(self.image, (30, 30, 30), (0, 8, 12, 16))

    def update(self, player_rect: pygame.Rect = None) -> None:
        """Fire cannonballs periodically."""
        self.shoot_timer -= 1
        if self.shoot_timer <= 0:
            self.shoot()
            self.shoot_timer = self.shoot_cooldown

    def shoot(self) -> None:
        """Fire a cannonball with arc."""
        direction = 1 if self.faces_right else -1
        ball = Cannonball(
            self.rect.centerx,
            self.rect.centery - 5,
            direction
        )
        self.projectile_group.add(ball)


class Projectile(pygame.sprite.Sprite):
    """Base class for projectiles."""

    def __init__(self, x: int, y: int, velocity_x: float, velocity_y: float,
                 size: int, color: tuple, damage: int = 1):
        super().__init__()
        self.image = pygame.Surface((size, size))
        self.image.fill(color)
        self.rect = self.image.get_rect(center=(x, y))

        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.damage = damage
        self.active = True

    def update(self) -> None:
        """Move projectile."""
        self.rect.x += int(self.velocity_x)
        self.rect.y += int(self.velocity_y)

        # Remove if off screen (handled by level)

    def draw(self, surface: pygame.Surface, camera_offset: tuple[int, int] = (0, 0)) -> None:
        """Draw the projectile."""
        draw_rect = self.rect.move(-camera_offset[0], -camera_offset[1])
        surface.blit(self.image, draw_rect)


class MusketBall(Projectile):
    """Fast, straight-flying projectile from Musketeers."""

    def __init__(self, x: int, y: int, direction: int):
        super().__init__(
            x, y,
            PROJECTILE_SPEED * direction, 0,
            8, WHITE, 1
        )


class Cannonball(Projectile):
    """Arcing projectile from Cannons."""

    def __init__(self, x: int, y: int, direction: int):
        super().__init__(
            x, y,
            CANNONBALL_SPEED * direction, -8,
            12, (30, 30, 30), 2
        )
        self.gravity = CANNONBALL_GRAVITY

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
            10, (200, 150, 50), 1
        )

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
        # Bullet
        pygame.draw.circle(surface, (200, 150, 50), draw_rect.center, 5)
