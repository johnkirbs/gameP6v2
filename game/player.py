import pygame

class Player:
    """Handles player input and controls"""
    
    def __init__(self, boat):
        """Initialize the player controller"""
        self.boat = boat
        
    def handle_event(self, event):
        """Handle keyboard/mouse events for player control"""
        if event.type == pygame.KEYDOWN:
            return self._handle_keydown(event)
        elif event.type == pygame.MOUSEBUTTONDOWN:
            self._handle_mouse_click(event)
            
    def _handle_keydown(self, event):
        """Handle key press events"""
        if event.key == pygame.K_LEFT:  # Left force
            self.boat.handle_keydown(event.key)
        elif event.key == pygame.K_RIGHT:  # Right force
            self.boat.handle_keydown(event.key)
        elif event.key == pygame.K_UP:  # Forward force
            self.boat.handle_keydown(event.key)
        elif event.key == pygame.K_DOWN:  # Backward force
            self.boat.handle_keydown(event.key)
        elif event.key == pygame.K_q:  # Rotate left
            self.boat.handle_keydown(event.key)
        elif event.key == pygame.K_e:  # Rotate right
            self.boat.handle_keydown(event.key)
        elif event.key == pygame.K_r:  # Restart game
            return "restart"
            
    def _handle_mouse_click(self, event):
        """Handle mouse/touch input"""
        # Check which region was clicked
        if hasattr(self.boat, 'handle_mouse_click'):
            self.boat.handle_mouse_click(event.pos)
    
    def update(self):
        """Update player state (called each frame)"""
        pass  # No continuous updates needed