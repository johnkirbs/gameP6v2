"""
Asset Generator for Island Navigator

This script creates basic placeholder assets for the game.
Run this script once to generate the necessary image files.
"""

import pygame
import os
import sys

def generate_assets():
    """Generate placeholder assets for the game"""
    print("Generating placeholder assets...")
    
    # Initialize pygame to use its drawing capabilities
    pygame.init()
    
    # Create directories if they don't exist
    if not os.path.exists("assets"):
        os.makedirs("assets")
    if not os.path.exists("assets/textures"):
        os.makedirs("assets/textures")
    
    # Generate water background
    print("Creating water background...")
    water = pygame.Surface((200, 200))
    water.fill((0, 70, 150))  # Dark blue
    # Add some wave lines
    for y in range(0, 200, 10):
        pygame.draw.line(water, (0, 100, 200), (0, y), (200, y), 2)
    pygame.image.save(water, "assets/textures/water.png")
    
    # Generate boat
    print("Creating boat image...")
    boat = pygame.Surface((60, 100), pygame.SRCALPHA)
    # Draw boat shape
    pygame.draw.polygon(boat, (200, 200, 200), [(30, 0), (60, 90), (40, 75), (20, 75), (0, 90)])
    # Add some details
    pygame.draw.rect(boat, (139, 69, 19), (20, 30, 20, 20))  # Cabin
    pygame.image.save(boat, "assets/textures/boat.png")
    
    # Generate island
    print("Creating island image...")
    island = pygame.Surface((160, 160), pygame.SRCALPHA)
    # Draw island base
    pygame.draw.circle(island, (194, 178, 128), (80, 80), 70)  # Sand
    # Add vegetation
    pygame.draw.circle(island, (34, 139, 34), (60, 60), 30)  # Trees
    pygame.draw.circle(island, (34, 139, 34), (90, 50), 25)  # Trees
    pygame.draw.circle(island, (34, 139, 34), (110, 80), 20)  # Trees
    pygame.image.save(island, "assets/textures/island.png")
    
    # Generate arrow
    print("Creating arrow image...")
    arrow = pygame.Surface((100, 50), pygame.SRCALPHA)
    pygame.draw.polygon(arrow, (255, 255, 0), [(0, 20), (70, 20), (70, 0), (100, 25), (70, 50), (70, 30), (0, 30)])
    pygame.image.save(arrow, "assets/textures/arrow.png")
    
    # Generate wave texture
    print("Creating wave texture...")
    wave = pygame.Surface((30, 30), pygame.SRCALPHA)
    pygame.draw.arc(wave, (255, 255, 255), (0, 0, 30, 30), 0, 3.14, 2)
    pygame.draw.arc(wave, (255, 255, 255), (5, 10, 20, 20), 0, 3.14, 2)
    pygame.image.save(wave, "assets/textures/wave.png")
    
    print("Asset generation complete!")

if __name__ == "__main__":
    generate_assets()