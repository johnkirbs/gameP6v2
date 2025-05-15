import pygame

class Controls:
    """Control mappings for the game"""
    
    def __init__(self):
        """Initialize the default control mappings"""
        self.STEER_LEFT = pygame.K_LEFT
        self.STEER_RIGHT = pygame.K_RIGHT
        self.PAUSE = pygame.K_p
        self.RESTART = pygame.K_r
        
    def load_custom_controls(self, config_file=None):
        """Load custom control mappings from a file"""
        # This could be implemented to load custom key bindings
        pass
