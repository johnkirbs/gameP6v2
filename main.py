import pygame
import sys
from game.engine import GameEngine
from config.settings import Settings

def main():
    # Initialize pygame
    pygame.init()
    
    # Load settings
    settings = Settings()
    
    # Create the game engine
    game = GameEngine(settings)
    
    # Main game loop
    clock = pygame.time.Clock()
    while True:
        # Check for quit event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            game.handle_event(event)
        
        # Update game state
        game.update()
        
        # Draw the game
        game.draw()
        
        # Update the display
        pygame.display.flip()
        
        # Cap the frame rate
        clock.tick(settings.FPS)

if __name__ == "__main__":
    main()
    