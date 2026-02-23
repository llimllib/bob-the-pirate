"""Player character: Captain Bob."""

import pygame

from game.settings import (
    ATTACK_COOLDOWN,
    ATTACK_DURATION,
    ATTACK_RANGE,
    BROWN,
    GRAVITY,
    INVINCIBILITY_FRAMES,
    MAX_FALL_SPEED,
    PLAYER_HEIGHT,
    PLAYER_JUMP_POWER,
    PLAYER_MAX_HEALTH,
    PLAYER_SPEED,
    PLAYER_WIDTH,
    YELLOW,
)


class Player(pygame.sprite.Sprite):
    """The player character - Captain Bob the Pirate."""

    def __init__(self, x: int, y: int):
        super().__init__()

        # Visual
        self.image = pygame.Surface((PLAYER_WIDTH, PLAYER_HEIGHT))
        self.image.fill(BROWN)
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

        # Power-ups
        self.has_parrot = False
        self.parrot_timer = 0
        self.has_shield = False
        self.has_grog = False
        self.grog_timer = 0
        self.damage_multiplier = 1

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

        # Jumping
        if (keys[pygame.K_SPACE] or keys[pygame.K_w] or keys[pygame.K_UP]) and self.on_ground:
            self.velocity_y = PLAYER_JUMP_POWER
            self.on_ground = False

    def attack(self) -> pygame.Rect | None:
        """
        Perform a sword slash attack.
        Returns the attack hitbox if attacking, None otherwise.
        """
        if self.attack_cooldown > 0 or self.attacking:
            return None

        self.attacking = True
        self.attack_timer = ATTACK_DURATION
        self.attack_cooldown = ATTACK_COOLDOWN

        return self.get_attack_hitbox()

    def get_attack_hitbox(self) -> pygame.Rect | None:
        """Get the current attack hitbox if attacking."""
        if not self.attacking:
            return None

        if self.facing_right:
            return pygame.Rect(
                self.rect.right,
                self.rect.centery - PLAYER_HEIGHT // 4,
                ATTACK_RANGE,
                PLAYER_HEIGHT // 2
            )
        else:
            return pygame.Rect(
                self.rect.left - ATTACK_RANGE,
                self.rect.centery - PLAYER_HEIGHT // 4,
                ATTACK_RANGE,
                PLAYER_HEIGHT // 2
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

        # Move (collision handled by level)
        self.rect.x += int(self.velocity_x)
        self.rect.y += int(self.velocity_y)

    def draw(self, surface: pygame.Surface, camera_offset: tuple[int, int] = (0, 0)) -> None:
        """Draw the player to the screen."""
        draw_rect = self.rect.move(-camera_offset[0], -camera_offset[1])

        # Flash when invincible
        if self.invincible and self.invincibility_timer % 10 < 5:
            return  # Skip drawing for flash effect

        # Draw player
        surface.blit(self.image, draw_rect)

        # Draw attack visual
        if self.attacking:
            attack_hitbox = self.get_attack_hitbox()
            if attack_hitbox:
                attack_draw = attack_hitbox.move(-camera_offset[0], -camera_offset[1])
                pygame.draw.rect(surface, YELLOW, attack_draw, 2)
