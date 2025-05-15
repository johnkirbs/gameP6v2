Quick Start Guide
Fixing the FileNotFoundError
You've encountered a FileNotFoundError because the game is looking for image assets that don't exist yet. Here's how to fix it:

Option 1: Generate Placeholder Assets (Recommended)
Run the included asset generator script to create basic placeholder images:
python asset_generator.py
This will create all required image files in the correct locations.
Option 2: Manual Directory Creation
If you prefer not to use the asset generator:

Create an assets folder in your project directory
Inside assets, create a textures folder
The game will now use basic shape drawings instead of image files



Running the Game
After fixing the asset issue, run the game with:
python main.py
Game Controls

Left Arrow Key: Steer boat left
Right Arrow Key: Steer boat right

Game Objective
Navigate the boat to reach the island while battling randomly changing ocean currents. The boat always moves forward automatically, but you must steer to control its direction.
Customizing the Game
To customize the game behavior, edit config/settings.py. Some useful settings to adjust:

BOAT_SPEED: How fast the boat moves
BOAT_ROTATION_SPEED: How quickly the boat turns
MIN_WAVE_MAGNITUDE and MAX_WAVE_MAGNITUDE: Range of current strengths
WAVE_CHANGE_INTERVAL: How often (in milliseconds) the currents change
ISLAND_DISTANCE: Distance to the target island

Creating Custom Graphics
If you want to create your own graphics, make PNG files with these names and place them in the assets/textures/ folder:

boat.png: Your boat graphic
water.png: Water/background texture
island.png: The target island
wave.png: Wave effect graphics (optional)
arrow.png: Direction indicator (optional)
