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
    water = pygame.Surface((300, 300))
    water.fill((10, 50, 120))  # Dark blue
    
    # Add subtle grid pattern instead of wave lines
    for x in range(0, 300, 50):
        pygame.draw.line(water, (20, 60, 140), (x, 0), (x, 300), 1)
    for y in range(0, 300, 50):
        pygame.draw.line(water, (20, 60, 140), (0, y), (300, y), 1)
    
    # Add some small dots as reference points
    for x in range(25, 300, 50):
        for y in range(25, 300, 50):
            pygame.draw.circle(water, (30, 70, 150), (x, y), 2)
    
    pygame.image.save(water, "assets/textures/water.png")
    
    # Generate boat
    print("Creating boat image...")
    boat = pygame.Surface((60, 100), pygame.SRCALPHA)
    
    # Draw boat shape with brighter colors
    pygame.draw.polygon(boat, (240, 240, 240), [(30, 0), (60, 90), (40, 75), (20, 75), (0, 90)])
    
    # Add more detailed cabin
    pygame.draw.rect(boat, (160, 80, 40), (20, 30, 20, 20))  # Cabin
    pygame.draw.rect(boat, (180, 180, 180), (25, 35, 10, 10))  # Window
    
    # Add distinctive markings for orientation
    pygame.draw.circle(boat, (220, 50, 50), (30, 15), 5)  # Red marker at front
    pygame.draw.rect(boat, (50, 50, 180), (23, 55, 14, 5))  # Blue stripe near back
    
    pygame.image.save(boat, "assets/textures/boat.png")
    
    # Generate island
    print("Creating island image...")
    island = pygame.Surface((160, 160), pygame.SRCALPHA)
    
    # Draw island base with more distinctive colors
    pygame.draw.circle(island, (220, 200, 120), (80, 80), 70)  # Brighter sand
    
    # Add vegetation with more contrast
    pygame.draw.circle(island, (34, 160, 34), (60, 60), 30)  # Brighter green trees
    pygame.draw.circle(island, (34, 180, 34), (90, 50), 25)  # Trees
    pygame.draw.circle(island, (34, 160, 34), (110, 80), 20)  # Trees
    
    # Add a distinctive marker/feature to make island more recognizable
    pygame.draw.circle(island, (180, 60, 60), (80, 60), 12)  # Red marker/building
    pygame.draw.rect(island, (150, 150, 150), (75, 20, 10, 30))  # Lighthouse or tower
    
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