#!/usr/bin/env python3
"""Render the Ghost Captain sprite to a PNG file for viewing."""
# ruff: noqa: E402

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pygame

pygame.init()

# Create a display (required for some pygame operations)
screen = pygame.display.set_mode((400, 300))

# Import after pygame init (must be after pygame.init())
from game.enemies import GhostCaptain
from game.settings import GHOST_CAPTAIN_HEIGHT, GHOST_CAPTAIN_WIDTH

# Create the ghost captain
ghost = GhostCaptain(100, 100)

# Get the sprite dimensions
w, h = GHOST_CAPTAIN_WIDTH, GHOST_CAPTAIN_HEIGHT

# Create a larger surface to show the sprite with some padding and labels
output_width = w * 4 + 60  # 4 views with padding
output_height = h + 80
output = pygame.Surface((output_width, output_height), pygame.SRCALPHA)
output.fill((40, 40, 50, 255))  # Dark background

# Draw a title
font = pygame.font.Font(None, 24)
title = font.render("LORD TIM, GHOST CAPTAIN - Sprite Sheet", True, (200, 220, 255))
output.blit(title, (output_width // 2 - title.get_width() // 2, 5))

# Draw the base sprite (facing right)
label1 = font.render("Idle Right", True, (180, 180, 180))
output.blit(label1, (15, 30))
output.blit(ghost.base_image, (15, 50))

# Draw flipped (facing left)
label2 = font.render("Idle Left", True, (180, 180, 180))
output.blit(label2, (w + 30, 30))
flipped = pygame.transform.flip(ghost.base_image, True, False)
output.blit(flipped, (w + 30, 50))

# Draw with glow effect
label3 = font.render("With Glow", True, (180, 180, 180))
output.blit(label3, (w * 2 + 45, 30))
glow_surf = pygame.Surface((w + 20, h + 20), pygame.SRCALPHA)
pygame.draw.ellipse(glow_surf, (150, 200, 230, 60), (0, 10, w + 20, h))
output.blit(glow_surf, (w * 2 + 35, 40))
output.blit(ghost.base_image, (w * 2 + 45, 50))

# Draw with damage flash
label4 = font.render("Damaged", True, (180, 180, 180))
output.blit(label4, (w * 3 + 60, 30))
damaged = ghost.base_image.copy()
flash = pygame.Surface((w, h), pygame.SRCALPHA)
flash.fill((255, 255, 255, 100))
damaged.blit(flash, (0, 0))
output.blit(damaged, (w * 3 + 60, 50))

# Save to file
output_path = "assets/sprites/ghost_captain_preview.png"
pygame.image.save(output, output_path)
print(f"Saved ghost captain sprite preview to: {output_path}")

# Also save just the base sprite
base_path = "assets/sprites/ghost_captain.png"
pygame.image.save(ghost.base_image, base_path)
print(f"Saved ghost captain base sprite to: {base_path}")

pygame.quit()
