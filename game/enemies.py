"""Enemy classes for British naval forces."""

import pygame
from game.settings import (
    TILE_SIZE, SAILOR_SPEED, SAILOR_HEALTH, MUSKETEER_HEALTH,
    MUSKETEER_SHOOT_COOLDOWN, OFFICER_SPEED, OFFICER_HEALTH,
    PROJECTILE_SPEED, BLUE, RED, WHITE, YELLOW
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
    """Aggressive enemy - chases and attacks player."""

    def __init__(self, x: int, y: int):
        super().__init__(x, y, 32, 48, OFFICER_HEALTH, (0, 0, 150))
        self.chase_range = 200
        self.attack_range = 40

    def update(self, player_rect: pygame.Rect = None) -> None:
        """Chase player if in range."""
        if not player_rect:
            return
        
        distance_x = player_rect.centerx - self.rect.centerx
        distance = abs(distance_x)
        
        if distance < self.chase_range and distance > self.attack_range:
            # Chase player
            if distance_x > 0:
                self.velocity_x = OFFICER_SPEED
                self.facing_right = True
            else:
                self.velocity_x = -OFFICER_SPEED
                self.facing_right = False
            self.rect.x += self.velocity_x
        else:
            self.velocity_x = 0


class Cannon(Enemy):
    """Stationary cannon that fires arcing cannonballs."""

    def __init__(self, x: int, y: int, projectile_group: pygame.sprite.Group, faces_right: bool = True):
        super().__init__(x, y, TILE_SIZE, TILE_SIZE, 2, (50, 50, 50))
        self.projectile_group = projectile_group
        self.faces_right = faces_right
        self.shoot_cooldown = 180  # 3 seconds
        self.shoot_timer = self.shoot_cooldown

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
            self.rect.centery,
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
            PROJECTILE_SPEED * 0.8 * direction, -8,
            12, (30, 30, 30), 2
        )
        self.gravity = 0.3

    def update(self) -> None:
        """Move with gravity arc."""
        self.velocity_y += self.gravity
        super().update()
