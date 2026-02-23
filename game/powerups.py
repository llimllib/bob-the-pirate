"""Power-up entities: Parrot companion, shields, monkey, etc."""

import math
import os

import pygame

from game.animation import AnimatedSprite, Animation, SpriteSheet, create_placeholder_frames
from game.settings import (
    CANNON_SHOT_DAMAGE,
    CANNON_SHOT_SPEED,
    MONKEY_ATTACK_COOLDOWN,
    MONKEY_DAMAGE,
    MONKEY_HEIGHT,
    MONKEY_RANGE,
    MONKEY_WIDTH,
    PARROT_ATTACK_COOLDOWN,
    PARROT_DAMAGE,
    PARROT_HEIGHT,
    PARROT_WIDTH,
    RED,
)


class Parrot(pygame.sprite.Sprite):
    """
    Parrot companion that follows the player and attacks nearby enemies.
    Floats around the player and periodically swoops at enemies.
    """

    def __init__(self, player):
        super().__init__()
        self.player = player

        # Set up animated sprite
        self.sprite = AnimatedSprite()
        self._load_animations()
        self.sprite.play("flying")

        # Visual - updated from animation
        self.image = self.sprite.get_frame()
        self.rect = self.image.get_rect()

        # Movement
        self.offset_x = -20  # Offset from player
        self.offset_y = -30
        self.bob_angle = 0  # For floating animation
        self.bob_speed = 0.1
        self.bob_amount = 5

        # Combat
        self.attack_cooldown = 0
        self.attacking = False
        self.attack_target = None
        self.attack_start_pos = None
        self.attack_timer = 0
        self.attack_duration = 20  # Frames to complete attack

        # Position
        self.x = player.rect.centerx + self.offset_x
        self.y = player.rect.top + self.offset_y

    def _load_animations(self) -> None:
        """Load parrot animations from sprite sheet or use placeholders."""
        sprite_path = "assets/sprites/parrot.png"

        if os.path.exists(sprite_path):
            sheet = SpriteSheet(sprite_path)

            # Row 0: Flying (2 frames), Attack (2 frames)
            flying_frames = sheet.get_strip(0, PARROT_WIDTH, PARROT_HEIGHT, 2)
            self.sprite.add_animation("flying", Animation(flying_frames, frame_duration=8, loop=True))

            attack_frames = sheet.get_strip(0, PARROT_WIDTH, PARROT_HEIGHT, 2, x_start=PARROT_WIDTH * 2)
            self.sprite.add_animation("attack", Animation(attack_frames, frame_duration=5, loop=True))
        else:
            self._load_placeholder_animations()

    def _load_placeholder_animations(self) -> None:
        """Load placeholder colored rectangle animations."""
        flying_frames = create_placeholder_frames(PARROT_WIDTH, PARROT_HEIGHT, (50, 180, 80), 2, "fly")
        self.sprite.add_animation("flying", Animation(flying_frames, frame_duration=8, loop=True))

        attack_frames = create_placeholder_frames(PARROT_WIDTH, PARROT_HEIGHT, (220, 60, 60), 2, "atk")
        self.sprite.add_animation("attack", Animation(attack_frames, frame_duration=5, loop=True))

    def find_target(self, enemies: pygame.sprite.Group) -> pygame.sprite.Sprite | None:
        """Find the nearest enemy within attack range."""
        attack_range = 150
        nearest = None
        nearest_dist = float('inf')

        for enemy in enemies:
            if not enemy.active:
                continue
            dx = enemy.rect.centerx - self.rect.centerx
            dy = enemy.rect.centery - self.rect.centery
            dist = math.sqrt(dx * dx + dy * dy)

            if dist < attack_range and dist < nearest_dist:
                nearest = enemy
                nearest_dist = dist

        return nearest

    def update(self, enemies: pygame.sprite.Group) -> pygame.sprite.Sprite | None:
        """
        Update parrot position and behavior.
        Returns enemy that was damaged, if any.
        """
        damaged_enemy = None

        if self.attacking:
            # Continue attack animation
            self.attack_timer += 1

            if self.attack_target and self.attack_target.active:
                # Lerp towards target
                progress = self.attack_timer / self.attack_duration

                if progress < 0.5:
                    # Moving towards target
                    t = progress * 2
                    target_x = self.attack_target.rect.centerx
                    target_y = self.attack_target.rect.centery
                    self.x = self.attack_start_pos[0] + (target_x - self.attack_start_pos[0]) * t
                    self.y = self.attack_start_pos[1] + (target_y - self.attack_start_pos[1]) * t

                    # Check for hit at midpoint
                    if progress >= 0.4 and self.rect.colliderect(self.attack_target.rect):
                        self.attack_target.take_damage(PARROT_DAMAGE)
                        damaged_enemy = self.attack_target
                else:
                    # Returning to player
                    t = (progress - 0.5) * 2
                    target_x = self.player.rect.centerx + self.offset_x
                    target_y = self.player.rect.top + self.offset_y
                    mid_x = self.attack_target.rect.centerx
                    mid_y = self.attack_target.rect.centery
                    self.x = mid_x + (target_x - mid_x) * t
                    self.y = mid_y + (target_y - mid_y) * t

            if self.attack_timer >= self.attack_duration:
                self.attacking = False
                self.attack_target = None
        else:
            # Idle floating near player
            self.bob_angle += self.bob_speed
            bob_offset = math.sin(self.bob_angle) * self.bob_amount

            # Follow player with offset
            target_x = self.player.rect.centerx + self.offset_x
            target_y = self.player.rect.top + self.offset_y + bob_offset

            # Smooth follow
            self.x += (target_x - self.x) * 0.2
            self.y += (target_y - self.y) * 0.2

            # Check for attack
            self.attack_cooldown -= 1
            if self.attack_cooldown <= 0:
                target = self.find_target(enemies)
                if target:
                    self.start_attack(target)

        # Update rect position
        self.rect.centerx = int(self.x)
        self.rect.centery = int(self.y)

        # Update animation
        if self.attacking:
            self.sprite.play("attack")
        else:
            self.sprite.play("flying")

        self.sprite.facing_right = self.player.facing_right
        self.sprite.update()
        self.image = self.sprite.get_frame()

        return damaged_enemy

    def start_attack(self, target: pygame.sprite.Sprite) -> None:
        """Begin attack on target enemy."""
        self.attacking = True
        self.attack_target = target
        self.attack_start_pos = (self.x, self.y)
        self.attack_timer = 0
        self.attack_cooldown = PARROT_ATTACK_COOLDOWN

    def draw(self, surface: pygame.Surface, camera_offset: tuple[int, int] = (0, 0)) -> None:
        """Draw the parrot."""
        draw_rect = self.rect.move(-camera_offset[0], -camera_offset[1])

        # Just draw the current animation frame (already flipped by AnimatedSprite)
        surface.blit(self.image, draw_rect)

        # Draw attack indicator when attacking
        if self.attacking:
            pygame.draw.circle(surface, RED, draw_rect.center, 8, 2)


