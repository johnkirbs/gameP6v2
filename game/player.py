import pygame

class Player:
    """Handles player input and controls"""
    
    def __init__(self, boat):
        """Initialize the player controller"""
        self.boat = boat
        
    def handle_event(self, event):
        """Handle keyboard/mouse events for player control"""
        if event.type == pygame.KEYDOWN:
            self._handle_keydown(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_click(event)
            
    def _handle_keydown(self, event):
        """Handle key press events"""
        if event.key == pygame.K_LEFT:  # Left force
            self.boat.add_force('left')
        elif event.key == pygame.K_RIGHT:  # Right force
            self.boat.add_force('right')
        elif event.key == pygame.K_r:  # Restart game
            return "restart"
            
    def _handle_mouse_click(self, event):
        """Handle mouse/touch input"""
        # Check which half of the screen was clicked
        if self.boat.left_click_region.collidepoint(event.pos):
            self.boat.add_force('left')
        elif self.boat.right_click_region.collidepoint(event.pos):
            self.boat.add_force('right')
    
    def update(self):
        """Update player state (called each frame)"""
        pass  # No continuous updates needed