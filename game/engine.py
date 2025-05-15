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
            # Draw some wave lines
            for y in range(0, settings.SCREEN_HEIGHT * 5, 20):
                pygame.draw.line(self.background_large, settings.BLUE, 
                               (0, y), (settings.SCREEN_WIDTH * 5, y), 2)
        
        # Initialize game components
        self.boat = Boat(settings, self.screen.get_rect())
        self.wave_generator = WaveGenerator(settings)
        self.player = Player(self.boat)
        
        # Game state
        self.world_pos = [0, 0]  # World position
        self.game_state = "playing"  # Can be "playing", "win", "lose"
        
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
        
    def handle_event(self, event):
        """Handle game events"""
        self.player.handle_event(event)
        
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
        
        # Update background offset for tiling
        self.background_offset[0] = -(self.world_pos[0] % self.background_large.get_width())
        self.background_offset[1] = -(self.world_pos[1] % self.background_large.get_height())
        
        # Check for island collision (win condition)
        island_screen_pos = self._world_to_screen(self.island_pos)
        distance_to_island = math.sqrt(
            (island_screen_pos[0] - self.screen.get_rect().centerx) ** 2 +
            (island_screen_pos[1] - self.screen.get_rect().centery) ** 2
        )
        
        if distance_to_island < self.settings.ISLAND_RADIUS:
            self.game_state = "win"
            
    def draw(self):
        """Draw the game state"""
        # Draw tiled background
        self.screen.blit(self.background_large, self.background_offset)
        
        # Draw the island
        island_screen_pos = self._world_to_screen(self.island_pos)
        self.island_rect.center = island_screen_pos
        
        # Only draw island if it's within view
        if (0 <= island_screen_pos[0] <= self.settings.SCREEN_WIDTH and
            0 <= island_screen_pos[1] <= self.settings.SCREEN_HEIGHT):
            self.screen.blit(self.island_image, self.island_rect)
        
        # Draw wave indicator
        self.wave_generator.draw_indicator(self.screen, self.boat.rect)
        
        # Draw the boat (always in center)
        self.boat.draw(self.screen)
        
        # Draw UI elements
        self._draw_ui()
        
        # Draw game state messages
        if self.game_state == "win":
            self._draw_message("You reached the island! Victory!", self.settings.GREEN)
        
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
        
        # Draw direction indicator to island
        indicator_radius = 40
        center_x = self.settings.SCREEN_WIDTH - indicator_radius - 20
        center_y = indicator_radius + 20
        
        # Draw outer circle
        pygame.draw.circle(self.screen, self.settings.WHITE, (center_x, center_y), indicator_radius, 2)
        
        # Calculate angle to island
        dx = self.island_pos[0] - self.world_pos[0]
        dy = self.island_pos[1] - self.world_pos[1]
        angle = math.degrees(math.atan2(dy, dx))
        
        # Adjust for boat heading (so indicator shows relative direction)
        relative_angle = angle - self.boat.heading + 90
        
        # Draw direction line
        endpoint_x = center_x + math.cos(math.radians(relative_angle)) * (indicator_radius - 5)
        endpoint_y = center_y + math.sin(math.radians(relative_angle)) * (indicator_radius - 5)
        
        pygame.draw.line(self.screen, self.settings.GREEN, (center_x, center_y), (endpoint_x, endpoint_y), 3)
        pygame.draw.circle(self.screen, self.settings.GREEN, (int(endpoint_x), int(endpoint_y)), 5)
        
        # Label
        label = self.font.render("Island", True, self.settings.WHITE)
        self.screen.blit(label, (center_x - label.get_width() // 2, center_y - indicator_radius - 30))
    
    def _draw_message(self, message, color):
        """Draw a centered message on the screen"""
        text_surface = self.font.render(message, True, color)
        text_rect = text_surface.get_rect(center=(self.settings.SCREEN_WIDTH // 2, self.settings.SCREEN_HEIGHT // 2))
        
        # Draw semi-transparent background
        bg_rect = text_rect.inflate(20, 20)
        bg_surface = pygame.Surface(bg_rect.size, pygame.SRCALPHA)
        bg_surface.fill((0, 0, 0, 150))  # Semi-transparent black
        self.screen.blit(bg_surface, bg_rect)
        
        # Draw text
        self.screen.blit(text_surface, text_rect)