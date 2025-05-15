import pygame
import math

class WaveGenerator:
    """Generates wave/current vectors for the game"""
    
    def __init__(self, settings):
        """Initialize the wave generator"""
        self.settings = settings
        self.current_vector = [0, 0]  # x, y components of current
        self.current_magnitude = settings.CURRENT_MAGNITUDE
        self.current_direction = settings.CURRENT_DIRECTION  # in degrees
        self.update_current_vector()
        
    def update_current_vector(self):
        """Update the current vector based on direction and magnitude"""
        # Calculate vector components
        self.current_vector[0] = math.sin(math.radians(self.current_direction)) * self.current_magnitude
        self.current_vector[1] = math.cos(math.radians(self.current_direction)) * self.current_magnitude
    
    def update(self):
        """Update the wave generator state"""
        pass  # Current is now fixed
            
    def get_current_vector(self):
        """Return the current wave/current vector"""
        return self.current_vector
    
    def draw_indicator(self, screen, boat_rect):
        """Draw an indicator showing wave direction and magnitude"""
        # Position of the indicator
        center_x = 70  # Fixed position on screen
        center_y = 70
        
        # Draw background circle
        pygame.draw.circle(screen, (0, 0, 0, 128), (center_x, center_y), 35)  # Background
        pygame.draw.circle(screen, self.settings.WHITE, (center_x, center_y), 30, 2)  # Outer circle
        
        # Draw the direction indicator
        endpoint_x = center_x + math.sin(math.radians(self.current_direction)) * 25
        endpoint_y = center_y + math.cos(math.radians(self.current_direction)) * 25
        
        # Draw arrow
        pygame.draw.line(screen, self.settings.BLUE, (center_x, center_y), (endpoint_x, endpoint_y), 3)
        pygame.draw.circle(screen, self.settings.BLUE, (int(endpoint_x), int(endpoint_y)), 5)
        
        # Draw magnitude text
        font = pygame.font.SysFont(None, 24)
        mag_text = f"{self.current_magnitude:.1f}"
        text = font.render(mag_text, True, self.settings.WHITE)
        screen.blit(text, (center_x - text.get_width() // 2, center_y + 35))
        
        # Label
        label = font.render("Current", True, self.settings.WHITE)
        screen.blit(label, (center_x - label.get_width() // 2, center_y - 50))