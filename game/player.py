"""Player character: Captain Bob."""

import os

import pygame

from game.animation import AnimatedSprite, Animation, SpriteSheet, create_placeholder_frames
from game.settings import (
    ANCHOR_SLAM_COOLDOWN,
    ANCHOR_SLAM_SPEED,
    ATTACK_COOLDOWN,
    ATTACK_DURATION,
    ATTACK_FRAME_WIDTH,
    ATTACK_RANGE,
    BARREL_ROLL_COOLDOWN,
    BARREL_ROLL_DOUBLE_TAP_WINDOW,
    BARREL_ROLL_DURATION,
    BARREL_ROLL_SPEED,
    CUTLASS_FURY_COOLDOWN_MULT,
    CUTLASS_FURY_RANGE_MULT,
    GHOST_SKIN_ATTACK_DURATION,
    GHOST_SKIN_ATTACK_FRAME_WIDTHS,
    GHOST_SKIN_ATTACK_HEIGHT,
    GHOST_SKIN_ATTACK_RANGE,
    GHOST_SKIN_CAN_MOVE_WHILE_ATTACKING,
    GHOST_SKIN_HEALTH_BONUS,
    GHOST_SKIN_SPEED_MULT,
    GRAVITY,
    INVINCIBILITY_FRAMES,
    MAX_FALL_SPEED,
    PLAYER_HEIGHT,
    PLAYER_JUMP_POWER,
    PLAYER_MAX_HEALTH,
    PLAYER_SPEED,
    PLAYER_WIDTH,
    SKELETON_SKIN_BONE_EVERY_N_ATTACKS,
    SKELETON_SKIN_DAMAGE_MULT,
    SKELETON_SKIN_HEALTH_PENALTY,
)


