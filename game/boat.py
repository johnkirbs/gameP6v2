import pygame
import math

class Boat:
    """Class to manage the player's boat"""
    
    def __init__(self, settings, screen_rect):
        """Initialize the boat and set its starting position"""
        self.settings = settings
        self.screen_rect = screen_rect
        
        # Load the boat image
        try:
            self.original_image = pygame.image.load(settings.BOAT_TEXTURE)
            self.rect = self.original_image.get_rect()
        except pygame.error:
            # Fallback to a simple surface if texture not found
            self.original_image = pygame.Surface((30, 60), pygame.SRCALPHA)
            pygame.draw.polygon(self.original_image, settings.WHITE, 
                               [(15, 0), (30, 60), (15, 45), (0, 60)])
            self.rect = self.original_image.get_rect()
        
        # Position the boat at the center of the screen
        self.x = float(screen_rect.centerx)
        self.y = float(screen_rect.centery)
        self.rect.center = (self.x, self.y)
        
        # Orientation and movement
        self.heading = 0  # in degrees, 0 is up
        self.velocity = [0, 0]
        self.rotation_direction = 0  # -1: left, 0: none, 1: right
        self.image = self.original_image  # Current rotated image
        
        # Steering arrow
        self.arrow_angle = 0  # Current steering angle
        self.steering_power = 0  # Current steering power (-1 to 1)
        
    def update(self, current_vector):
        """Update the boat's position based on user input and wave currents"""
        # Update boat heading based on steering
        self.heading += self.rotation_direction * self.settings.BOAT_ROTATION_SPEED
        self.heading %= 360
        
        # Calculate boat forward movement vector
        forward_x = -math.sin(math.radians(self.heading)) * self.settings.BOAT_SPEED
        forward_y = -math.cos(math.radians(self.heading)) * self.settings.BOAT_SPEED
        
        # Add current (wave) influence
        self.velocity[0] = forward_x + current_vector[0] 
        self.velocity[1] = forward_y + current_vector[1]
        
        # Update position (the boat is always at screen center, this moves the world)
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        
        # Update the rect position
        self.rect.center = (self.screen_rect.centerx, self.screen_rect.centery)
        
        # Rotate the image to match the heading
        self.image = pygame.transform.rotate(self.original_image, self.heading)
        self.rect = self.image.get_rect(center=self.rect.center)
        
    def steer(self, direction):
        """Set the steering direction"""
        self.rotation_direction = direction
        
    def draw(self, screen):
        """Draw the boat on the screen"""
        screen.blit(self.image, self.rect)
        self.draw_steering_arrow(screen)
    
    def draw_steering_arrow(self, screen):
        """Draw the steering arrow indicator"""
        arrow_length = 50
        arrow_width = 10
        
        # Calculate position for the arrow (below the boat)
        arrow_x = self.rect.centerx
        arrow_y = self.rect.bottom + 20
        
        # Draw arrow base
        pygame.draw.rect(screen, self.settings.WHITE, 
                         (arrow_x - arrow_length//2, arrow_y - arrow_width//2, 
                          arrow_length, arrow_width))
        
        # Draw arrow indicator (moves left/right based on steering)
        indicator_x = arrow_x + (self.steering_power * arrow_length//2)
        indicator_rect = pygame.Rect(0, 0, 15, 20)
        indicator_rect.center = (indicator_x, arrow_y)
        pygame.draw.rect(screen, self.settings.GREEN, indicator_rect)
        
    def get_position(self):
        """Return the boat's global position"""
        return (self.x, self.y)