import pygame

class Player:
    """Handles player input and controls"""
    
    def __init__(self, boat):
        """Initialize the player controller"""
        self.boat = boat
        self.steering_left = False
        self.steering_right = False
        
    def handle_event(self, event):
        """Handle keyboard/mouse events for player control"""
        if event.type == pygame.KEYDOWN:
            self._handle_keydown(event)
        elif event.type == pygame.KEYUP:
            self._handle_keyup(event)
            
    def _handle_keydown(self, event):
        """Handle key press events"""
        if event.key == pygame.K_LEFT:
            self.steering_left = True
            self._update_steering()
        elif event.key == pygame.K_RIGHT:
            self.steering_right = True
            self._update_steering()
            
    def _handle_keyup(self, event):
        """Handle key release events"""
        if event.key == pygame.K_LEFT:
            self.steering_left = False
            self._update_steering()
        elif event.key == pygame.K_RIGHT:
            self.steering_right = False
            self._update_steering()
    
    def _update_steering(self):
        """Update the boat's steering based on current key states"""
        if self.steering_left and not self.steering_right:
            self.boat.steer(-1)
            self.boat.steering_power = -1.0
        elif self.steering_right and not self.steering_left:
            self.boat.steer(1)
            self.boat.steering_power = 1.0
        else:
            self.boat.steer(0)
            self.boat.steering_power = 0.0
            
    def update(self):
        """Update player state (called each frame)"""
        pass  # Currently all updates are driven by events