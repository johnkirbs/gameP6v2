# 🧭 Island Navigator

**Island Navigator** is a Python-based boat navigation game where you steer through dynamic ocean currents to reach a distant island. Built using **Pygame**, this project combines vector-based steering, physics-based motion, and customizable gameplay for an immersive experience.

---

## 🚀 Game Overview

In **Island Navigator**, you control a boat that moves forward automatically while unpredictable ocean currents attempt to steer you off course. Your mission? Navigate the turbulent waters and safely reach the island!

---

## 🎮 Game Features

- 🌊 **Dynamic Wave System**  
  Unpredictable ocean currents with randomized direction and magnitude.

- 🧭 **Vector-Based Navigation**  
  Realistic steering mechanics based on heading and vector movement.

- ⚙️ **Physics-Based Boat Movement**  
  Boat motion is influenced by both your controls and wave forces.

- 📍 **Distance & Direction Indicators**  
  UI elements guide you toward your destination.

- 🖼️ **Customizable Graphics**  
  Easily replace textures and sprites to personalize your game.

- ⚙️ **Configurable Settings**  
  Tweak difficulty, boat handling, wave strength, and more.

---

## 📁 Project Structure

island-navigator/
├── main.py # Main entry point
├── game/
│ ├── init.py
│ ├── engine.py # Core game logic
│ ├── boat.py # Boat class and physics
│ ├── wave.py # Wave/current generator
│ └── player.py # Player control input
├── graphics/
│ ├── init.py
│ ├── renderer.py # Rendering engine
│ ├── sprites.py # Sprite management
│ └── animation.py # Animation framework
├── config/
│ ├── init.py
│ ├── settings.py # Gameplay & visual settings
│ └── controls.py # Key mappings
└── assets/
├── textures/ # PNG image assets
├── sounds/ # Sound effects (optional)
└── fonts/ # Game fonts


---

## ⚙️ Installation

1. **Clone the repository:**

```bash
git clone https://github.com/yourusername/island-navigator.git
cd island-navigator


pip install pygame
python main.py


🎮 Controls
Key	Action
← Arrow	Steer boat left
→ Arrow	Steer boat right
P	Pause game (optional)
R	Restart game (optional)

🔧 Customization
Settings
Modify config/settings.py to customize gameplay:
self.BOAT_SPEED = 1.5             # Boat speed
self.MAX_WAVE_MAGNITUDE = 3.5     # Wave force
self.WAVE_CHANGE_INTERVAL = 2000  # Wave change frequency (ms)

Graphics
Replace default textures in assets/textures/:
boat.png — Your boat
island.png — Target island
water.png — Ocean background
wave.png — Optional wave visuals
arrow.png — Optional direction arrow
