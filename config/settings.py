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
        self.SAND_COLOR = (238, 214, 175)
        self.RED = (255, 0, 0)
        
        # Game mechanics
        self.BOAT_SPEED = 1.5
        self.BOAT_ROTATION_SPEED = 2.0
        self.BOAT_BOOST_MULTIPLIER = 1.5
        self.BOAT_WAKE_LIFETIME = 1.0
        self.BOAT_WAKE_SIZE = 5
        
        # Current settings (fixed)
        self.CURRENT_MAGNITUDE = 0.7
        self.CURRENT_DIRECTION = 45
        
        # Main target island settings
        self.ISLAND_DISTANCE = 1000  # Reduced from 3000 to 1000
        self.ISLAND_RADIUS = 80
        self.ISLAND_GLOW_INTENSITY = 0.5
        
        # Decorative islands settings (adjusted for shorter distance)
        self.DECORATIVE_ISLANDS = [
            {"x": 500, "y": 300, "size": 60},
            {"x": -400, "y": 400, "size": 40},
            {"x": 600, "y": -200, "size": 50},
            {"x": -500, "y": -300, "size": 45},
            {"x": 700, "y": 400, "size": 55},
        ]
        
        # Wave/current settings
        self.MIN_WAVE_MAGNITUDE = 0.3
        self.MAX_WAVE_MAGNITUDE = 1.5
        self.WAVE_CHANGE_INTERVAL = 4000
        self.WAVE_PARTICLE_COUNT = 20
        
        # Visual effects
        self.WATER_RIPPLE_SPEED = 0.5
        self.WATER_RIPPLE_SIZE = 2.0
        self.PARTICLE_ALPHA_DECAY = 0.02
        self.PARTICLE_SIZE_DECAY = 0.95
        
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
        
        # UI settings
        self.UI_OPACITY = 0.8
        self.COMPASS_SIZE = 90
        self.COMPASS_MARGIN = 20
        self.DISTANCE_FONT_SIZE = 30