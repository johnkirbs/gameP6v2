import pygame
import math
from game.boat import Boat
from game.wave import WaveGenerator
from game.player import Player
import sys

class GameEngine:
    """Main game engine that coordinates all game elements"""
    
    def __init__(self, settings):
        """Initialize the game engine"""
        self.settings = settings
        
        # Set up the display
        self.screen = pygame.display.set_mode(
            (settings.SCREEN_WIDTH, settings.SCREEN_HEIGHT)
        )
        pygame.display.set_caption(settings.SCREEN_TITLE)
        
        # Game state variables
        self.show_current_notification = False
        self.is_docked = True  # Start docked
        self.game_paused = True  # Start paused with instructions
        self.notification_start_time = 0
        self.current_notification = ""
        self.warning_message = ""
        self.warning_start_time = 0
        self.show_warning = False
        self.game_state = "instructions"  # New state for initial instructions
        self.instruction_shown = False
        
        # Initialize world position at center
        self.world_pos = [0, 0]
        
        # Background and world coordinates
        self.background_offset = [0, 0]
        
        # Check if assets directory exists, if not create it
        import os
        if not os.path.exists("assets"):
            os.makedirs("assets")
        if not os.path.exists("assets/textures"):
            os.makedirs("assets/textures")
        
        try:
            # Try to load background texture
            if os.path.exists(settings.BACKGROUND_TEXTURE):
                self.background = pygame.image.load(settings.BACKGROUND_TEXTURE)
                # Create a repeating background
                bg_width, bg_height = self.background.get_size()
                self.background_large = pygame.Surface((bg_width * 5, bg_height * 5))
                for x in range(0, 5):
                    for y in range(0, 5):
                        self.background_large.blit(self.background, (x * bg_width, y * bg_height))
            else:
                # Fallback to a simple background if texture not found
                self.background_large = pygame.Surface((settings.SCREEN_WIDTH * 5, settings.SCREEN_HEIGHT * 5))
                self.background_large.fill(settings.DARK_BLUE)
                # Draw some wave lines
                for y in range(0, settings.SCREEN_HEIGHT * 5, 20):
                    pygame.draw.line(self.background_large, settings.BLUE, 
                                   (0, y), (settings.SCREEN_WIDTH * 5, y), 2)
        except Exception as e:
            print(f"Background loading error: {e}. Using fallback.")
            # Fallback to a simple background
            self.background_large = pygame.Surface((settings.SCREEN_WIDTH * 5, settings.SCREEN_HEIGHT * 5))
            self.background_large.fill(settings.DARK_BLUE)
            # Add subtle grid for motion reference
            grid_spacing = 100
            for x in range(0, settings.SCREEN_WIDTH * 5, grid_spacing):
                pygame.draw.line(self.background_large, (0, 70, 130), 
                               (x, 0), (x, settings.SCREEN_HEIGHT * 5), 1)
            for y in range(0, settings.SCREEN_HEIGHT * 5, grid_spacing):
                pygame.draw.line(self.background_large, (0, 70, 130), 
                               (0, y), (settings.SCREEN_WIDTH * 5, y), 1)
        
        # Generate world features
        self.generate_world_features()
        
        # Initialize game components
        self.boat = Boat(settings, self.screen.get_rect())
        self.wave_generator = WaveGenerator(settings)
        self.player = Player(self.boat)
        
        # Game state
        self.game_state = "playing"  # Can be "playing", "win", "fail", "restart"
        self.restart_requested = False
        self.success_start_time = 0
        
        # Target island
        self.island_pos = [self.settings.ISLAND_DISTANCE_MIN, 0]  # Relative to start position
        try:
            if os.path.exists(settings.ISLAND_TEXTURE):
                self.island_image = pygame.image.load(settings.ISLAND_TEXTURE)
                self.island_rect = self.island_image.get_rect()
            else:
                # Fallback island
                self.island_image = pygame.Surface((settings.ISLAND_RADIUS * 2, settings.ISLAND_RADIUS * 2), pygame.SRCALPHA)
                pygame.draw.circle(self.island_image, settings.GREEN, 
                                  (settings.ISLAND_RADIUS, settings.ISLAND_RADIUS), settings.ISLAND_RADIUS)
                self.island_rect = self.island_image.get_rect()
        except Exception as e:
            print(f"Island image loading error: {e}. Using fallback.")
            # Fallback island
            self.island_image = pygame.Surface((settings.ISLAND_RADIUS * 2, settings.ISLAND_RADIUS * 2), pygame.SRCALPHA)
            pygame.draw.circle(self.island_image, settings.GREEN, 
                              (settings.ISLAND_RADIUS, settings.ISLAND_RADIUS), settings.ISLAND_RADIUS)
            self.island_rect = self.island_image.get_rect()
        
        # Font for UI elements
        self.font = pygame.font.SysFont(None, 30)
        
        # Navigation arrow settings
        self.nav_arrow_size = 40
        self.nav_arrow_color = (255, 255, 0)  # Yellow
        self.nav_arrow_distance = 100  # Distance from boat center
        
    def handle_event(self, event):
        """Handle game events"""
        try:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r and (self.game_state == "fail" or self.game_state == "win"):
                    self.restart_game()
                    return
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                    
                if self.game_state == "instructions":
                    self.game_state = "playing"
                    self.show_current_notification = True
                    self.current_notification = "Press UP arrow to undock the boat and start your journey!"
                    self.notification_start_time = pygame.time.get_ticks()
                    return
                    
                if self.game_state == "playing":
                    if self.show_current_notification:
                        self.show_current_notification = False
                        self.game_paused = False
                        if not self.instruction_shown:
                            self.instruction_shown = True
                            self.show_current_notification = True
                            self.current_notification = f"Current detected! Magnitude: {self.wave_generator.get_magnitude():.1f}, Direction: {self.wave_generator.get_direction()}°"
                            self.notification_start_time = pygame.time.get_ticks()
                        return
                    
                    if self.is_docked and (event.key in [pygame.K_UP, pygame.K_w]):
                        self.is_docked = False
                        self.show_current_notification = True
                        self.game_paused = True
                        self.current_notification = "Boat undocked! Navigate carefully through the currents."
                        self.notification_start_time = pygame.time.get_ticks()
                    elif not self.is_docked and hasattr(self, 'boat'):
                        self.boat.handle_keydown(event.key)
            
            elif event.type == pygame.KEYUP and self.game_state == "playing" and not self.is_docked:
                if hasattr(self, 'boat'):
                    self.boat.handle_keyup(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.show_current_notification:
                    self.show_current_notification = False
                    self.game_paused = False
                elif self.game_state == "playing" and not self.is_docked and hasattr(self, 'boat'):
                    # Validate mouse position is within screen bounds
                    if (0 <= event.pos[0] <= self.settings.SCREEN_WIDTH and 
                        0 <= event.pos[1] <= self.settings.SCREEN_HEIGHT):
                        self.boat.handle_mouse_click(event.pos)
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                # Reset all active states on mouse release
                if self.game_state == "playing" and not self.is_docked and hasattr(self, 'boat'):
                    self.boat.left_active = False
                    self.boat.right_active = False
                    self.boat.forward_active = False
                    self.boat.backward_active = False
        except Exception as e:
            print(f"Error handling event: {e}")
            # If there's an error, try to recover by resetting game state
            if hasattr(self, 'boat'):
                self.boat.left_active = False
                self.boat.right_active = False
                self.boat.forward_active = False
                self.boat.backward_active = False
    
    def generate_world_features(self):
        """Generate random world features"""
        import random
        
        # Clear existing features
        self.settings.SEA_FEATURES = []
        
        # Generate random islands (3-5)
        num_islands = random.randint(3, 5)
        for _ in range(num_islands):
            distance = random.uniform(self.settings.ISLAND_DISTANCE_MIN * 0.7,
                                   self.settings.ISLAND_DISTANCE_MAX * 0.8)
            angle = random.uniform(0, 2 * math.pi)
            self.settings.SEA_FEATURES.append({
                "type": "island",
                "x": distance * math.cos(angle),
                "y": distance * math.sin(angle),
                "size": random.randint(30, 50)
            })
        
        # Generate trees on islands (2-4 per island)
        for island in self.settings.SEA_FEATURES:
            if island["type"] == "island":
                num_trees = random.randint(2, 4)
                for _ in range(num_trees):
                    tree_angle = random.uniform(0, 2 * math.pi)
                    tree_distance = island["size"] * 0.6
                    self.settings.SEA_FEATURES.append({
                        "type": "tree",
                        "x": island["x"] + tree_distance * math.cos(tree_angle),
                        "y": island["y"] + tree_distance * math.sin(tree_angle),
                        "size": random.randint(10, 15)
                    })
        
        # Generate other boats (2-3)
        num_boats = random.randint(2, 3)
        for _ in range(num_boats):
            distance = random.uniform(self.settings.ISLAND_DISTANCE_MIN * 0.4,
                                   self.settings.ISLAND_DISTANCE_MAX * 0.6)
            angle = random.uniform(0, 2 * math.pi)
            self.settings.SEA_FEATURES.append({
                "type": "other_boat",
                "x": distance * math.cos(angle),
                "y": distance * math.sin(angle),
                "size": 20,
                "heading": random.randint(0, 359)
            })
        
        # Generate the target island last to ensure it's properly placed
        self._generate_target_island()
        
        # Add target island to features
        self.all_features = self.settings.SEA_FEATURES.copy()
        self.all_features.append({
            "type": "target_island",
            "x": self.target_pos[0],
            "y": self.target_pos[1],
            "size": self.settings.ISLAND_RADIUS,
        })
    
    def _generate_target_island(self):
        """Generate a random position for the target island"""
        import random
        
        # Keep trying until we find a valid position
        while True:
            # Random distance between min and max
            distance = random.uniform(self.settings.ISLAND_DISTANCE_MIN,
                                   self.settings.ISLAND_DISTANCE_MAX)
            # Random angle
            angle = random.uniform(0, 2 * math.pi)
            
            # Calculate position
            x = distance * math.cos(angle)
            y = distance * math.sin(angle)
            
            # Check if position is far enough from other features
            valid = True
            min_distance = 200  # Minimum distance from other features
            
            for feature in self.settings.SEA_FEATURES:
                dx = x - feature["x"]
                dy = y - feature["y"]
                dist = math.sqrt(dx*dx + dy*dy)
                if dist < min_distance:
                    valid = False
                    break
            
            if valid:
                self.target_pos = [x, y]
                break
    
    def restart_game(self):
        """Restart the game with new settings"""
        # Reset world position to center
        self.world_pos = [0, 0]
        
        # Generate new world features
        self.generate_world_features()
        
        # Reset boat position and state
        if hasattr(self, 'boat'):
            self.boat.reset(self.screen.get_rect())
        
        # Change current direction randomly
        import random
        self.settings.CURRENT_DIRECTION = random.randint(0, 359)
        self.wave_generator = WaveGenerator(self.settings)
        
        # Reset game state
        self.game_state = "playing"
        self.success_start_time = 0
        self.is_docked = True
        self.show_current_notification = True
        self.current_notification = "Press UP arrow to undock the boat and start your journey!"
        self.notification_start_time = pygame.time.get_ticks()
        self.game_paused = True
        self.instruction_shown = False
    
    def update(self):
        """Update game state"""
        current_time = pygame.time.get_ticks()
        
        # Handle notifications timing
        if self.show_current_notification and current_time - self.notification_start_time > 2000:
            self.show_current_notification = False
            self.game_paused = False
        
        # Handle warning timing
        if self.show_warning and current_time - self.warning_start_time > 2000:
            self.show_warning = False
        
        if self.game_state == "win":
            if current_time - self.success_start_time > self.settings.SUCCESS_FLASH_DURATION:
                self.game_state = "menu"
            return
        elif self.game_state != "playing" or self.game_paused:
            return
            
        # Update game components
        self.wave_generator.update()
        
        if hasattr(self, 'boat'):
            # Get current vector before boat update
            current_vector = self.wave_generator.get_current_vector()
            
            # Update boat
            self.boat.update(current_vector)
            
            # Check for high velocity warning
            velocity = self.boat.get_velocity()
            if abs(velocity[0]) > 2 or abs(velocity[1]) > 2:
                self.show_warning = True
                self.warning_message = "Warning: High velocity detected!"
                self.warning_start_time = current_time
        
        # Update world position
        boat_pos = self.boat.get_position()
        self.world_pos[0] = boat_pos[0]
        self.world_pos[1] = boat_pos[1]
        
        # Check collisions with all features
        boat_radius = self.boat.rect.width // 2
        boat_center = (self.world_pos[0], self.world_pos[1])
        
        for feature in self.all_features:
            # Calculate distance to feature center
            dx = self.world_pos[0] - feature["x"]
            dy = self.world_pos[1] - feature["y"]
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Check collision
            if distance < (feature["size"] + boat_radius):
                if feature["type"] == "target_island":
                    self.game_state = "win"
                    self.success_start_time = pygame.time.get_ticks()
                else:
                    self.game_state = "fail"
                return
        
        # Update background offset for tiling
        self.background_offset[0] = -(self.world_pos[0] % self.background_large.get_width())
        self.background_offset[1] = -(self.world_pos[1] % self.background_large.get_height())
        
    def draw(self):
        """Draw the game state"""
        # Clear the screen first
        self.screen.fill(self.settings.BLACK)
        
        if self.game_state == "instructions":
            instructions = [
                "Welcome to the Boat Navigation Game!",
                "",
                "Instructions:",
                "- Your boat starts docked at the center",
                "- Press UP arrow to undock and begin",
                "- Use arrow keys to control the boat",
                "- Navigate to the glowing target island",
                "- Avoid other islands and watch for currents",
                "- Press ESC to exit anytime",
                "",
                "Press any key to continue..."
            ]
            
            y_offset = self.settings.SCREEN_HEIGHT // 4
            for line in instructions:
                self._draw_message(line, self.settings.WHITE, y_offset)
                y_offset += 40
            return
            
        if self.game_state == "fail":
            self._draw_message("You docked at the wrong island!", self.settings.RED)
            self._draw_message("Press R to restart or ESC to exit", self.settings.WHITE, 
                             self.settings.SCREEN_HEIGHT // 2 + 50)
            return
            
        if self.game_state == "win":
            self._draw_message_with_glow("Congratulations! You reached the target island!", 
                                       self.settings.GOLD)
            self._draw_message("Press R to play again or ESC to exit", self.settings.WHITE,
                             self.settings.SCREEN_HEIGHT // 2 + 50)
            return
            
        # Only draw game elements if in playing state
        if self.game_state == "playing":
            self.screen.blit(self.background_large, self.background_offset)
            self._draw_features()
            
            try:
                self.wave_generator.draw_indicator(self.screen, self.boat.rect)
                self.boat.draw(self.screen)
                self._draw_navigation_arrow()
                self._draw_ui()
            except Exception as e:
                print(f"Error during game rendering: {e}")
            
            # Draw current notification if active
            if self.show_current_notification:
                self._draw_notification(self.current_notification)
            
            # Draw warning if active
            if self.show_warning:
                self._draw_warning(self.warning_message)
    
    def _world_to_screen(self, world_pos):
        """Convert world coordinates to screen coordinates"""
        screen_x = self.screen.get_rect().centerx - (self.world_pos[0] - world_pos[0])
        screen_y = self.screen.get_rect().centery - (self.world_pos[1] - world_pos[1])
        return (screen_x, screen_y)
        
    def _draw_ui(self):
        """Draw UI elements like distance indicator"""
        # Calculate distance to target
        dx = self.target_pos[0] - self.world_pos[0]
        dy = self.target_pos[1] - self.world_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Draw distance text
        distance_text = f"Distance: {int(distance)} m"
        font = pygame.font.SysFont(None, 30)
        text_surface = font.render(distance_text, True, self.settings.WHITE)
        self.screen.blit(text_surface, (10, 10))
        
        # Draw direction indicator to target (compass style)
        indicator_radius = 45
        center_x = self.settings.SCREEN_WIDTH - indicator_radius - 20
        center_y = indicator_radius + 20
        
        # Draw outer circle with better visibility
        pygame.draw.circle(self.screen, (80, 80, 80), (center_x, center_y), indicator_radius + 2)  # Shadow
        pygame.draw.circle(self.screen, self.settings.WHITE, (center_x, center_y), indicator_radius)
        pygame.draw.circle(self.screen, (220, 220, 220), (center_x, center_y), indicator_radius - 2)  # Inner circle
        
        # Calculate angle to target
        angle = math.degrees(math.atan2(dy, dx))
        
        # Adjust for boat heading (so indicator shows relative direction)
        relative_angle = angle - self.boat.heading + 90
        
        # Draw compass cardinal points
        cardinal_points = [("N", 0), ("E", 90), ("S", 180), ("W", 270)]
        for label, degrees in cardinal_points:
            point_x = center_x + math.cos(math.radians(degrees)) * (indicator_radius - 10)
            point_y = center_y + math.sin(math.radians(degrees)) * (indicator_radius - 10)
            small_font = pygame.font.SysFont(None, 20)
            cardinal = small_font.render(label, True, (80, 80, 80))
            self.screen.blit(cardinal, (point_x - cardinal.get_width()//2, point_y - cardinal.get_height()//2))
        
        # Draw target direction arrow
        arrow_length = indicator_radius - 5
        arrow_color = self.settings.GOLD
        
        # Make arrow pulse based on distance
        pulse = math.sin(pygame.time.get_ticks() / 300) * 0.2 + 0.8
        if distance < 300:
            # Make arrow blink faster when close to target
            if (pygame.time.get_ticks() % 1000) > 500:
                arrow_color = (250, 250, 50)  # Yellow
        
        # Draw direction arrow
        endpoint_x = center_x + math.cos(math.radians(relative_angle)) * arrow_length * pulse
        endpoint_y = center_y + math.sin(math.radians(relative_angle)) * arrow_length * pulse
        
        # Draw arrow with thickness
        pygame.draw.line(self.screen, (0, 0, 0), (center_x, center_y), (endpoint_x, endpoint_y), 5)  # Shadow
        pygame.draw.line(self.screen, arrow_color, (center_x, center_y), (endpoint_x, endpoint_y), 3)
        
        # Draw arrowhead
        arrowhead_size = 7
        pygame.draw.circle(self.screen, (0, 0, 0), (int(endpoint_x), int(endpoint_y)), arrowhead_size+1)  # Shadow
        pygame.draw.circle(self.screen, arrow_color, (int(endpoint_x), int(endpoint_y)), arrowhead_size)
        
        # Label
        label = font.render("Target", True, self.settings.WHITE)
        self.screen.blit(label, (center_x - label.get_width() // 2, center_y - indicator_radius - 30))
        
        # Add mini version of distance
        mini_dist = font.render(f"{int(distance)}m", True, self.settings.WHITE)
        self.screen.blit(mini_dist, (center_x - mini_dist.get_width() // 2, center_y + indicator_radius + 5))
    
    def _draw_message(self, message, color, y_offset=None):
        """Draw a centered message on the screen"""
        font = pygame.font.SysFont(None, 36)
        text_surface = font.render(message, True, color)
        
        if y_offset is None:
            # Center vertically if no y_offset provided
            text_rect = text_surface.get_rect(center=(self.settings.SCREEN_WIDTH // 2, 
                                                    self.settings.SCREEN_HEIGHT // 2))
        else:
            # Use provided y_offset
            text_rect = text_surface.get_rect(center=(self.settings.SCREEN_WIDTH // 2, y_offset))
        
        # Draw semi-transparent background
        bg_rect = text_rect.inflate(20, 20)
        bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 150))
        self.screen.blit(bg_surface, bg_rect)
        
        # Draw text
        self.screen.blit(text_surface, text_rect)
    
    def _draw_message_with_glow(self, message, color, alpha=255):
        """Draw a centered message with a glow effect"""
        font = pygame.font.SysFont(None, 48)  # Larger font for better visibility
        
        # Create the main text
        text_surface = font.render(message, True, color)
        text_rect = text_surface.get_rect(center=(self.settings.SCREEN_WIDTH // 2, 
                                                self.settings.SCREEN_HEIGHT // 2))
        
        # Create glow effect
        glow_surfaces = []
        for size in range(10, 0, -2):  # Create multiple layers of glow
            glow_color = (*color, int(alpha * 0.1))  # Reduce alpha for glow
            glow_surface = font.render(message, True, glow_color)
            glow_surface = pygame.transform.scale(glow_surface, 
                (glow_surface.get_width() + size, 
                 glow_surface.get_height() + size))
            glow_rect = glow_surface.get_rect(center=text_rect.center)
            glow_surfaces.append((glow_surface, glow_rect))
        
        # Draw semi-transparent background
        bg_rect = text_rect.inflate(40, 40)
        bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, min(200, alpha)))
        self.screen.blit(bg_surface, bg_rect)
        
        # Draw glow layers
        for glow_surface, glow_rect in glow_surfaces:
            self.screen.blit(glow_surface, glow_rect)
        
        # Draw main text
        self.screen.blit(text_surface, text_rect)
    
    def _draw_navigation_arrow(self):
        """Draw an arrow pointing to the target island"""
        if self.game_state != "playing":
            return
            
        # Calculate angle to target island
        dx = self.target_pos[0] - self.world_pos[0]
        dy = self.target_pos[1] - self.world_pos[1]
        angle = math.degrees(math.atan2(dy, dx))
        
        # Calculate arrow position (centered on boat)
        center_x = self.screen.get_rect().centerx
        center_y = self.screen.get_rect().centery
        
        # Create arrow surface
        arrow_size = 40
        arrow_surf = pygame.Surface((arrow_size * 2, arrow_size * 2), pygame.SRCALPHA)
        
        # Calculate arrow points
        arrow_points = [
            (arrow_size * 2, arrow_size),  # Tip
            (arrow_size, arrow_size - 10),  # Left wing
            (arrow_size, arrow_size + 10)   # Right wing
        ]
        
        # Draw arrow
        pygame.draw.polygon(arrow_surf, self.settings.GOLD, arrow_points)
        
        # Rotate arrow to point at target
        rotated_arrow = pygame.transform.rotate(arrow_surf, -angle - 90)
        arrow_rect = rotated_arrow.get_rect(center=(center_x, center_y))
        
        # Draw distance text
        distance = math.sqrt(dx * dx + dy * dy)
        font = pygame.font.SysFont(None, 24)
        distance_text = f"{int(distance)}m"
        text_surf = font.render(distance_text, True, self.settings.GOLD)
        text_rect = text_surf.get_rect(center=(center_x, center_y + arrow_size + 20))
        
        # Draw arrow with slight transparency
        arrow_surf = pygame.Surface(rotated_arrow.get_size(), pygame.SRCALPHA)
        arrow_surf.fill((0, 0, 0, 0))
        arrow_surf.blit(rotated_arrow, (0, 0))
        self.screen.blit(arrow_surf, arrow_rect)
        self.screen.blit(text_surf, text_rect)
    
    def _draw_features(self):
        """Draw all sea features"""
        try:
            for feature in self.all_features:
                # Convert world coordinates to screen coordinates
                screen_pos = self._world_to_screen([feature["x"], feature["y"]])
                
                # Only draw if within view distance
                if (-100 <= screen_pos[0] <= self.settings.SCREEN_WIDTH + 100 and
                    -100 <= screen_pos[1] <= self.settings.SCREEN_HEIGHT + 100):
                    
                    if feature["type"] == "target_island":
                        # Draw target island with enhanced glow effect
                        glow_surf = pygame.Surface((feature["size"] * 3, feature["size"] * 3),
                                                pygame.SRCALPHA)
                        # Pulse effect
                        pulse = (math.sin(pygame.time.get_ticks() / 500) + 1) * 0.5
                        glow_alpha = int(100 + pulse * 50)
                        
                        pygame.draw.circle(glow_surf, (*self.settings.GOLD, glow_alpha),
                                         (feature["size"] * 1.5, feature["size"] * 1.5),
                                         feature["size"] * 1.5)
                        self.screen.blit(glow_surf, (screen_pos[0] - feature["size"] * 1.5,
                                               screen_pos[1] - feature["size"] * 1.5))
                        
                        # Draw the island with more detail
                        pygame.draw.circle(self.screen, self.settings.SAND_COLOR,
                                         screen_pos, feature["size"])
                        pygame.draw.circle(self.screen, self.settings.GREEN,
                                         screen_pos, feature["size"] - 5)
                        
                        # Add "TARGET" text above
                        font = pygame.font.SysFont(None, 24)
                        text = font.render("TARGET", True, self.settings.GOLD)
                        text_rect = text.get_rect(center=(screen_pos[0], screen_pos[1] - feature["size"] - 20))
                        self.screen.blit(text, text_rect)
                        
                    elif feature["type"] == "island":
                        # Draw regular island
                        pygame.draw.circle(self.screen, self.settings.SAND_COLOR,
                                         screen_pos, feature["size"])
                        pygame.draw.circle(self.screen, self.settings.GREEN,
                                         screen_pos, feature["size"] - 3)
                        
                    elif feature["type"] == "tree":
                        # Draw tree
                        trunk_color = (101, 67, 33)  # Brown
                        leaf_color = (34, 139, 34)   # Forest green
                        
                        # Draw trunk
                        pygame.draw.rect(self.screen, trunk_color,
                                       (screen_pos[0] - 2, screen_pos[1] - feature["size"],
                                        4, feature["size"]))
                        
                        # Draw triangular leaves
                        pygame.draw.polygon(self.screen, leaf_color, [
                            (screen_pos[0], screen_pos[1] - feature["size"] * 2),
                            (screen_pos[0] - feature["size"], screen_pos[1] - feature["size"] * 0.5),
                            (screen_pos[0] + feature["size"], screen_pos[1] - feature["size"] * 0.5)
                        ])
                        
                    elif feature["type"] == "other_boat":
                        # Draw other boats
                        boat_color = (200, 200, 200)  # Light gray
                        
                        # Create a simple boat shape
                        boat_points = [
                            (screen_pos[0], screen_pos[1] - feature["size"]),
                            (screen_pos[0] + feature["size"], screen_pos[1] + feature["size"]),
                            (screen_pos[0] - feature["size"], screen_pos[1] + feature["size"])
                        ]
                        
                        # Rotate the boat based on its heading
                        center = screen_pos
                        angle = feature["heading"]
                        rotated_points = [
                            (
                                center[0] + (x - center[0]) * math.cos(math.radians(angle)) -
                                (y - center[1]) * math.sin(math.radians(angle)),
                                center[1] + (x - center[0]) * math.sin(math.radians(angle)) +
                                (y - center[1]) * math.cos(math.radians(angle))
                            )
                            for x, y in boat_points
                        ]
                        
                        pygame.draw.polygon(self.screen, boat_color, rotated_points)
                        pygame.draw.polygon(self.screen, (100, 100, 100), rotated_points, 2)
        except Exception as e:
            print(f"Error drawing features: {e}")
    
    def _draw_notification(self, message):
        """Draw a notification message with background"""
        notification_surface = pygame.Surface((self.settings.SCREEN_WIDTH, 100), pygame.SRCALPHA)
        notification_surface.fill((0, 0, 0, 180))
        
        font = pygame.font.SysFont(None, 36)
        text_surface = font.render(message, True, self.settings.WHITE)
        text_rect = text_surface.get_rect(center=(self.settings.SCREEN_WIDTH // 2, 50))
        
        notification_surface.blit(text_surface, text_rect)
        self.screen.blit(notification_surface, (0, self.settings.SCREEN_HEIGHT // 3))
    
    def _draw_warning(self, message):
        """Draw a warning message at the bottom of the screen"""
        warning_surface = pygame.Surface((self.settings.SCREEN_WIDTH, 50), pygame.SRCALPHA)
        warning_surface.fill((255, 0, 0, 150))
        
        font = pygame.font.SysFont(None, 30)
        text_surface = font.render(message, True, self.settings.WHITE)
        text_rect = text_surface.get_rect(center=(self.settings.SCREEN_WIDTH // 2, 25))
        
        warning_surface.blit(text_surface, text_rect)
        self.screen.blit(warning_surface, (0, self.settings.SCREEN_HEIGHT - 50))