class Player(pygame.sprite.Sprite):
    """The player character - Captain Bob the Pirate."""

    def __init__(self, x: int, y: int):
        super().__init__()

        # Check for special skins
        from game.skins import (
            is_admiral_bob_active,
            is_blackbeard_active,
            is_ghost_captain_active,
            is_noble_pirate_active,
            is_skeleton_pirate_active,
        )
        self.is_ghost_captain = is_ghost_captain_active()
        self.is_skeleton_pirate = is_skeleton_pirate_active()
        self.is_blackbeard = is_blackbeard_active()
        self.is_noble_pirate = is_noble_pirate_active()
        self.is_admiral_bob = is_admiral_bob_active()

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

        # Stats - skins modify health
        base_health = PLAYER_MAX_HEALTH
        if self.is_ghost_captain:
            base_health += GHOST_SKIN_HEALTH_BONUS
        elif self.is_skeleton_pirate:
            base_health -= SKELETON_SKIN_HEALTH_PENALTY
        self.max_health = max(1, base_health)  # Minimum 1 health
        self.health = self.max_health
        self.lives = 3

        # Ghost Captain wispy trail particles
        self.trail_particles: list[dict] = []

        # Combat
        self.attacking = False
        self.attack_timer = 0
        self.attack_cooldown = 0
        self.invincible = False
        self.invincibility_timer = 0
        self.hurt_timer = 0  # For hurt animation
        self.enemies_hit_this_attack: set[int] = set()  # Track enemy IDs hit during current attack
        self.last_attack_frame = -1  # Track animation frame for Ghost Captain multi-hit

        # Skeleton Pirate bone throw tracking
        self.attack_count = 0  # Counts attacks for bone throw
        self.pending_bone_throw = False  # Set to True when bone should be thrown

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

        # Barrel Roll ability (innate)
        self.rolling = False
        self.roll_timer = 0
        self.roll_cooldown = 0
        self.roll_direction = 1  # 1 = right, -1 = left
        self.last_left_tap = 0  # Frame counter for double-tap detection
        self.last_right_tap = 0

        # Anchor Slam ability (innate)
        self.slamming = False
        self.slam_cooldown = 0
        self.slam_landed = False  # True when slam hit the ground

    def _load_animations(self) -> None:
        """Load player animations from sprite sheet or use placeholders."""
        # Get selected skin sprite
        from game.skins import get_selected_skin_sprite
        skin_sprite = get_selected_skin_sprite()
        sprite_path = f"assets/sprites/{skin_sprite}"

        # Fall back to default if skin sprite doesn't exist
        if not os.path.exists(sprite_path):
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

            # Row 3: Attack (3 frames with variable widths)
            # Ghost Captain has different frame widths for flame attack
            attack_y = PLAYER_HEIGHT * 3
            if self.is_ghost_captain:
                # Ghost Captain flame attack: 32, 56, 56 widths
                # Fast animation that loops during the 2-second attack
                frame_widths = GHOST_SKIN_ATTACK_FRAME_WIDTHS
                x_pos = 0
                attack_frames = []
                for width in frame_widths:
                    frame = sheet.sheet.subsurface((x_pos, attack_y, width, PLAYER_HEIGHT))
                    attack_frames.append(frame)
                    x_pos += width
                # 20 frames per animation frame = ~3 cycles per second, loops during attack
                self.sprite.add_animation("attack", Animation(attack_frames, frame_duration=20, loop=True))
            else:
                # Normal attack: 32, 56, 32 widths
                attack_frame_0 = sheet.sheet.subsurface((0, attack_y, PLAYER_WIDTH, PLAYER_HEIGHT))
                attack_frame_1 = sheet.sheet.subsurface((PLAYER_WIDTH, attack_y, ATTACK_FRAME_WIDTH, PLAYER_HEIGHT))
                attack_frame_2 = sheet.sheet.subsurface((PLAYER_WIDTH + ATTACK_FRAME_WIDTH, attack_y, PLAYER_WIDTH, PLAYER_HEIGHT))
                attack_frames = [attack_frame_0, attack_frame_1, attack_frame_2]
                self.sprite.add_animation("attack", Animation(attack_frames, frame_duration=5, loop=False))

            # Row 4: Roll (4 frames)
            roll_frames = sheet.get_strip(PLAYER_HEIGHT * 4, PLAYER_WIDTH, PLAYER_HEIGHT, 4)
            self.sprite.add_animation("roll", Animation(roll_frames, frame_duration=4, loop=True))

            # Row 5: Slam (3 frames)
            slam_frames = sheet.get_strip(PLAYER_HEIGHT * 5, PLAYER_WIDTH, PLAYER_HEIGHT, 3)
            self.sprite.add_animation("slam", Animation(slam_frames, frame_duration=5, loop=False))
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

        # Barrel roll - blue tint to indicate invincibility
        roll_frames = create_placeholder_frames(PLAYER_WIDTH, PLAYER_HEIGHT, (50, 100, 200), 4, "roll")
        self.sprite.add_animation("roll", Animation(roll_frames, frame_duration=4, loop=True))

        # Anchor slam - red/orange tint for power attack
        slam_frames = create_placeholder_frames(PLAYER_WIDTH, PLAYER_HEIGHT, (200, 100, 50), 3, "slam")
        self.sprite.add_animation("slam", Animation(slam_frames, frame_duration=5, loop=False))

    def reload_skin(self) -> None:
        """Reload animations with the currently selected skin."""
        # Store current animation state
        current_anim = self.sprite.current_animation

        # Update skin status flags
        from game.skins import (
            is_admiral_bob_active,
            is_blackbeard_active,
            is_ghost_captain_active,
            is_noble_pirate_active,
            is_skeleton_pirate_active,
        )
        old_is_ghost = self.is_ghost_captain
        old_is_skeleton = self.is_skeleton_pirate
        old_is_blackbeard = self.is_blackbeard
        old_is_noble = self.is_noble_pirate
        old_is_admiral = self.is_admiral_bob
        self.is_ghost_captain = is_ghost_captain_active()
        self.is_skeleton_pirate = is_skeleton_pirate_active()
        self.is_blackbeard = is_blackbeard_active()
        self.is_noble_pirate = is_noble_pirate_active()
        self.is_admiral_bob = is_admiral_bob_active()

        # Update max health if skin changed
        skin_changed = (old_is_ghost != self.is_ghost_captain or
                       old_is_skeleton != self.is_skeleton_pirate or
                       old_is_blackbeard != self.is_blackbeard or
                       old_is_noble != self.is_noble_pirate or
                       old_is_admiral != self.is_admiral_bob)
        if skin_changed:
            old_max = self.max_health
            base_health = PLAYER_MAX_HEALTH
            if self.is_ghost_captain:
                base_health += GHOST_SKIN_HEALTH_BONUS
            elif self.is_skeleton_pirate:
                base_health -= SKELETON_SKIN_HEALTH_PENALTY
            self.max_health = max(1, base_health)
            # Scale current health proportionally
            if old_max > 0:
                health_pct = self.health / old_max
                self.health = max(1, int(self.max_health * health_pct))
            # Reset skeleton attack counter on skin change
            self.attack_count = 0
            self.pending_bone_throw = False

        # Clear and reload animations
        self.sprite = AnimatedSprite()
        self._load_animations()

        # Restore animation state
        if current_anim:
            self.sprite.play(current_anim)
        else:
            self.sprite.play("idle")

        # Update image
        self.image = self.sprite.get_frame()

    def _update_animation_state(self) -> None:
        """Update which animation should be playing based on player state."""
        # Priority: hurt > roll > slam > attack > jump/fall > run > idle
        if self.hurt_timer > 0:
            self.sprite.play("hurt")
        elif self.rolling:
            self.sprite.play("roll")
        elif self.slamming:
            self.sprite.play("slam")
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

        # Update facing direction (unless rolling, keep roll direction)
        if not self.rolling:
            self.sprite.facing_right = self.facing_right
        else:
            self.sprite.facing_right = self.roll_direction > 0

    def handle_input(self, keys: pygame.key.ScancodeWrapper) -> None:
        """Process keyboard input for movement and actions."""
        # Don't allow normal movement during roll or slam
        if self.rolling:
            self.velocity_x = BARREL_ROLL_SPEED * self.roll_direction
            return
        if self.slamming:
            self.velocity_x = 0
            return

        # Ghost Captain can move while attacking, others cannot
        can_move = True
        if self.attacking and not (self.is_ghost_captain and GHOST_SKIN_CAN_MOVE_WHILE_ATTACKING):
            can_move = False

        # Horizontal movement
        self.velocity_x = 0
        if can_move:
            # Ghost Captain has reduced speed
            speed = PLAYER_SPEED
            if self.is_ghost_captain:
                speed = int(PLAYER_SPEED * GHOST_SKIN_SPEED_MULT)

            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.velocity_x = -speed
                self.facing_right = False
            if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.velocity_x = speed
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

    def try_barrel_roll(self, direction: int, frame_count: int) -> bool:
        """
        Attempt to start a barrel roll.

        Args:
            direction: -1 for left, 1 for right
            frame_count: Current game frame for double-tap detection

        Returns True if roll was started.
        """
        if self.rolling or self.roll_cooldown > 0 or self.slamming:
            return False

        # Check for double-tap within window
        # Must have a previous tap (non-zero) and be within the window
        if direction < 0:
            if self.last_left_tap > 0 and frame_count - self.last_left_tap <= BARREL_ROLL_DOUBLE_TAP_WINDOW:
                self._start_roll(direction)
                self.last_left_tap = 0  # Reset to prevent triple-tap issues
                return True
            self.last_left_tap = frame_count
        else:
            if self.last_right_tap > 0 and frame_count - self.last_right_tap <= BARREL_ROLL_DOUBLE_TAP_WINDOW:
                self._start_roll(direction)
                self.last_right_tap = 0  # Reset to prevent triple-tap issues
                return True
            self.last_right_tap = frame_count

        return False

    def _start_roll(self, direction: int) -> None:
        """Start the barrel roll."""
        self.rolling = True
        self.roll_timer = BARREL_ROLL_DURATION
        self.roll_direction = direction
        self.invincible = True
        self.invincibility_timer = BARREL_ROLL_DURATION + 5  # Slightly longer for safety
        self.sprite.play("roll", force_restart=True)

    def try_anchor_slam(self) -> bool:
        """
        Attempt to start an anchor slam.
        Can only be done while in the air.

        Returns True if slam was started.
        """
        if self.on_ground or self.slamming or self.slam_cooldown > 0 or self.rolling:
            return False

        self.slamming = True
        self.slam_landed = False
        self.velocity_y = ANCHOR_SLAM_SPEED
        self.velocity_x = 0
        self.sprite.play("slam", force_restart=True)
        return True

    def land_anchor_slam(self) -> bool:
        """
        Called when player lands during a slam.
        Returns True if this was an anchor slam landing (for triggering effects).
        """
        if self.slamming and not self.slam_landed:
            self.slam_landed = True
            self.slamming = False
            self.slam_cooldown = ANCHOR_SLAM_COOLDOWN
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

        # Ghost Captain has 2-second flame attack
        attack_duration = ATTACK_DURATION
        if self.is_ghost_captain:
            attack_duration = GHOST_SKIN_ATTACK_DURATION
        self.attack_timer = attack_duration

        # Cutlass Fury reduces cooldown
        cooldown = ATTACK_COOLDOWN
        if self.has_cutlass_fury:
            cooldown = int(ATTACK_COOLDOWN * CUTLASS_FURY_COOLDOWN_MULT)
        self.attack_cooldown = cooldown

        self.enemies_hit_this_attack.clear()  # Reset hit tracking for new attack
        self.last_attack_frame = -1  # Reset frame tracker for Ghost Captain multi-hit

        # Skeleton Pirate: track attacks and throw bone every Nth attack
        if self.is_skeleton_pirate:
            self.attack_count += 1
            if self.attack_count >= SKELETON_SKIN_BONE_EVERY_N_ATTACKS:
                self.pending_bone_throw = True
                self.attack_count = 0

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

    def get_total_damage_multiplier(self) -> float:
        """Get the total damage multiplier from all sources."""
        mult = self.damage_multiplier  # Base multiplier (grog rage sets this to 2)
        if self.is_skeleton_pirate:
            mult *= SKELETON_SKIN_DAMAGE_MULT
        return mult

    def get_attack_hitbox(self) -> pygame.Rect | None:
        """Get the current attack hitbox if attacking."""
        if not self.attacking:
            return None

        # Ghost Captain has larger flame hitbox
        if self.is_ghost_captain:
            attack_range = GHOST_SKIN_ATTACK_RANGE
            attack_height = GHOST_SKIN_ATTACK_HEIGHT
        else:
            attack_range = ATTACK_RANGE
            attack_height = PLAYER_HEIGHT // 2

        # Cutlass Fury increases range (applies to both)
        if self.has_cutlass_fury:
            attack_range = int(attack_range * CUTLASS_FURY_RANGE_MULT)
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
        # Apply gravity (reduced during slam for consistent speed)
        if not self.slamming:
            self.velocity_y += GRAVITY
            if self.velocity_y > MAX_FALL_SPEED:
                self.velocity_y = MAX_FALL_SPEED

        # Update attack state
        if self.attacking:
            self.attack_timer -= 1
            if self.attack_timer <= 0:
                self.attacking = False
                self.last_attack_frame = -1

            # Ghost Captain flame attack: reset hit tracking when animation frame changes
            # This allows the flame to deal damage once per animation cycle
            if self.is_ghost_captain and self.attacking:
                current_frame = self.sprite.get_current_frame_index()
                if current_frame != self.last_attack_frame:
                    self.enemies_hit_this_attack.clear()
                    self.last_attack_frame = current_frame

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

        # Update barrel roll
        if self.rolling:
            self.roll_timer -= 1
            if self.roll_timer <= 0:
                self.rolling = False
                self.roll_cooldown = BARREL_ROLL_COOLDOWN

        if self.roll_cooldown > 0:
            self.roll_cooldown -= 1

        # Update anchor slam cooldown
        if self.slam_cooldown > 0:
            self.slam_cooldown -= 1

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

        # Ghost Captain wispy trail effect
        if self.is_ghost_captain:
            self._update_ghost_trail()

        # Update animation
        self._update_animation_state()
        self.sprite.update()
        self.image = self.sprite.get_frame()

    def _update_ghost_trail(self) -> None:
        """Update Ghost Captain's wispy particle trail."""
        import random

        # Spawn new particles when moving
        if abs(self.velocity_x) > 0 or abs(self.velocity_y) > 1:
            # Spawn 2-4 particles per frame when moving (more visible)
            for _ in range(random.randint(2, 4)):
                self.trail_particles.append({
                    "x": self.rect.centerx + random.randint(-10, 10),
                    "y": self.rect.centery + random.randint(-5, 20),
                    "vx": random.uniform(-0.8, 0.8),
                    "vy": random.uniform(-2.0, -0.8),  # Float upward faster
                    "life": random.randint(25, 45),  # Longer life
                    "max_life": 45,
                    "size": random.randint(5, 10),  # Much bigger particles
                })

        # Update existing particles
        for p in self.trail_particles:
            p["x"] += p["vx"]
            p["y"] += p["vy"]
            p["life"] -= 1
            # Slow down slightly
            p["vx"] *= 0.96
            p["vy"] *= 0.98

        # Remove dead particles
        self.trail_particles = [p for p in self.trail_particles if p["life"] > 0]

        # Limit max particles (higher limit for more visible trail)
        if len(self.trail_particles) > 80:
            self.trail_particles = self.trail_particles[-80:]

    def draw(self, surface: pygame.Surface, camera_offset: tuple[int, int] = (0, 0)) -> None:
        """Draw the player to the screen."""
        draw_x = self.rect.x - camera_offset[0]
        draw_y = self.rect.y - camera_offset[1]

        # Draw Ghost Captain wispy trail behind player
        if self.is_ghost_captain and self.trail_particles:
            self._draw_ghost_trail(surface, camera_offset)

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

    def _draw_ghost_trail(self, surface: pygame.Surface, camera_offset: tuple[int, int]) -> None:
        """Draw Ghost Captain's wispy particle trail."""
        for p in self.trail_particles:
            # Calculate alpha based on remaining life (brighter)
            life_ratio = p["life"] / p["max_life"]
            alpha = int(220 * life_ratio)  # Brighter base alpha

            # Brighter spectral blue-green color with cyan tint
            # Core is brighter, fades to darker edge
            r = int(120 + 80 * life_ratio)  # 120-200
            g = int(200 + 55 * life_ratio)  # 200-255
            b = int(220 + 35 * life_ratio)  # 220-255
            color = (r, g, b, alpha)

            # Draw position
            px = int(p["x"]) - camera_offset[0]
            py = int(p["y"]) - camera_offset[1]

            # Size shrinks as particle fades, but stays bigger
            size = max(2, int(p["size"] * (0.4 + 0.6 * life_ratio)))

            # Draw as a soft glowing circle
            particle_surf = pygame.Surface((size * 2 + 4, size * 2 + 4), pygame.SRCALPHA)

            # Outer glow (larger, dimmer)
            glow_alpha = alpha // 3
            glow_color = (r, g, b, glow_alpha)
            pygame.draw.circle(particle_surf, glow_color, (size + 2, size + 2), size + 2)

            # Inner bright core
            pygame.draw.circle(particle_surf, color, (size + 2, size + 2), size)

            surface.blit(particle_surf, (px - size - 2, py - size - 2))
