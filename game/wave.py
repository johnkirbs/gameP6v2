import pygame
import random
import math

class WaveGenerator:
    """Generates random wave/current vectors for the game"""
    
    def __init__(self, settings):
        """Initialize the wave generator"""
        self.settings = settings
        self.current_vector = [0, 0]  # x, y components of current
        self.current_magnitude = 0
        self.current_direction = 0  # in degrees
        self.next_wave_time = 0
        self.generate_new_wave()
        
    def generate_new_wave(self):
        """Generate a new random wave/current"""
        # Random direction (0-359 degrees)
        self.current_direction = random.randint(0, 359)
        
        # Random magnitude within settings
        self.current_magnitude = random.uniform(
            self.settings.MIN_WAVE_MAGNITUDE, 
            self.settings.MAX_WAVE_MAGNITUDE
        )
        
        # Calculate vector components
        self.current_vector[0] = math.sin(math.radians(self.current_direction)) * self.current_magnitude
        self.current_vector[1] = math.cos(math.radians(self.current_direction)) * self.current_magnitude
        
        # Set next wave change time
        self.next_wave_time = pygame.time.get_ticks() + self.settings.WAVE_CHANGE_INTERVAL
    
    def update(self):
        """Update the wave generator state"""
        current_time = pygame.time.get_ticks()
        
        # Check if it's time for a new wave
        if current_time >= self.next_wave_time:
            self.generate_new_wave()
            
    def get_current_vector(self):
        """Return the current wave/current vector"""
        return self.current_vector
    
    def draw_indicator(self, screen, boat_rect):
        """Draw an indicator showing wave direction and magnitude"""
        # Position of the indicator
        center_x = boat_rect.centerx + 100
        center_y = boat_rect.centery - 100
        
        # Draw the outer circle
        pygame.draw.circle(screen, self.settings.WHITE, (center_x, center_y), 30, 2)
        
        # Draw the direction indicator
        endpoint_x = center_x + math.sin(math.radians(self.current_direction)) * 25 * (self.current_magnitude / self.settings.MAX_WAVE_MAGNITUDE)
        endpoint_y = center_y + math.cos(math.radians(self.current_direction)) * 25 * (self.current_magnitude / self.settings.MAX_WAVE_MAGNITUDE)
        
        pygame.draw.line(screen, self.settings.BLUE, (center_x, center_y), (endpoint_x, endpoint_y), 3)
        pygame.draw.circle(screen, self.settings.BLUE, (int(endpoint_x), int(endpoint_y)), 5)
        
        # Label
        font = pygame.font.SysFont(None, 24)
        text = font.render("Current", True, self.settings.WHITE)
        screen.blit(text, (center_x - text.get_width() // 2, center_y - 50))