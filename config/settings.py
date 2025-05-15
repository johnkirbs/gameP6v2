class Settings:
    """Game settings and configuration parameters"""
    
    def __init__(self):
        # Screen settings
        self.SCREEN_WIDTH = 800
        self.SCREEN_HEIGHT = 600
        self.SCREEN_TITLE = "Island Navigator"
        self.FPS = 60
        
        # Color definitions
        self.BLUE = (0, 121, 255)
        self.DARK_BLUE = (0, 0, 139)
        self.GREEN = (34, 139, 34)
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        
        # Game mechanics
        self.BOAT_SPEED = 2.0
        self.BOAT_ROTATION_SPEED = 3.0
        
        # Wave/current settings
        self.MIN_WAVE_MAGNITUDE = 0.5
        self.MAX_WAVE_MAGNITUDE = 2.5
        self.WAVE_CHANGE_INTERVAL = 3000  # milliseconds
        
        # Island settings
        self.ISLAND_DISTANCE = 2000  # Distance to target island
        self.ISLAND_RADIUS = 80
        
        # Asset paths
        self.TEXTURE_FOLDER = "assets/textures/"
        self.SOUND_FOLDER = "assets/sounds/"
        self.FONTS_FOLDER = "assets/fonts/"
        
        # Asset filenames
        self.BOAT_TEXTURE = self.TEXTURE_FOLDER + "boat.png"
        self.WAVE_TEXTURE = self.TEXTURE_FOLDER + "wave.png"
        self.ISLAND_TEXTURE = self.TEXTURE_FOLDER + "island.png"
        self.BACKGROUND_TEXTURE = self.TEXTURE_FOLDER + "water.png"
        self.ARROW_TEXTURE = self.TEXTURE_FOLDER + "arrow.png"