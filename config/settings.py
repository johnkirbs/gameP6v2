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
        self.GOLD = (255, 215, 0)
        self.GRAY = (128, 128, 128)
        self.LIGHT_GRAY = (200, 200, 200)
        self.BROWN = (101, 67, 33)
        self.FOREST_GREEN = (34, 139, 34)
        
        # Game mechanics
        self.BOAT_SPEED = 1.5
        self.BOAT_ROTATION_SPEED = 2.0
        self.BOAT_BOOST_MULTIPLIER = 1.5
        self.BOAT_WAKE_LIFETIME = 1.0
        self.BOAT_WAKE_SIZE = 5
        
        # Current settings
        self.CURRENT_MAGNITUDE = 0.7
        self.CURRENT_DIRECTION = 45
        self.CURRENT_UPDATE_INTERVAL = 5000  # 5 seconds
        
        # Main target island settings
        self.ISLAND_DISTANCE_MIN = 400
        self.ISLAND_DISTANCE_MAX = 800
        self.ISLAND_RADIUS = 60
        self.ISLAND_GLOW_INTENSITY = 0.8
        
        # World generation settings
        self.MIN_FEATURE_DISTANCE = 200  # Minimum distance between features
        self.TREE_MIN_SIZE = 10
        self.TREE_MAX_SIZE = 15
        self.OTHER_BOAT_SIZE = 20
        self.MIN_ISLANDS = 3
        self.MAX_ISLANDS = 5
        self.TREES_PER_ISLAND_MIN = 2
        self.TREES_PER_ISLAND_MAX = 4
        self.MIN_OTHER_BOATS = 2
        self.MAX_OTHER_BOATS = 3
        
        # Initialize empty features list
        self.SEA_FEATURES = []
        
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
        
        # Success effect settings
        self.SUCCESS_FLASH_DURATION = 2000
        self.SUCCESS_TEXT_SIZE = 48
        self.SUCCESS_TEXT_COLOR = self.GOLD
        
        # Warning settings
        self.WARNING_DURATION = 2000
        self.WARNING_FADE_START = 1500
        self.WARNING_BG_COLOR = (255, 0, 0, 150)
        self.WARNING_TEXT_COLOR = self.WHITE
        
        # Notification settings
        self.NOTIFICATION_DURATION = 2000
        self.NOTIFICATION_BG_COLOR = (0, 0, 0, 180)
        self.NOTIFICATION_TEXT_COLOR = self.WHITE
        
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
        self.UI_FONT_SIZE = 24
        self.INSTRUCTION_FONT_SIZE = 36