"""Power-up entities: Parrot companion, shields, etc."""

import pygame
import math
from game.settings import (
    PARROT_ATTACK_COOLDOWN, PARROT_DAMAGE, GREEN, RED, YELLOW
)


class Parrot(pygame.sprite.Sprite):
    """
    Parrot companion that follows the player and attacks nearby enemies.
    Floats around the player and periodically swoops at enemies.
    """

    def __init__(self, player):
        super().__init__()
        self.player = player
        
        # Visual
        self.image = pygame.Surface((16, 12))
        self.image.fill(GREEN)
        # Add wing detail
        pygame.draw.polygon(self.image, (0, 200, 0), [(8, 0), (16, 6), (8, 6)])
        # Add beak
        pygame.draw.polygon(self.image, YELLOW, [(0, 4), (0, 8), (-4, 6)])
        
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
        
        # Flip image based on direction
        img = self.image
        if self.player.facing_right:
            img = pygame.transform.flip(self.image, True, False)
        
        surface.blit(img, draw_rect)
        
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
