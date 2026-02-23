"""Player character: Captain Bob."""

import os

import pygame

from game.animation import AnimatedSprite, Animation, SpriteSheet, create_placeholder_frames
from game.settings import (
    ATTACK_COOLDOWN,
    ATTACK_DURATION,
    ATTACK_FRAME_WIDTH,
    ATTACK_RANGE,
    CUTLASS_FURY_COOLDOWN_MULT,
    CUTLASS_FURY_RANGE_MULT,
    GRAVITY,
    INVINCIBILITY_FRAMES,
    MAX_FALL_SPEED,
    PLAYER_HEIGHT,
    PLAYER_JUMP_POWER,
    PLAYER_MAX_HEALTH,
    PLAYER_SPEED,
    PLAYER_WIDTH,
)


class Player(pygame.sprite.Sprite):
    """The player character - Captain Bob the Pirate."""

    def __init__(self, x: int, y: int):
        super().__init__()

        # Set up animated sprite
        self.sprite = AnimatedSprite()
        self._load_animations()

        # Start with idle animation
        self.sprite.play("idle")

        # Visual - image updated each frame from animation
        self.image = self.sprite.get_frame()
        self.rect = self.image.get_rect(topleft=(x, y))

        # Movement
        self.velocity_x = 0
        self.velocity_y = 0
        self.on_ground = False
        self.facing_right = True

        # Stats
        self.max_health = PLAYER_MAX_HEALTH
        self.health = self.max_health
        self.lives = 3

        # Combat
        self.attacking = False
        self.attack_timer = 0
        self.attack_cooldown = 0
        self.invincible = False
        self.invincibility_timer = 0
        self.hurt_timer = 0  # For hurt animation
        self.enemies_hit_this_attack: set[int] = set()  # Track enemy IDs hit during current attack

        # Power-ups
        self.has_parrot = False
        self.parrot_timer = 0
        self.has_shield = False
        self.has_grog = False
        self.grog_timer = 0
        self.damage_multiplier = 1

        # Cannon Shot power-up
        self.has_cannon_shot = False
        self.cannon_ammo = 0

        # Double Jump power-up
        self.has_double_jump = False
        self.double_jump_timer = 0
        self.can_double_jump = False  # Reset when landing
        self.used_double_jump = False  # Track if used in current air time

        # Cutlass Fury power-up
        self.has_cutlass_fury = False
        self.cutlass_fury_timer = 0

        # Treasure Magnet power-up
        self.has_magnet = False
        self.magnet_timer = 0

        # Monkey Mate power-up
        self.has_monkey = False
        self.monkey_timer = 0

    def _load_animations(self) -> None:
        """Load player animations from sprite sheet or use placeholders."""
        sprite_path = "assets/sprites/player.png"

        if os.path.exists(sprite_path):
            sheet = SpriteSheet(sprite_path)

            # Row 0: Idle (2 frames)
            idle_frames = sheet.get_strip(0, PLAYER_WIDTH, PLAYER_HEIGHT, 2)
            self.sprite.add_animation("idle", Animation(idle_frames, frame_duration=30, loop=True))

            # Row 1: Run (4 frames)
            run_frames = sheet.get_strip(PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT, 4)
            self.sprite.add_animation("run", Animation(run_frames, frame_duration=8, loop=True))

            # Row 2: Jump, Fall, Hurt
            jump_frames = sheet.get_strip(PLAYER_HEIGHT * 2, PLAYER_WIDTH, PLAYER_HEIGHT, 1)
            self.sprite.add_animation("jump", Animation(jump_frames, frame_duration=1, loop=False))

            fall_frames = sheet.get_strip(PLAYER_HEIGHT * 2, PLAYER_WIDTH, PLAYER_HEIGHT, 1, x_start=PLAYER_WIDTH)
            self.sprite.add_animation("fall", Animation(fall_frames, frame_duration=1, loop=False))

            hurt_frames = sheet.get_strip(PLAYER_HEIGHT * 2, PLAYER_WIDTH, PLAYER_HEIGHT, 1, x_start=PLAYER_WIDTH * 2)
            self.sprite.add_animation("hurt", Animation(hurt_frames, frame_duration=8, loop=False))

            # Row 3: Attack (3 frames with variable widths: 32, 56, 32)
            attack_y = PLAYER_HEIGHT * 3
            attack_frame_0 = sheet.sheet.subsurface((0, attack_y, PLAYER_WIDTH, PLAYER_HEIGHT))
            attack_frame_1 = sheet.sheet.subsurface((PLAYER_WIDTH, attack_y, ATTACK_FRAME_WIDTH, PLAYER_HEIGHT))
            attack_frame_2 = sheet.sheet.subsurface((PLAYER_WIDTH + ATTACK_FRAME_WIDTH, attack_y, PLAYER_WIDTH, PLAYER_HEIGHT))
            attack_frames = [attack_frame_0, attack_frame_1, attack_frame_2]
            self.sprite.add_animation("attack", Animation(attack_frames, frame_duration=5, loop=False))
        else:
            # Use placeholder frames if sprite sheet not found
            self._load_placeholder_animations()

    def _load_placeholder_animations(self) -> None:
        """Load placeholder colored rectangle animations."""
        brown = (139, 69, 19)

        idle_frames = create_placeholder_frames(PLAYER_WIDTH, PLAYER_HEIGHT, brown, 2, "idle")
        self.sprite.add_animation("idle", Animation(idle_frames, frame_duration=30, loop=True))

        run_frames = create_placeholder_frames(PLAYER_WIDTH, PLAYER_HEIGHT, brown, 4, "run")
        self.sprite.add_animation("run", Animation(run_frames, frame_duration=8, loop=True))

        jump_frames = create_placeholder_frames(PLAYER_WIDTH, PLAYER_HEIGHT, brown, 1, "jump")
        self.sprite.add_animation("jump", Animation(jump_frames, frame_duration=1, loop=False))

        fall_frames = create_placeholder_frames(PLAYER_WIDTH, PLAYER_HEIGHT, brown, 1, "fall")
        self.sprite.add_animation("fall", Animation(fall_frames, frame_duration=1, loop=False))

        hurt_frames = create_placeholder_frames(PLAYER_WIDTH, PLAYER_HEIGHT, (200, 50, 50), 1, "hurt")
        self.sprite.add_animation("hurt", Animation(hurt_frames, frame_duration=8, loop=False))

        attack_frames = create_placeholder_frames(PLAYER_WIDTH, PLAYER_HEIGHT, (200, 150, 50), 3, "atk")
        self.sprite.add_animation("attack", Animation(attack_frames, frame_duration=5, loop=False))

    def _update_animation_state(self) -> None:
        """Update which animation should be playing based on player state."""
        # Priority: hurt > attack > jump/fall > run > idle
        if self.hurt_timer > 0:
            self.sprite.play("hurt")
        elif self.attacking:
            self.sprite.play("attack")
        elif not self.on_ground:
            if self.velocity_y < 0:
                self.sprite.play("jump")
            else:
                self.sprite.play("fall")
        elif self.velocity_x != 0:
            self.sprite.play("run")
        else:
            self.sprite.play("idle")

        # Update facing direction
        self.sprite.facing_right = self.facing_right

    def handle_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        """Process keyboard input for movement and actions."""
        # Horizontal movement
        self.velocity_x = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.velocity_x = -PLAYER_SPEED
            self.facing_right = False
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.velocity_x = PLAYER_SPEED
            self.facing_right = True

        # Jumping (handled by game.py for double jump sound support)
        # Base jump
        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.on_ground:
            self.velocity_y = PLAYER_JUMP_POWER
            self.on_ground = False
            self.used_double_jump = False  # Reset double jump on ground jump

    def try_double_jump(self) -> bool:
        """
        Attempt to perform a double jump.
        Returns True if double jump was performed.
        """
        if self.has_double_jump and not self.on_ground and not self.used_double_jump:
            self.velocity_y = PLAYER_JUMP_POWER * 0.85  # Slightly weaker
            self.used_double_jump = True
            return True
        return False

    def attack(self) -> pygame.Rect | None:
        """
        Perform a sword slash attack.
        Returns the attack hitbox if attacking, None otherwise.
        """
        if self.attack_cooldown > 0 or self.attacking:
            return None

        self.attacking = True
        self.attack_timer = ATTACK_DURATION

        # Cutlass Fury reduces cooldown
        cooldown = ATTACK_COOLDOWN
        if self.has_cutlass_fury:
            cooldown = int(ATTACK_COOLDOWN * CUTLASS_FURY_COOLDOWN_MULT)
        self.attack_cooldown = cooldown

        self.enemies_hit_this_attack.clear()  # Reset hit tracking for new attack

        # Force attack animation to restart
        self.sprite.play("attack", force_restart=True)

        return self.get_attack_hitbox()

    def fire_cannon(self) -> bool:
        """
        Fire a cannon shot if player has ammo.
        Returns True if shot was fired.
        """
        if self.has_cannon_shot and self.cannon_ammo > 0 and self.attack_cooldown <= 0:
            self.cannon_ammo -= 1
            self.attack_cooldown = ATTACK_COOLDOWN  # Share cooldown with melee
            if self.cannon_ammo <= 0:
                self.has_cannon_shot = False
            return True
        return False

    def get_attack_hitbox(self) -> pygame.Rect | None:
        """Get the current attack hitbox if attacking."""
        if not self.attacking:
            return None

        # Cutlass Fury increases range
        attack_range = ATTACK_RANGE
        attack_height = PLAYER_HEIGHT // 2
        if self.has_cutlass_fury:
            attack_range = int(ATTACK_RANGE * CUTLASS_FURY_RANGE_MULT)
            attack_height = int(attack_height * CUTLASS_FURY_RANGE_MULT)

        if self.facing_right:
            return pygame.Rect(
                self.rect.right,
                self.rect.centery - attack_height // 2,
                attack_range,
                attack_height
            )
        else:
            return pygame.Rect(
                self.rect.left - attack_range,
                self.rect.centery - attack_height // 2,
                attack_range,
                attack_height
            )

    def take_damage(self, amount: int = 1) -> bool:
        """
        Take damage if not invincible.
        Returns True if damage was taken.
        """
        if self.invincible:
            return False

        self.health -= amount
        self.invincible = True
        self.invincibility_timer = INVINCIBILITY_FRAMES
        self.hurt_timer = 20  # Show hurt animation for 20 frames

        if self.health <= 0:
            self.die()

        return True

    def die(self) -> None:
        """Handle player death."""
        self.lives -= 1
        if self.lives > 0:
            self.respawn()
        # Game over handled by game manager

    def respawn(self) -> None:
        """Respawn at checkpoint or level start."""
        self.health = self.max_health
        self.invincible = True
        self.invincibility_timer = INVINCIBILITY_FRAMES * 2
        self.hurt_timer = 0
        # Position reset handled by level manager

    def heal(self, amount: int = 1) -> None:
        """Restore health."""
        self.health = min(self.health + amount, self.max_health)

    def update(self, dt: float = 1.0) -> None:
        """Update player state each frame."""
        # Apply gravity
        self.velocity_y += GRAVITY
        if self.velocity_y > MAX_FALL_SPEED:
            self.velocity_y = MAX_FALL_SPEED

        # Update attack state
        if self.attacking:
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.attacking = False

        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1

        # Update hurt timer
        if self.hurt_timer > 0:
            self.hurt_timer -= 1

        # Update invincibility
        if self.invincible:
            self.invincibility_timer -= 1
            if self.invincibility_timer <= 0:
                self.invincible = False

        # Update power-ups
        if self.has_parrot:
            self.parrot_timer -= 1
            if self.parrot_timer <= 0:
                self.has_parrot = False

        if self.has_grog:
            self.grog_timer -= 1
            if self.grog_timer <= 0:
                self.has_grog = False
                self.damage_multiplier = 1

        if self.has_double_jump:
            self.double_jump_timer -= 1
            if self.double_jump_timer <= 0:
                self.has_double_jump = False

        if self.has_cutlass_fury:
            self.cutlass_fury_timer -= 1
            if self.cutlass_fury_timer <= 0:
                self.has_cutlass_fury = False

        if self.has_magnet:
            self.magnet_timer -= 1
            if self.magnet_timer <= 0:
                self.has_magnet = False

        if self.has_monkey:
            self.monkey_timer -= 1
            if self.monkey_timer <= 0:
                self.has_monkey = False

        # Reset double jump when landing
        if self.on_ground:
            self.used_double_jump = False

        # Move (collision handled by level)
        self.rect.x += int(self.velocity_x)
        self.rect.y += int(self.velocity_y)

        # Update animation
        self._update_animation_state()
        self.sprite.update()
        self.image = self.sprite.get_frame()

    def draw(self, surface: pygame.Surface, camera_offset: tuple[int, int] = (0, 0)) -> None:
        """Draw the player to the screen."""
        draw_x = self.rect.x - camera_offset[0]
        draw_y = self.rect.y - camera_offset[1]

        # Flash when invincible (but not during hurt animation)
        if self.invincible and self.hurt_timer <= 0 and self.invincibility_timer % 10 < 5:
            return  # Skip drawing for flash effect

        # Handle wider attack sprite offset
        # When attacking with the extended frame, adjust position so Bob stays centered
        # and the sword extends in the correct direction
        if self.attacking and self.image.get_width() > PLAYER_WIDTH:
            extra_width = self.image.get_width() - PLAYER_WIDTH
            if not self.facing_right:
                # Facing left: shift draw position left so sword extends left
                draw_x -= extra_width

        # Draw player sprite
        surface.blit(self.image, (draw_x, draw_y))