class GhostShield:
    """
    Temporary shield that absorbs one hit.
    Visual effect around player.
    """

    def __init__(self, player):
        self.player = player
        self.active = True
        self.pulse_angle = 0
        self.pulse_speed = 0.1

    def absorb_hit(self) -> bool:
        """
        Try to absorb damage.
        Returns True if shield blocked the hit (and is now gone).
        """
        if self.active:
            self.active = False
            return True
        return False

    def update(self) -> None:
        """Update shield animation."""
        self.pulse_angle += self.pulse_speed

    def draw(self, surface: pygame.Surface, camera_offset: tuple[int, int] = (0, 0)) -> None:
        """Draw shield effect around player."""
        if not self.active:
            return

        # Pulsing shield circle
        pulse = math.sin(self.pulse_angle) * 5
        radius = max(self.player.rect.width, self.player.rect.height) // 2 + 10 + int(pulse)

        center_x = self.player.rect.centerx - camera_offset[0]
        center_y = self.player.rect.centery - camera_offset[1]

        # Ghost ship colors - translucent blue
        pygame.draw.circle(surface, (100, 150, 200), (center_x, center_y), radius, 3)
        pygame.draw.circle(surface, (150, 200, 255), (center_x, center_y), radius - 3, 1)


class Monkey(pygame.sprite.Sprite):
    """
    Monkey companion that follows the player and throws coconuts at enemies.
    Has longer range than parrot but similar behavior.
    """

    def __init__(self, player, projectile_group: pygame.sprite.Group):
        super().__init__()
        self.player = player
        self.projectile_group = projectile_group

        # Set up animated sprite
        self.sprite = AnimatedSprite()
        self._load_animations()
        self.sprite.play("idle")

        # Visual
        self.image = self.sprite.get_frame()
        self.rect = self.image.get_rect()

        # Movement - sits on player's shoulder
        self.offset_x = 15
        self.offset_y = -20
        self.bob_angle = 0
        self.bob_speed = 0.15
        self.bob_amount = 3

        # Combat
        self.attack_cooldown = 0
        self.throwing = False
        self.throw_timer = 0
        self.throw_duration = 15

        # Position
        self.x = player.rect.centerx + self.offset_x
        self.y = player.rect.top + self.offset_y

    def _load_animations(self) -> None:
        """Load monkey animations (placeholder for now)."""
        # Brown monkey colors
        idle_frames = create_placeholder_frames(
            MONKEY_WIDTH, MONKEY_HEIGHT, (139, 90, 43), 2, "idle"
        )
        self.sprite.add_animation(
            "idle", Animation(idle_frames, frame_duration=12, loop=True)
        )

        throw_frames = create_placeholder_frames(
            MONKEY_WIDTH, MONKEY_HEIGHT, (180, 120, 60), 2, "throw"
        )
        self.sprite.add_animation(
            "throw", Animation(throw_frames, frame_duration=7, loop=False)
        )

    def find_target(self, enemies: pygame.sprite.Group) -> pygame.sprite.Sprite | None:
        """Find the nearest enemy within attack range."""
        nearest = None
        nearest_dist = float('inf')

        for enemy in enemies:
            if not enemy.active:
                continue
            dx = enemy.rect.centerx - self.rect.centerx
            dy = enemy.rect.centery - self.rect.centery
            dist = math.sqrt(dx * dx + dy * dy)

            if dist < MONKEY_RANGE and dist < nearest_dist:
                nearest = enemy
                nearest_dist = dist

        return nearest

    def update(self, enemies: pygame.sprite.Group) -> None:
        """Update monkey position and behavior."""
        # Handle throwing animation
        if self.throwing:
            self.throw_timer -= 1
            if self.throw_timer <= 0:
                self.throwing = False
        else:
            # Check for attack
            self.attack_cooldown -= 1
            if self.attack_cooldown <= 0:
                target = self.find_target(enemies)
                if target:
                    self.throw_coconut(target)

        # Idle on player's shoulder with slight bob
        self.bob_angle += self.bob_speed
        bob_offset = math.sin(self.bob_angle) * self.bob_amount

        # Follow player - on opposite side from facing direction
        if self.player.facing_right:
            target_x = self.player.rect.left - 5
        else:
            target_x = self.player.rect.right + 5 - MONKEY_WIDTH

        target_y = self.player.rect.top + self.offset_y + bob_offset

        # Smooth follow
        self.x += (target_x - self.x) * 0.3
        self.y += (target_y - self.y) * 0.3

        # Update rect
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

        # Update animation
        if self.throwing:
            self.sprite.play("throw")
        else:
            self.sprite.play("idle")

        self.sprite.facing_right = self.player.facing_right
        self.sprite.update()
        self.image = self.sprite.get_frame()

    def throw_coconut(self, target: pygame.sprite.Sprite) -> None:
        """Throw a coconut at target."""
        self.throwing = True
        self.throw_timer = self.throw_duration
        self.attack_cooldown = MONKEY_ATTACK_COOLDOWN

        # Create coconut projectile
        coconut = Coconut(
            self.rect.centerx,
            self.rect.centery,
            target.rect.centerx,
            target.rect.centery
        )
        self.projectile_group.add(coconut)

    def draw(self, surface: pygame.Surface, camera_offset: tuple[int, int] = (0, 0)) -> None:
        """Draw the monkey."""
        draw_rect = self.rect.move(-camera_offset[0], -camera_offset[1])
        surface.blit(self.image, draw_rect)


