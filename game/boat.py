import pygame
import math

class Boat:
    """Class to manage the player's boat"""
    
    def __init__(self, settings, screen_rect):
        """Initialize the boat and set its starting position"""
        self.settings = settings
        self.screen_rect = screen_rect
        
        # Load the boat image
        import os
        try:
            if os.path.exists(settings.BOAT_TEXTURE):
                self.original_image = pygame.image.load(settings.BOAT_TEXTURE).convert_alpha()
                # Scale the image to desired size
                self.original_image = pygame.transform.scale(self.original_image, (60, 100))
                self.rect = self.original_image.get_rect()
            else:
                # Fallback to a simple boat shape if texture not found
                self.original_image = pygame.Surface((60, 100), pygame.SRCALPHA)
                pygame.draw.polygon(self.original_image, settings.WHITE, 
                                   [(30, 0), (60, 90), (30, 75), (0, 90)])
                self.rect = self.original_image.get_rect()
        except Exception as e:
            print(f"Boat image loading error: {e}. Using fallback.")
            # Fallback to a simple boat shape
            self.original_image = pygame.Surface((60, 100), pygame.SRCALPHA)
            pygame.draw.polygon(self.original_image, settings.WHITE, 
                               [(30, 0), (60, 90), (30, 75), (0, 90)])
            self.rect = self.original_image.get_rect()
        
        # Position the boat at the center of the screen
        self.x = float(screen_rect.centerx)
        self.y = float(screen_rect.centery)
        self.rect.center = (self.x, self.y)
        
        # Movement physics
        self.heading = 0  # in degrees, 0 is up
        self.velocity = [0, 0]
        self.momentum = [0, 0]
        self.angular_velocity = 0  # Angular velocity for rotation
        self.image = self.original_image
        
        # Steering forces
        self.left_force = 0  # Force applied from left arrow (0-100)
        self.right_force = 0  # Force applied from right arrow (0-100)
        self.MAX_FORCE = 100
        self.FORCE_INCREMENT = 2  # Force added per tap
        
        # Physics constants
        self.MOMENTUM_DAMPING = 0.95
        self.ANGULAR_DAMPING = 0.98
        self.FORCE_TO_ROTATION = 0.1
        self.MAX_ANGULAR_VELOCITY = 5.0
        
        # Visual effects
        self.wake_particles = []
        self.MAX_WAKE_PARTICLES = 20
        
        # Click regions for touch controls
        self.left_click_region = pygame.Rect(0, 0, screen_rect.width // 2, screen_rect.height)
        self.right_click_region = pygame.Rect(screen_rect.width // 2, 0, 
                                            screen_rect.width // 2, screen_rect.height)
        
    def update(self, current_vector):
        """Update the boat's position based on forces and currents"""
        # Calculate net torque from forces
        net_torque = (self.right_force - self.left_force) * self.FORCE_TO_ROTATION
        
        # Update angular velocity with damping
        self.angular_velocity = (self.angular_velocity + net_torque) * self.ANGULAR_DAMPING
        
        # Clamp angular velocity
        self.angular_velocity = max(min(self.angular_velocity, self.MAX_ANGULAR_VELOCITY), 
                                  -self.MAX_ANGULAR_VELOCITY)
        
        # Update heading based on angular velocity
        self.heading += self.angular_velocity
        self.heading %= 360
        
        # Calculate boat forward movement vector
        forward_x = -math.sin(math.radians(self.heading)) * self.settings.BOAT_SPEED
        forward_y = -math.cos(math.radians(self.heading)) * self.settings.BOAT_SPEED
        
        # Update momentum with forces
        total_force = (self.left_force + self.right_force) / self.MAX_FORCE
        self.momentum[0] = (self.momentum[0] + forward_x * total_force) * self.MOMENTUM_DAMPING
        self.momentum[1] = (self.momentum[1] + forward_y * total_force) * self.MOMENTUM_DAMPING
        
        # Add current influence
        self.velocity[0] = self.momentum[0] + current_vector[0]
        self.velocity[1] = self.momentum[1] + current_vector[1]
        
        # Update position
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        
        # Update rect position
        self.rect.center = (self.screen_rect.centerx, self.screen_rect.centery)
        
        # Update wake particles
        self.update_wake()
        
        # Rotate image
        self.image = pygame.transform.rotate(self.original_image, self.heading)
        self.rect = self.image.get_rect(center=self.rect.center)
        
    def check_collision(self, islands):
        """Check for collision with islands"""
        boat_radius = self.rect.width // 2  # Simplified circular collision
        boat_center = (self.x, self.y)
        
        for island in islands:
            # Calculate distance to island center
            dx = self.x - island["x"]
            dy = self.y - island["y"]
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Check collision (using island size for radius)
            if distance < (island["size"] + boat_radius):
                return True
        return False
        
    def apply_force(self, side, force):
        """Apply force to either side of the boat"""
        if side == 'left':
            self.left_force = max(0, min(force, self.MAX_FORCE))
        else:
            self.right_force = max(0, min(force, self.MAX_FORCE))
    
    def add_force(self, side):
        """Add incremental force to one side"""
        if side == 'left':
            self.left_force = min(self.MAX_FORCE, self.left_force + self.FORCE_INCREMENT)
        else:
            self.right_force = min(self.MAX_FORCE, self.right_force + self.FORCE_INCREMENT)
    
    def update_wake(self):
        """Update boat wake particles"""
        if len(self.wake_particles) < self.MAX_WAKE_PARTICLES:
            wake_x = self.rect.centerx + math.sin(math.radians(self.heading)) * self.rect.height/2
            wake_y = self.rect.centery + math.cos(math.radians(self.heading)) * self.rect.height/2
            
            self.wake_particles.append({
                'pos': [wake_x, wake_y],
                'life': 1.0,
                'size': 5
            })
        
        for particle in self.wake_particles[:]:
            particle['life'] -= 0.02
            particle['size'] *= 0.95
            if particle['life'] <= 0:
                self.wake_particles.remove(particle)
    
    def draw(self, screen):
        """Draw the boat and its effects"""
        # Draw wake particles
        for particle in self.wake_particles:
            alpha = int(255 * particle['life'])
            wake_surf = pygame.Surface((int(particle['size']*2), int(particle['size']*2)), pygame.SRCALPHA)
            pygame.draw.circle(wake_surf, (255, 255, 255, alpha), 
                             (int(particle['size']), int(particle['size'])), 
                             int(particle['size']))
            screen.blit(wake_surf, (particle['pos'][0] - particle['size'], 
                                  particle['pos'][1] - particle['size']))
        
        # Draw the boat
        screen.blit(self.image, self.rect)
        
        # Draw force arrows
        self.draw_force_arrows(screen)
    
    def draw_force_arrows(self, screen):
        """Draw the force arrows for steering"""
        # Arrow dimensions
        arrow_width = 80
        arrow_height = 30
        spacing = 40  # Space between arrows
        base_y = self.rect.bottom + 50
        
        # Calculate positions for arrows pointing at each other
        left_x = self.rect.centerx - spacing
        right_x = self.rect.centerx + spacing
        
        # Colors based on force
        left_color = (255, int(255 * (1 - self.left_force/self.MAX_FORCE)), 0) if self.left_force > 0 else (100, 100, 100)
        right_color = (255, int(255 * (1 - self.right_force/self.MAX_FORCE)), 0) if self.right_force > 0 else (100, 100, 100)
        
        # Draw arrows pointing at each other
        # Left arrow (pointing right)
        pygame.draw.rect(screen, left_color, 
                        (left_x - arrow_width, base_y - arrow_height//2,
                         arrow_width, arrow_height))
        pygame.draw.polygon(screen, left_color, [
            (left_x, base_y),
            (left_x - 10, base_y - arrow_height//2 - 10),
            (left_x - 10, base_y + arrow_height//2 + 10)
        ])
        
        # Right arrow (pointing left)
        pygame.draw.rect(screen, right_color, 
                        (right_x, base_y - arrow_height//2,
                         arrow_width, arrow_height))
        pygame.draw.polygon(screen, right_color, [
            (right_x, base_y),
            (right_x + 10, base_y - arrow_height//2 - 10),
            (right_x + 10, base_y + arrow_height//2 + 10)
        ])
        
        # Draw force values
        font = pygame.font.SysFont(None, 30)
        for x, force, align in [(left_x - arrow_width//2, self.left_force, "right"),
                              (right_x + arrow_width//2, self.right_force, "left")]:
            force_text = f"{force:.0f}N"
            text = font.render(force_text, True, (255, 255, 255))
            text_rect = text.get_rect()
            if align == "right":
                text_rect.right = x
            else:
                text_rect.left = x
            text_rect.centery = base_y
            screen.blit(text, text_rect)
    
    def get_position(self):
        """Return the boat's global position"""
        return (self.x, self.y)
        
    def reset(self, screen_rect):
        """Reset the boat to starting position"""
        self.x = float(screen_rect.centerx)
        self.y = float(screen_rect.centery)
        self.heading = 0
        self.velocity = [0, 0]
        self.momentum = [0, 0]
        self.angular_velocity = 0
        self.left_force = 0
        self.right_force = 0
        self.wake_particles.clear()