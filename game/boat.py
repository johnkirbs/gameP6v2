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
                # Scale the image to smaller size
                self.original_image = pygame.transform.scale(self.original_image, (40, 60))  # Reduced from (60, 100)
                self.rect = self.original_image.get_rect()
            else:
                # Fallback to a simple boat shape if texture not found
                self.original_image = pygame.Surface((40, 60), pygame.SRCALPHA)  # Reduced size
                pygame.draw.polygon(self.original_image, settings.WHITE, 
                                   [(20, 0), (40, 50), (20, 45), (0, 50)])  # Adjusted points for smaller size
                self.rect = self.original_image.get_rect()
        except Exception as e:
            print(f"Boat image loading error: {e}. Using fallback.")
            # Fallback to a simple boat shape
            self.original_image = pygame.Surface((40, 60), pygame.SRCALPHA)  # Reduced size
            pygame.draw.polygon(self.original_image, settings.WHITE, 
                               [(20, 0), (40, 50), (20, 45), (0, 50)])  # Adjusted points
            self.rect = self.original_image.get_rect()
        
        # Position the boat at the center of the screen
        self.x = float(screen_rect.centerx)
        self.y = float(screen_rect.centery)
        self.rect.center = (self.x, self.y)
        
        # Movement physics
        self.heading = 0  # in degrees, 0 is up
        self.velocity = [0, 0]
        self.momentum = [0, 0]
        self.angular_velocity = 0
        self.image = self.original_image
        
        # Initialize all forces to 0
        self.left_force = 0
        self.right_force = 0
        self.forward_force = 0
        self.backward_force = 0
        self.MAX_FORCE = 100
        self.FORCE_INCREMENT = 1
        
        # Control state
        self.left_active = False
        self.right_active = False
        self.forward_active = False
        self.backward_active = False
        self.is_docked = True  # Start docked
        
        # Click regions
        self.arrow_width = 30
        self.arrow_height = 15
        self.spacing = 60
        
        # Initialize click regions
        self.left_click_region = pygame.Rect(0, 0, 0, 0)
        self.right_click_region = pygame.Rect(0, 0, 0, 0)
        self.forward_click_region = pygame.Rect(0, 0, 0, 0)
        self.backward_click_region = pygame.Rect(0, 0, 0, 0)
        
        # Wake particles
        self.wake_particles = []
        self.MAX_WAKE_PARTICLES = 20
        
        # Force display
        self.show_force = False
        self.force_display_time = 0
        self.FORCE_DISPLAY_DURATION = 1000
        
        # Update click regions initially
        self.update_click_regions()
        
    def handle_keydown(self, event):
        """Handle key press events"""
        if self.is_docked and event.key != pygame.K_UP:
            return  # Ignore all controls except UP when docked
        
        if event.key == pygame.K_LEFT:
            if not self.left_active:
                # If right force exists, reduce it first
                if self.right_force > 0:
                    self.right_force = max(0, self.right_force - self.FORCE_INCREMENT)
                else:
                    self.left_force = min(self.MAX_FORCE, self.left_force + self.FORCE_INCREMENT)
            self.left_active = True
        elif event.key == pygame.K_RIGHT:
            if not self.right_active:
                # If left force exists, reduce it first
                if self.left_force > 0:
                    self.left_force = max(0, self.left_force - self.FORCE_INCREMENT)
                else:
                    self.right_force = min(self.MAX_FORCE, self.right_force + self.FORCE_INCREMENT)
            self.right_active = True
        elif event.key == pygame.K_UP:
            if not self.forward_active:
                # If backward force exists, reduce it first
                if self.backward_force > 0:
                    self.backward_force = max(0, self.backward_force - self.FORCE_INCREMENT)
                else:
                    self.forward_force = min(self.MAX_FORCE, self.forward_force + self.FORCE_INCREMENT)
            self.forward_active = True
        elif event.key == pygame.K_DOWN:
            if not self.backward_active:
                # If forward force exists, reduce it first
                if self.forward_force > 0:
                    self.forward_force = max(0, self.forward_force - self.FORCE_INCREMENT)
                else:
                    self.backward_force = min(self.MAX_FORCE, self.backward_force + self.FORCE_INCREMENT)
            self.backward_active = True
        # Rotation controls
        elif event.key == pygame.K_q:  # Q to rotate left
            self.heading = (self.heading + 2) % 360
        elif event.key == pygame.K_e:  # E to rotate right
            self.heading = (self.heading - 2) % 360
    
    def handle_keyup(self, key):
        """Handle key release events"""
        if key == pygame.K_LEFT:
            self.left_active = False
        elif key == pygame.K_RIGHT:
            self.right_active = False
        elif key == pygame.K_UP:
            self.forward_active = False
        elif key == pygame.K_DOWN:
            self.backward_active = False
    
    def handle_mouse_click(self, pos):
        """Handle mouse click events"""
        if self.is_docked:
            return  # Ignore mouse clicks when docked
        
        try:
            if not all([self.left_click_region, self.right_click_region, 
                       self.forward_click_region, self.backward_click_region]):
                self.update_click_regions()
                return
            
            x, y = pos
            
            # Show force display when clicking
            self.show_force = True
            self.force_display_time = pygame.time.get_ticks()
            
            if self.left_click_region.collidepoint(x, y):
                self._handle_left_click()
            elif self.right_click_region.collidepoint(x, y):
                self._handle_right_click()
            elif self.forward_click_region.collidepoint(x, y):
                self._handle_forward_click()
            elif self.backward_click_region.collidepoint(x, y):
                self._handle_backward_click()
                
        except Exception as e:
            print(f"Error handling mouse click: {e}")
            self._reset_controls()

    def _handle_left_click(self):
        """Handle left arrow click"""
        if not self.left_active:
            if self.right_force > 0:
                self.right_force = max(0, self.right_force - self.FORCE_INCREMENT)
            self.left_force = min(self.MAX_FORCE, self.left_force + self.FORCE_INCREMENT)
        self.left_active = True
        self.right_active = False

    def _handle_right_click(self):
        """Handle right arrow click"""
        if not self.right_active:
            if self.left_force > 0:
                self.left_force = max(0, self.left_force - self.FORCE_INCREMENT)
            self.right_force = min(self.MAX_FORCE, self.right_force + self.FORCE_INCREMENT)
        self.right_active = True
        self.left_active = False

    def _handle_forward_click(self):
        """Handle forward arrow click"""
        if not self.forward_active:
            if self.backward_force > 0:
                self.backward_force = max(0, self.backward_force - self.FORCE_INCREMENT)
            self.forward_force = min(self.MAX_FORCE, self.forward_force + self.FORCE_INCREMENT)
        self.forward_active = True
        self.backward_active = False

    def _handle_backward_click(self):
        """Handle backward arrow click"""
        if not self.backward_active:
            if self.forward_force > 0:
                self.forward_force = max(0, self.forward_force - self.FORCE_INCREMENT)
            self.backward_force = min(self.MAX_FORCE, self.backward_force + self.FORCE_INCREMENT)
        self.backward_active = True
        self.forward_active = False

    def _reset_controls(self):
        """Reset all control states"""
        self.left_active = False
        self.right_active = False
        self.forward_active = False
        self.backward_active = False
        self.left_force = 0
        self.right_force = 0
        self.forward_force = 0
        self.backward_force = 0

    def update_click_regions(self):
        """Update click regions to match current boat position"""
        try:
            # Get screen dimensions from rect
            screen_width = self.screen_rect.width
            screen_height = self.screen_rect.height
            
            # Calculate base positions
            base_y = self.rect.centery
            center_x = self.rect.centerx
            
            # Calculate arrow positions with fixed spacing from center
            self.spacing = min(60, screen_width // 6)  # Adjust spacing based on screen size
            
            # Calculate positions with spacing
            left_x = center_x - self.spacing
            right_x = center_x + self.spacing
            up_y = base_y - self.spacing
            down_y = base_y + self.spacing
            
            # Ensure click regions stay within screen bounds with padding
            padding = 10
            left_x = max(padding, min(left_x, screen_width - self.arrow_width - padding))
            right_x = max(padding, min(right_x, screen_width - self.arrow_width - padding))
            up_y = max(padding, min(up_y, screen_height - self.arrow_width - padding))
            down_y = max(padding, min(down_y, screen_height - self.arrow_width - padding))
            
            # Update click regions with fixed sizes and proper positioning
            self.left_click_region = pygame.Rect(
                left_x - self.arrow_width,
                base_y - self.arrow_height//2,
                self.arrow_width + 10,  # Slightly wider for better clicking
                self.arrow_height + 10   # Slightly taller for better clicking
            )
            
            self.right_click_region = pygame.Rect(
                right_x,
                base_y - self.arrow_height//2,
                self.arrow_width + 10,
                self.arrow_height + 10
            )
            
            self.forward_click_region = pygame.Rect(
                center_x - self.arrow_height//2,
                up_y - self.arrow_width//2,
                self.arrow_height + 10,
                self.arrow_width + 10
            )
            
            self.backward_click_region = pygame.Rect(
                center_x - self.arrow_height//2,
                down_y,
                self.arrow_height + 10,
                self.arrow_width + 10
            )
            
            print("Debug: Click regions updated successfully")
        except Exception as e:
            print(f"Debug: Error updating click regions: {e}")

    def update(self, current_vector):
        """Update the boat's position based on forces and currents"""
        try:
            if self.is_docked:
                # When docked, only allow rotation and keep position fixed
                self.velocity = [0, 0]
                self.momentum = [0, 0]
                return
            
            # Calculate directional forces with smoother transitions
            horizontal_force = (self.left_force - self.right_force) / self.MAX_FORCE
            vertical_force = (self.backward_force - self.forward_force) / self.MAX_FORCE
            
            # Calculate movement vectors with improved precision
            movement_x = horizontal_force * self.settings.BOAT_SPEED
            movement_y = vertical_force * self.settings.BOAT_SPEED
            
            # Calculate current velocity magnitude
            current_speed = math.sqrt(self.velocity[0]**2 + self.velocity[1]**2)
            
            # Apply appropriate damping based on speed
            if current_speed > 5.0:
                damping = 0.90
            else:
                damping = 0.98
            
            # Update momentum with movement forces and dynamic damping
            self.momentum[0] = (self.momentum[0] + movement_x) * damping
            self.momentum[1] = (self.momentum[1] + movement_y) * damping
            
            # Add current influence
            self.velocity[0] = self.momentum[0] + current_vector[0]
            self.velocity[1] = self.momentum[1] + current_vector[1]
            
            # Update position
            self.x += self.velocity[0]
            self.y += self.velocity[1]
            
            # Update rect position
            self.rect.center = (self.screen_rect.centerx, self.screen_rect.centery)
            
            # Update wake particles only when moving
            if current_speed > 0.1:
                self.update_wake()
            
            # Rotate boat image based on heading
            self.image = pygame.transform.rotate(self.original_image, self.heading)
            self.rect = self.image.get_rect(center=self.rect.center)
            
            # Update click regions to match new position
            self.update_click_regions()
            
        except Exception as e:
            print(f"Error updating boat: {e}")
            self._reset_controls()
    
    def check_collision(self, islands):
        """Check for collision with islands"""
        boat_radius = self.rect.width // 2  # Simplified circular collision
        boat_center = (self.x, self.y)
        
        # Calculate current velocity magnitude
        current_speed = math.sqrt(self.velocity[0]**2 + self.velocity[1]**2)
        MAX_DOCKING_SPEED = 2.0  # Maximum safe speed for docking
        MAX_SAFE_SPEED = 8.0  # Maximum safe speed for general navigation
        
        # Check for excessive speed first
        if current_speed > MAX_SAFE_SPEED:
            return "crash_speed_general"  # New result for general high-speed crash
        
        for island in islands:
            # Calculate distance to island center
            dx = self.x - island["x"]
            dy = self.y - island["y"]
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Check collision (using island size for radius)
            if distance < (island["size"] + boat_radius):
                # Always check speed first when colliding with any island
                if current_speed > MAX_DOCKING_SPEED:
                    return "crash_speed_dock"  # High-speed collision with any island
                    
                # Only then check island type
                if island["type"] == "target_island":
                    return "dock_success"
                elif island["type"] == "rock":
                    return "collision"
                else:
                    return "dock_fail"
        return "no_collision"
        
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
        # Position arrows relative to boat center
        base_y = self.rect.centery
        left_x = self.rect.centerx - self.spacing
        right_x = self.rect.centerx + self.spacing
        up_y = base_y - self.spacing
        down_y = base_y + self.spacing
        
        # Colors based on active state and force
        left_color = (255, int(255 * (1 - self.left_force/self.MAX_FORCE)), 0) if self.left_active else (180, 180, 180)
        right_color = (255, int(255 * (1 - self.right_force/self.MAX_FORCE)), 0) if self.right_active else (180, 180, 180)
        forward_color = (255, int(255 * (1 - self.forward_force/self.MAX_FORCE)), 0) if self.forward_active else (180, 180, 180)
        backward_color = (255, int(255 * (1 - self.backward_force/self.MAX_FORCE)), 0) if self.backward_active else (180, 180, 180)
        
        def draw_arrow(surface, color, start_pos, end_pos, width=3):
            """Draw an arrow from start_pos to end_pos"""
            pygame.draw.line(surface, color, start_pos, end_pos, width)
            # Calculate arrow head
            angle = math.atan2(end_pos[1] - start_pos[1], end_pos[0] - start_pos[0])
            arrow_size = 10
            angle_left = angle + math.pi/6
            angle_right = angle - math.pi/6
            
            # Arrow head points
            head_left = (
                end_pos[0] - arrow_size * math.cos(angle_left),
                end_pos[1] - arrow_size * math.sin(angle_left)
            )
            head_right = (
                end_pos[0] - arrow_size * math.cos(angle_right),
                end_pos[1] - arrow_size * math.sin(angle_right)
            )
            
            # Draw arrow head
            pygame.draw.polygon(surface, color, [end_pos, head_left, head_right])
        
        def draw_control_arrow(center_pos, direction, color, active):
            """Draw a control arrow with background and glow effect"""
            arrow_length = 25
            if direction == "left":
                # Point towards boat (right to left)
                start_pos = (center_pos[0] + arrow_length, center_pos[1])
                end_pos = (center_pos[0] - arrow_length, center_pos[1])
            elif direction == "right":
                # Point towards boat (left to right)
                start_pos = (center_pos[0] - arrow_length, center_pos[1])
                end_pos = (center_pos[0] + arrow_length, center_pos[1])
            elif direction == "up":
                start_pos = (center_pos[0], center_pos[1] + arrow_length)
                end_pos = (center_pos[0], center_pos[1] - arrow_length)
            else:  # down
                start_pos = (center_pos[0], center_pos[1] - arrow_length)
                end_pos = (center_pos[0], center_pos[1] + arrow_length)
            
            # Draw glow effect if active
            if active:
                glow_surf = pygame.Surface((arrow_length * 3, arrow_length * 3), pygame.SRCALPHA)
                glow_color = (*color[:3], 50)  # Semi-transparent version of the color
                draw_arrow(glow_surf, glow_color, 
                          (glow_surf.get_width()//2, glow_surf.get_height()//2),
                          (glow_surf.get_width()//2 + (end_pos[0] - start_pos[0]),
                           glow_surf.get_height()//2 + (end_pos[1] - start_pos[1])), width=5)
                screen.blit(glow_surf, 
                           (start_pos[0] - glow_surf.get_width()//2,
                            start_pos[1] - glow_surf.get_height()//2))
            
            # Draw main arrow
            draw_arrow(screen, color, start_pos, end_pos)
        
        # Draw the control arrows
        draw_control_arrow((left_x, base_y), "left", left_color, self.left_active)
        draw_control_arrow((right_x, base_y), "right", right_color, self.right_active)
        draw_control_arrow((self.rect.centerx, up_y), "up", forward_color, self.forward_active)
        draw_control_arrow((self.rect.centerx, down_y), "down", backward_color, self.backward_active)
        
        # Draw force values with current speed
        font = pygame.font.SysFont(None, 20)
        
        def draw_force_text(force, pos):
            text = font.render(f"{force:.0f}N", True, (255, 255, 255))
            text_rect = text.get_rect(center=pos)
            pygame.draw.rect(screen, (0, 0, 0), text_rect.inflate(4, 4))
            screen.blit(text, text_rect)
        
        # Draw force values
        draw_force_text(self.left_force, (left_x - self.arrow_width - 20, base_y))
        draw_force_text(self.right_force, (right_x + self.arrow_width + 20, base_y))
        draw_force_text(self.forward_force, (self.rect.centerx, up_y - 20))
        draw_force_text(self.backward_force, (self.rect.centerx, down_y + 20))
        
        # Draw current speed
        current_speed = math.sqrt(self.velocity[0]**2 + self.velocity[1]**2)
        speed_color = (255, 255, 255) if current_speed <= 2.0 else (255, 165, 0) if current_speed <= 8.0 else (255, 0, 0)
        speed_text = font.render(f"Speed: {current_speed:.1f}", True, speed_color)
        speed_rect = speed_text.get_rect(center=(self.rect.centerx, self.rect.centery - 40))
        pygame.draw.rect(screen, (0, 0, 0), speed_rect.inflate(4, 4))
        screen.blit(speed_text, speed_rect)
    
    def get_position(self):
        """Return the boat's global position"""
        return (self.x, self.y)
        
    def reset(self, screen_rect):
        """Reset boat to initial state"""
        print("Debug: Resetting boat state")
        self.x = float(screen_rect.centerx)
        self.y = float(screen_rect.centery)
        self.rect.center = (self.x, self.y)
        self.heading = 0
        self.velocity = [0, 0]
        self.momentum = [0, 0]
        self.angular_velocity = 0
        
        # Reset all forces
        self.left_force = 0
        self.right_force = 0
        self.forward_force = 0
        self.backward_force = 0
        
        # Reset control states
        self.left_active = False
        self.right_active = False
        self.forward_active = False
        self.backward_active = False
        
        # Clear wake particles
        self.wake_particles.clear()
        
        # Reset force display
        self.show_force = False
        self.force_display_time = 0
        
        # Ensure click regions are properly initialized
        self.screen_rect = screen_rect  # Update screen_rect reference
        self.update_click_regions()
        
        # Update the boat image
        self.image = pygame.transform.rotate(self.original_image, self.heading)
        self.rect = self.image.get_rect(center=self.rect.center)
        
        print("Debug: Boat reset complete")

    def adjust_power(self, increase):
        """Adjust the boat's power level"""
        if increase:
            self.power_level = min(self.MAX_POWER, self.power_level + self.POWER_INCREMENT)
        else:
            self.power_level = max(self.MIN_POWER, self.power_level - self.POWER_INCREMENT)

    def get_velocity(self):
        """Get the current velocity of the boat"""
        return self.velocity

    def reset_controls(self):
        """Reset all control states"""
        self.left_active = False
        self.right_active = False
        self.forward_active = False
        self.backward_active = False