import pygame
import math
from game.boat import Boat
from game.wave import WaveGenerator
from game.player import Player

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
            # Add subtle grid for motion reference (instead of wave lines)
            grid_spacing = 100
            for x in range(0, settings.SCREEN_WIDTH * 5, grid_spacing):
                pygame.draw.line(self.background_large, (0, 70, 130), 
                               (x, 0), (x, settings.SCREEN_HEIGHT * 5), 1)
            for y in range(0, settings.SCREEN_HEIGHT * 5, grid_spacing):
                pygame.draw.line(self.background_large, (0, 70, 130), 
                               (0, y), (settings.SCREEN_WIDTH * 5, y), 1)
        
        # Initialize game components
        self.boat = Boat(settings, self.screen.get_rect())
        self.wave_generator = WaveGenerator(settings)
        self.player = Player(self.boat)
        
        # Game state
        self.world_pos = [0, 0]  # World position
        self.game_state = "playing"  # Can be "playing", "win", "fail", "restart"
        self.restart_requested = False
        
        # Get all islands including decorative ones
        self.all_islands = settings.DECORATIVE_ISLANDS.copy()
        self.all_islands.append({
            "x": settings.ISLAND_DISTANCE,
            "y": 0,
            "size": settings.ISLAND_RADIUS,
            "is_target": True
        })
        
        # Target island
        self.island_pos = [settings.ISLAND_DISTANCE, 0]  # Relative to start position
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
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r and self.game_state == "fail":
                self.restart_game()
            elif self.game_state == "playing":
                self.boat.handle_keydown(event.key)
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.game_state == "playing":
            self.boat.handle_mouse_click(event.pos)
            
    def restart_game(self):
        """Restart the game with new current settings"""
        # Reset boat position and state
        self.boat.reset(self.screen.get_rect())
        
        # Reset world position
        self.world_pos = [0, 0]
        
        # Change current direction randomly
        import random
        self.settings.CURRENT_DIRECTION = random.randint(0, 359)
        self.wave_generator = WaveGenerator(self.settings)
        
        # Reset game state
        self.game_state = "playing"
        
    def update(self):
        """Update game state"""
        if self.game_state != "playing":
            return
            
        # Update wave generator
        self.wave_generator.update()
        
        # Update boat position
        self.boat.update(self.wave_generator.get_current_vector())
        
        # Update world position
        boat_pos = self.boat.get_position()
        self.world_pos[0] = boat_pos[0]
        self.world_pos[1] = boat_pos[1]
        
        # Check collisions with all islands
        if self.boat.check_collision(self.all_islands):
            # Check if it's the target island
            target_distance = math.sqrt(
                (self.world_pos[0] - self.settings.ISLAND_DISTANCE) ** 2 +
                self.world_pos[1] ** 2
            )
            
            if target_distance < self.settings.ISLAND_RADIUS:
                self.game_state = "win"
            else:
                self.game_state = "fail"
        
        # Update background offset for tiling
        self.background_offset[0] = -(self.world_pos[0] % self.background_large.get_width())
        self.background_offset[1] = -(self.world_pos[1] % self.background_large.get_height())
        
    def draw(self):
        """Draw the game state"""
        if self.game_state == "fail":
            # On failure, draw only black background and message
            self.screen.fill(self.settings.BLACK)
            self._draw_message("Mission Failed! Hit wrong island! Press R to restart", self.settings.RED)
            return
            
        # Draw tiled background
        self.screen.blit(self.background_large, self.background_offset)
        
        # Draw decorative islands
        self._draw_islands()
        
        # Draw wave indicator
        self.wave_generator.draw_indicator(self.screen, self.boat.rect)
        
        # Draw the boat
        self.boat.draw(self.screen)
        
        # Draw navigation arrow
        self._draw_navigation_arrow()
        
        # Draw UI elements
        self._draw_ui()
        
        # Draw game state messages
        if self.game_state == "win":
            self._draw_message("You reached the target island! Victory!", self.settings.GREEN)
        
    def _world_to_screen(self, world_pos):
        """Convert world coordinates to screen coordinates"""
        screen_x = self.screen.get_rect().centerx - (self.world_pos[0] - world_pos[0])
        screen_y = self.screen.get_rect().centery - (self.world_pos[1] - world_pos[1])
        return (screen_x, screen_y)
        
    def _draw_ui(self):
        """Draw UI elements like distance indicator"""
        # Calculate distance to island
        distance = math.sqrt(
            (self.world_pos[0] - self.island_pos[0]) ** 2 +
            (self.world_pos[1] - self.island_pos[1]) ** 2
        )
        
        # Draw distance text
        distance_text = f"Distance: {int(distance)} m"
        text_surface = self.font.render(distance_text, True, self.settings.WHITE)
        self.screen.blit(text_surface, (10, 10))
        
        # Draw direction indicator to island (compass style)
        indicator_radius = 45
        center_x = self.settings.SCREEN_WIDTH - indicator_radius - 20
        center_y = indicator_radius + 20
        
        # Draw outer circle with better visibility
        pygame.draw.circle(self.screen, (80, 80, 80), (center_x, center_y), indicator_radius + 2)  # Shadow
        pygame.draw.circle(self.screen, self.settings.WHITE, (center_x, center_y), indicator_radius)
        pygame.draw.circle(self.screen, (220, 220, 220), (center_x, center_y), indicator_radius - 2)  # Inner circle
        
        # Calculate angle to island
        dx = self.island_pos[0] - self.world_pos[0]
        dy = self.island_pos[1] - self.world_pos[1]
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
        
        # Draw island direction arrow (more visible)
        arrow_length = indicator_radius - 5
        arrow_color = self.settings.GREEN
        
        # Make arrow pulse based on distance
        pulse = math.sin(pygame.time.get_ticks() / 300) * 0.2 + 0.8
        if distance < 300:
            # Make arrow blink faster when close to island
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
        label = self.font.render("Island", True, self.settings.WHITE)
        self.screen.blit(label, (center_x - label.get_width() // 2, center_y - indicator_radius - 30))
        
        # Add mini version of distance
        mini_dist = self.font.render(f"{int(distance)}m", True, self.settings.WHITE)
        self.screen.blit(mini_dist, (center_x - mini_dist.get_width() // 2, center_y + indicator_radius + 5))
    
    def _draw_message(self, message, color):
        """Draw a centered message on the screen"""
        text_surface = self.font.render(message, True, color)
        text_rect = text_surface.get_rect(center=(self.settings.SCREEN_WIDTH // 2, 
                                                self.settings.SCREEN_HEIGHT // 2))
        
        # Draw semi-transparent background
        bg_rect = text_rect.inflate(20, 20)
        bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 150))
        self.screen.blit(bg_surface, bg_rect)
        
        # Draw text
        self.screen.blit(text_surface, text_rect)
    
    def _draw_navigation_arrow(self):
        """Draw an arrow pointing to the target island"""
        if self.game_state != "playing":
            return
            
        # Calculate angle to target island
        dx = self.settings.ISLAND_DISTANCE - self.world_pos[0]
        dy = -self.world_pos[1]  # Target is at y=0
        angle = math.degrees(math.atan2(dy, dx))
        
        # Calculate arrow position (centered on boat)
        center_x = self.screen.get_rect().centerx
        center_y = self.screen.get_rect().centery
        
        # Create arrow surface
        arrow_surf = pygame.Surface((self.nav_arrow_size * 2, self.nav_arrow_size * 2), pygame.SRCALPHA)
        
        # Calculate arrow points
        arrow_points = [
            (self.nav_arrow_size * 2, self.nav_arrow_size),  # Tip
            (self.nav_arrow_size, self.nav_arrow_size - 10),  # Left wing
            (self.nav_arrow_size, self.nav_arrow_size + 10)   # Right wing
        ]
        
        # Draw arrow
        pygame.draw.polygon(arrow_surf, self.nav_arrow_color, arrow_points)
        
        # Rotate arrow to point at target
        rotated_arrow = pygame.transform.rotate(arrow_surf, -angle - 90)  # -90 to adjust for arrow pointing right
        arrow_rect = rotated_arrow.get_rect(center=(center_x, center_y))
        
        # Draw distance text
        distance = math.sqrt(dx * dx + dy * dy)
        font = pygame.font.SysFont(None, 24)
        distance_text = f"{int(distance)}m"
        text_surf = font.render(distance_text, True, self.nav_arrow_color)
        text_rect = text_surf.get_rect(center=(center_x, center_y + self.nav_arrow_size + 20))
        
        # Draw arrow with slight transparency
        arrow_surf = pygame.Surface(rotated_arrow.get_size(), pygame.SRCALPHA)
        arrow_surf.fill((0, 0, 0, 0))
        arrow_surf.blit(rotated_arrow, (0, 0))
        self.screen.blit(arrow_surf, arrow_rect)
        self.screen.blit(text_surf, text_rect)
    
    def _draw_islands(self):
        """Draw all islands"""
        # Draw decorative islands
        for island in self.settings.DECORATIVE_ISLANDS:
            screen_pos = self._world_to_screen([island["x"], island["y"]])
            
            # Check if island is within view distance
            if (-100 <= screen_pos[0] <= self.settings.SCREEN_WIDTH + 100 and
                -100 <= screen_pos[1] <= self.settings.SCREEN_HEIGHT + 100):
                
                # Create scaled island surface if needed
                scale = island["size"] / self.settings.ISLAND_RADIUS
                scaled_size = (int(self.island_image.get_width() * scale),
                             int(self.island_image.get_height() * scale))
                
                scaled_island = pygame.transform.scale(self.island_image, scaled_size)
                island_rect = scaled_island.get_rect(center=screen_pos)
                
                # Draw island with sand circle underneath
                sand_surf = pygame.Surface((island["size"] * 2.2, island["size"] * 2.2), pygame.SRCALPHA)
                pygame.draw.circle(sand_surf, (*self.settings.SAND_COLOR, 180), 
                                 (island["size"] * 1.1, island["size"] * 1.1), 
                                 island["size"] * 1.1)
                self.screen.blit(sand_surf, (screen_pos[0] - island["size"] * 1.1,
                                           screen_pos[1] - island["size"] * 1.1))
                self.screen.blit(scaled_island, island_rect)
        
        # Draw target island
        island_screen_pos = self._world_to_screen(self.island_pos)
        self.island_rect.center = island_screen_pos
        
        # Check if target island is within view distance
        if (-100 <= island_screen_pos[0] <= self.settings.SCREEN_WIDTH + 100 and
            -100 <= island_screen_pos[1] <= self.settings.SCREEN_HEIGHT + 100):
            
            # Draw sand circle underneath target island
            sand_surf = pygame.Surface((self.settings.ISLAND_RADIUS * 2.2, 
                                      self.settings.ISLAND_RADIUS * 2.2), pygame.SRCALPHA)
            pygame.draw.circle(sand_surf, (*self.settings.SAND_COLOR, 180), 
                             (self.settings.ISLAND_RADIUS * 1.1, self.settings.ISLAND_RADIUS * 1.1), 
                             self.settings.ISLAND_RADIUS * 1.1)
            self.screen.blit(sand_surf, (island_screen_pos[0] - self.settings.ISLAND_RADIUS * 1.1,
                                       island_screen_pos[1] - self.settings.ISLAND_RADIUS * 1.1))
            
            # Draw the target island
            self.screen.blit(self.island_image, self.island_rect)
            
            # Draw target indicator
            pygame.draw.circle(self.screen, (255, 255, 0, 100), island_screen_pos, 
                             self.settings.ISLAND_RADIUS + 10, 3)
