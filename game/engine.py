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
        self.game_state = "instructions"  # Start with instructions
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
        
        # Load background
        try:
            if os.path.exists(settings.BACKGROUND_TEXTURE):
                self.background = pygame.image.load(settings.BACKGROUND_TEXTURE)
                bg_width, bg_height = self.background.get_size()
                self.background_large = pygame.Surface((bg_width * 5, bg_height * 5))
                for x in range(0, 5):
                    for y in range(0, 5):
                        self.background_large.blit(self.background, (x * bg_width, y * bg_height))
            else:
                self.background_large = pygame.Surface((settings.SCREEN_WIDTH * 5, settings.SCREEN_HEIGHT * 5))
                self.background_large.fill(settings.DARK_BLUE)
                for y in range(0, settings.SCREEN_HEIGHT * 5, 20):
                    pygame.draw.line(self.background_large, settings.BLUE, 
                                   (0, y), (settings.SCREEN_WIDTH * 5, y), 2)
        except Exception as e:
            print(f"Background loading error: {e}. Using fallback.")
            self.background_large = pygame.Surface((settings.SCREEN_WIDTH * 5, settings.SCREEN_HEIGHT * 5))
            self.background_large.fill(settings.DARK_BLUE)
            for y in range(0, settings.SCREEN_HEIGHT * 5, grid_spacing):
                pygame.draw.line(self.background_large, (0, 70, 130), 
                               (0, y), (settings.SCREEN_WIDTH * 5, y), 1)
        
        # Add starting island first
        self.settings.SEA_FEATURES = [{
            "type": "starting_island",
            "x": 0,  # At center
            "y": 0,
            "size": 40  # Smaller than regular islands
        }]
        
        # Generate world features (this will add other islands and rocks)
        self.generate_world_features()
        
        # Initialize game components
        self.boat = Boat(settings, self.screen.get_rect())
        self.wave_generator = WaveGenerator(settings)
        self.player = Player(self.boat)
        
        # Game state
        self.game_state = "instructions"  # Start with instructions
        self.restart_requested = False
        self.success_start_time = 0
        
        # Checkpoint system
        self.checkpoint_pos = [0, 0]  # Starting position is first checkpoint
        self.has_checkpoint = True
        
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
        
        # Make sure game starts in instruction state
        self.game_state = "instructions"  # Ensure we start with instructions
        
    def handle_event(self, event):
        """Handle game events"""
        try:
            if event.type == pygame.KEYDOWN:
                if self.game_state == "instructions":
                    self.game_state = "playing"
                    self.show_current_notification = True
                    self.current_notification = "Press UP arrow to undock the boat and start your journey!"
                    self.notification_start_time = pygame.time.get_ticks()
                    return
                
                if event.key == pygame.K_r and (self.game_state == "fail" or self.game_state == "win"):
                    print("Debug: R key pressed, initiating restart")
                    self.initiate_restart()
                    return
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
                    sys.exit()
                
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
                    
                    if self.is_docked and event.key == pygame.K_UP:
                        self.is_docked = False
                        self.boat.is_docked = False  # Update boat's docked state
                        self.show_current_notification = True
                        self.game_paused = True
                        self.current_notification = "Boat undocked! Navigate carefully through the currents."
                        self.notification_start_time = pygame.time.get_ticks()
                        if hasattr(self, 'boat'):
                            self.boat.velocity = [0, 0]  # Reset velocity when undocking
                            self.boat.momentum = [0, 0]  # Reset momentum when undocking
                    elif not self.is_docked and hasattr(self, 'boat'):
                        self.boat.handle_keydown(event)
            
            elif event.type == pygame.KEYUP and self.game_state == "playing" and not self.is_docked:
                if hasattr(self, 'boat'):
                    self.boat.handle_keyup(event.key)
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if self.show_current_notification:
                    self.show_current_notification = False
                    self.game_paused = False
                elif self.game_state == "playing" and not self.is_docked:
                    # Validate mouse position is within screen bounds
                    if (0 <= event.pos[0] <= self.settings.SCREEN_WIDTH and 
                        0 <= event.pos[1] <= self.settings.SCREEN_HEIGHT):
                        if hasattr(self, 'boat'):
                            # Reset controls before applying new ones
                            self.boat.reset_controls()
                            self.boat.handle_mouse_click(event.pos)
                        
            elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
                if hasattr(self, 'boat'):
                    self.boat.reset_controls()
        except Exception as e:
            print(f"Debug: Error in handle_event: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def generate_world_features(self):
        """Generate random world features"""
        import random
        
        # Clear existing features
        self.settings.SEA_FEATURES = []
        
        # Generate random rocks (4-6)
        num_rocks = random.randint(4, 6)
        for _ in range(num_rocks):
            distance = random.uniform(self.settings.ISLAND_DISTANCE_MIN * 0.5,
                                   self.settings.ISLAND_DISTANCE_MAX * 0.7)
            angle = random.uniform(0, 2 * math.pi)
            self.settings.SEA_FEATURES.append({
                "type": "rock",
                "x": distance * math.cos(angle),
                "y": distance * math.sin(angle),
                "size": random.randint(20, 35)  # Rocks are smaller than islands
            })
        
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
    
    def initiate_restart(self):
        """Safely initiate a game restart"""
        try:
            print("Debug: Initiating game restart")
            # Create new boat instance
            from game.boat import Boat
            self.boat = Boat(self.settings, self.screen.get_rect())
            
            # Create new player instance with new boat
            from game.player import Player
            self.player = Player(self.boat)
            
            # Reset world position to center
            self.world_pos = [0, 0]
            
            # Generate new world features
            self.generate_world_features()
            
            # Reset game state variables
            self.near_target_notified = False
            self.instruction_shown = False
            self.bermuda_triggered = False
            
            # Create new wave generator
            from game.wave import WaveGenerator
            self.wave_generator = WaveGenerator(self.settings)
            
            # Reset game state
            self.game_state = "playing"
            self.success_start_time = 0
            self.is_docked = True
            self.show_current_notification = True
            self.current_notification = "Press UP arrow to undock the boat and start your journey!"
            self.notification_start_time = pygame.time.get_ticks()
            self.game_paused = True
            
            print("Debug: Game restart completed successfully")
            
        except Exception as e:
            print(f"Debug: Error in initiate_restart: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def update(self):
        """Update game state"""
        try:
            current_time = pygame.time.get_ticks()
            
            # Handle notifications timing
            if self.show_current_notification and current_time - self.notification_start_time > self.settings.NOTIFICATION_DURATION:
                self.show_current_notification = False
                self.game_paused = False
            
            # Handle warning timing
            if self.show_warning and current_time - self.warning_start_time > self.settings.WARNING_DURATION:
                self.show_warning = False
            
            if self.game_state == "win":
                return
            elif self.game_state == "fail":
                # Show fail menu
                return
            elif self.game_state != "playing" or self.game_paused:
                return
                
            # Only update boat if not docked
            if not self.is_docked:
                # Update game components
                self.wave_generator.update()
                
                if hasattr(self, 'boat'):
                    # Get current vector before boat update
                    current_vector = self.wave_generator.get_current_vector()
                    
                    # Update boat
                    self.boat.update(current_vector)
                    
                    # Get boat position and velocity
                    boat_pos = self.boat.get_position()
                    velocity = self.boat.get_velocity()
                    
                    # Check world boundaries and return to checkpoint
                    if abs(boat_pos[0]) > self.settings.WORLD_BOUNDARY or abs(boat_pos[1]) > self.settings.WORLD_BOUNDARY:
                        print("Debug: Out of bounds - returning to checkpoint")
                        
                        # Return to checkpoint
                        self.boat.x = self.checkpoint_pos[0]
                        self.boat.y = self.checkpoint_pos[1]
                        self.boat.velocity = [0, 0]
                        self.boat.momentum = [0, 0]
                        self.world_pos = list(self.checkpoint_pos)
                        
                        # Show warning
                        self.show_warning = True
                        self.warning_message = "Out of bounds! Returning to checkpoint..."
                        self.warning_start_time = current_time
                        return
                    
                    # Check for collisions
                    collision_result = self.boat.check_collision(self.all_features)
                    if collision_result != "no_collision":
                        if collision_result == "dock_success":
                            print("Debug: Target island reached!")
                            self.game_state = "win"
                            self.success_start_time = current_time
                            return
                        elif collision_result == "dock_fail":
                            print("Debug: Wrong island docking - game over")
                            self.game_state = "fail"
                            self.show_warning = True
                            self.warning_message = "Wrong docking! Game Over!"
                            self.warning_start_time = current_time
                            return
                        elif collision_result == "collision":
                            print("Debug: Collision detected - game over")
                            self.game_state = "fail"
                            self.show_warning = True
                            self.warning_message = "Collision! Game Over!"
                            self.warning_start_time = current_time
                            return
                    
                    # Update world position
                    self.world_pos = list(boat_pos)
                    
                    # Update background offset for tiling
                    self.background_offset[0] = -(self.world_pos[0] % self.background_large.get_width())
                    self.background_offset[1] = -(self.world_pos[1] % self.background_large.get_height())
                
        except Exception as e:
            print(f"Debug: Error in update loop: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def draw(self):
        """Draw the game state"""
        try:
            # Clear the screen first
            self.screen.fill(self.settings.BLACK)
            
            if self.game_state == "instructions":
                print("Debug: Drawing instructions screen")
                instructions = [
                    "Welcome to the Island Navigator!",
                    "",
                    "Game Controls:",
                    "- Use ARROW KEYS or CLICK the arrows around the boat",
                    "- Q/E keys to rotate the boat",
                    "",
                    "Game Rules:",
                    "- Press UP arrow to undock and start",
                    "- Avoid rocks and wrong islands",
                    "- Watch minimap and compass",
                    "- Mind the currents",
                    "",
                    "Press ANY KEY to begin..."
                ]
                
                y_offset = self.settings.SCREEN_HEIGHT // 4  # Start higher up
                line_spacing = 25  # Reduced from 35
                for line in instructions:
                    self._draw_message(line, self.settings.WHITE, y_offset)
                    y_offset += line_spacing
                return
                
            if self.game_state == "fail":
                print("Debug: Drawing fail state")
                self._draw_message("Wrong Island! Mission Failed!", self.settings.RED)
                
                # Draw menu options
                menu_options = [
                    "Press R - Return to Checkpoint",
                    "Press ESC - Exit Game"
                ]
                
                y_offset = self.settings.SCREEN_HEIGHT // 2 + 50
                for option in menu_options:
                    self._draw_message(option, self.settings.WHITE, y_offset)
                    y_offset += 40
                return
                
            if self.game_state == "win":
                print("Debug: Drawing win state")
                self._draw_message_with_glow("Congratulations! You reached the target island!", 
                                           self.settings.GOLD)
                
                # Draw menu options
                menu_options = [
                    "Press R - Start New Game",
                    "Press ESC - Exit Game"
                ]
                
                y_offset = self.settings.SCREEN_HEIGHT // 2 + 50
                for option in menu_options:
                    self._draw_message(option, self.settings.WHITE, y_offset)
                    y_offset += 40
                return
                
            # Only draw game elements if in playing state
            if self.game_state == "playing":
                try:
                    print("Debug: Drawing game state")
                    self.screen.blit(self.background_large, self.background_offset)
                    self._draw_features()
                    
                    if hasattr(self, 'boat') and hasattr(self, 'wave_generator'):
                        self.wave_generator.draw_indicator(self.screen, self.boat.rect)
                        self.boat.draw(self.screen)
                        self._draw_navigation_arrow()
                        self._draw_ui()
                    else:
                        print("Debug: Missing boat or wave_generator")
                    
                    # Draw current notification if active
                    if self.show_current_notification:
                        print(f"Debug: Drawing notification: {self.current_notification}")
                        self._draw_notification(self.current_notification)
                    
                    # Draw warning if active
                    if self.show_warning:
                        print(f"Debug: Drawing warning: {self.warning_message}")
                        self._draw_warning(self.warning_message)
                        
                except Exception as e:
                    print(f"Debug: Error drawing game elements: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    
        except Exception as e:
            print(f"Debug: Critical error in draw method: {str(e)}")
            import traceback
            traceback.print_exc()
    
    def _world_to_screen(self, world_pos):
        """Convert world coordinates to screen coordinates"""
        screen_x = self.screen.get_rect().centerx - (self.world_pos[0] - world_pos[0])
        screen_y = self.screen.get_rect().centery - (self.world_pos[1] - world_pos[1])
        return (screen_x, screen_y)
        
    def _draw_ui(self):
        """Draw UI elements like minimap and distance indicator"""
        # Draw minimap
        self._draw_minimap()
        
        # Draw distance text at the bottom
        dx = self.target_pos[0] - self.world_pos[0]
        dy = self.target_pos[1] - self.world_pos[1]
        distance = math.sqrt(dx * dx + dy * dy)
        
        # Draw distance text at bottom center
        distance_text = f"Distance: {int(distance)} m"
        font = pygame.font.SysFont(None, 30)
        text_surface = font.render(distance_text, True, self.settings.WHITE)
        text_rect = text_surface.get_rect(centerx=self.settings.SCREEN_WIDTH // 2,
                                        bottom=self.settings.SCREEN_HEIGHT - 10)
        self.screen.blit(text_surface, text_rect)
    
    def _draw_minimap(self):
        """Draw the minimap showing the entire game world"""
        # Create minimap surface with transparency
        minimap_surf = pygame.Surface((self.settings.MINIMAP_SIZE, self.settings.MINIMAP_SIZE), pygame.SRCALPHA)
        minimap_surf.fill((0, 0, 0, self.settings.MINIMAP_OPACITY))
        
        # Calculate scale factor to fit world into minimap
        scale = self.settings.MINIMAP_SCALE
        
        # Draw world boundary
        pygame.draw.rect(minimap_surf, (50, 50, 50, 100), 
                        (0, 0, self.settings.MINIMAP_SIZE, self.settings.MINIMAP_SIZE), 1)
        
        # Draw all features on minimap
        minimap_center = self.settings.MINIMAP_SIZE // 2
        for feature in self.all_features:
            # Convert world coordinates to minimap coordinates
            mini_x = minimap_center + feature["x"] * scale
            mini_y = minimap_center + feature["y"] * scale
            
            # Only draw if within minimap bounds
            if (0 <= mini_x <= self.settings.MINIMAP_SIZE and 
                0 <= mini_y <= self.settings.MINIMAP_SIZE):
                
                if feature["type"] == "target_island":
                    # Draw target island (larger, gold)
                    pygame.draw.circle(minimap_surf, self.settings.MINIMAP_TARGET_COLOR,
                                     (int(mini_x), int(mini_y)), 4)
                elif feature["type"] == "island":
                    # Draw regular island (green)
                    pygame.draw.circle(minimap_surf, self.settings.MINIMAP_ISLAND_COLOR,
                                     (int(mini_x), int(mini_y)), 2)
                elif feature["type"] == "rock":
                    # Draw rocks (gray)
                    pygame.draw.circle(minimap_surf, (100, 100, 100),
                                     (int(mini_x), int(mini_y)), 2)
        
        # Draw player position
        player_x = minimap_center + self.world_pos[0] * scale
        player_y = minimap_center + self.world_pos[1] * scale
        pygame.draw.circle(minimap_surf, self.settings.MINIMAP_PLAYER_COLOR,
                         (int(player_x), int(player_y)), 3)
        
        # Draw minimap border
        pygame.draw.rect(minimap_surf, self.settings.MINIMAP_BORDER_COLOR,
                        (0, 0, self.settings.MINIMAP_SIZE, self.settings.MINIMAP_SIZE), 2)
        
        # Draw compass points on minimap
        font = pygame.font.SysFont(None, 20)
        compass_points = [
            ("N", (minimap_center, 5)),
            ("S", (minimap_center, self.settings.MINIMAP_SIZE - 5)),
            ("E", (self.settings.MINIMAP_SIZE - 5, minimap_center)),
            ("W", (5, minimap_center))
        ]
        
        for label, pos in compass_points:
            text = font.render(label, True, self.settings.WHITE)
            text_rect = text.get_rect(center=pos)
            minimap_surf.blit(text, text_rect)
        
        # Position minimap in lower-right corner with margin
        minimap_x = self.settings.SCREEN_WIDTH - self.settings.MINIMAP_SIZE - self.settings.MINIMAP_MARGIN
        minimap_y = self.settings.SCREEN_HEIGHT - self.settings.MINIMAP_SIZE - self.settings.MINIMAP_MARGIN
        self.screen.blit(minimap_surf, (minimap_x, minimap_y))
    
    def _draw_message(self, message, color, y_offset=None):
        """Draw a centered message on the screen"""
        font = pygame.font.SysFont(None, 24)  # Reduced from 36 to 24
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
                    
                    if feature["type"] == "starting_island":
                        # Draw starting island (blue color to distinguish)
                        pygame.draw.circle(self.screen, self.settings.BLUE,
                                         screen_pos, feature["size"])
                        pygame.draw.circle(self.screen, self.settings.LIGHT_BLUE,
                                         screen_pos, feature["size"] - 3)
                        # Add "START" text above
                        font = pygame.font.SysFont(None, 24)
                        text = font.render("START", True, self.settings.WHITE)
                        text_rect = text.get_rect(center=(screen_pos[0], screen_pos[1] - feature["size"] - 10))
                        self.screen.blit(text, text_rect)
                    
                    elif feature["type"] == "rock":
                        # Draw rock
                        rock_color = (100, 100, 100)  # Gray color for rocks
                        pygame.draw.circle(self.screen, rock_color,
                                         screen_pos, feature["size"])
                        # Add some texture/detail to rocks
                        pygame.draw.circle(self.screen, (80, 80, 80),
                                         (screen_pos[0] - 5, screen_pos[1] - 5),
                                         feature["size"] // 3)
                    
                    elif feature["type"] == "target_island":
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