class Coconut(pygame.sprite.Sprite):
    """Projectile thrown by monkey companion."""

    def __init__(self, x: int, y: int, target_x: int, target_y: int):
        super().__init__()
        self.image = pygame.Surface((10, 10), pygame.SRCALPHA)
        # Brown coconut
        pygame.draw.circle(self.image, (101, 67, 33), (5, 5), 5)
        pygame.draw.circle(self.image, (139, 90, 43), (5, 5), 3)

        self.rect = self.image.get_rect(center=(x, y))
        self.damage = MONKEY_DAMAGE

        # Calculate velocity toward target
        dx = target_x - x
        dy = target_y - y
        dist = math.sqrt(dx * dx + dy * dy)
        speed = 8
        if dist > 0:
            self.velocity_x = (dx / dist) * speed
            self.velocity_y = (dy / dist) * speed
        else:
            self.velocity_x = speed
            self.velocity_y = 0

        self.lifetime = 60  # Max frames before despawn

    def update(self) -> None:
        """Move coconut."""
        self.rect.x += int(self.velocity_x)
        self.rect.y += int(self.velocity_y)
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.kill()


class PlayerCannonball(pygame.sprite.Sprite):
    """Cannonball fired by player with Cannon Shot power-up."""

    def __init__(self, x: int, y: int, direction: int):
        super().__init__()
        self.image = pygame.Surface((14, 14), pygame.SRCALPHA)
        # Dark cannonball with highlight
        pygame.draw.circle(self.image, (30, 30, 30), (7, 7), 7)
        pygame.draw.circle(self.image, (60, 60, 60), (5, 5), 3)

        self.rect = self.image.get_rect(center=(x, y))
        self.velocity_x = CANNON_SHOT_SPEED * direction
        self.damage = CANNON_SHOT_DAMAGE
        self.direction = direction

    def update(self) -> None:
        """Move cannonball."""
        self.rect.x += int(self.velocity_x)

    def draw(self, surface: pygame.Surface, camera_offset: tuple[int, int] = (0, 0)) -> None:
        """Draw with trail effect."""
        draw_rect = self.rect.move(-camera_offset[0], -camera_offset[1])

        # Draw trail
        trail_color = (100, 100, 100)
        trail_start = (draw_rect.centerx, draw_rect.centery)
        trail_end = (draw_rect.centerx - self.direction * 20, draw_rect.centery)
        pygame.draw.line(surface, trail_color, trail_start, trail_end, 3)

        # Draw cannonball
        surface.blit(self.image, draw_rect)
