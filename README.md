# Telescope Tracker Emulator

A modern desktop emulator built in **Python + Pygame** for prototyping the UX and logic of a micropython-esp32c3 based **telescope tracking assistant**.
The real-world target is a compact ESP32-S3-based device with an IMU, compass, GPS, and small TFT display that guides users to align and track celestial objects on an Alt-Az mount.

---

## 🪐 Overview

This emulator provides a complete simulation of telescope tracking functionality:

- **Realistic Alt/Az Motion**: Smooth telescope movement with keyboard controls
- **Dynamic Starfield**: Moving starfield that responds to telescope orientation
- **Target Tracking**: Visual indicators and directional arrows for target guidance
- **Multi-Mode Interface**: Complete UX for alignment, object selection, and tracking
- **Sensor Simulation**: Realistic IMU/compass simulation with configurable noise

### Key Features

- **Align Mode**: Calibrate telescope by centering on known stars
- **Select Mode**: Browse and choose from celestial object database
- **Track Mode**: Real-time target following with visual guidance
- **Menu Mode**: Main navigation and system control

---

## 🧩 Project Structure

```
telescope_sim/
│
├── main.py             # Main application class and game loop
├── config.py           # Configuration constants and colors
├── sensors.py          # Simulated sensor data with noise
├── modes.py            # Mode management and state transitions
├── input_handler.py    # Comprehensive input processing
├── starfield.py        # Starfield rendering and celestial objects
├── tracker.py          # Coordinate conversion and tracking visuals
├── ui.py               # UI rendering and overlay management
├── requirements.txt    # Python dependencies
├── README.md           # This file
├── ROADMAP.md          # Development roadmap
└── .gitignore          # Git ignore rules
```

---

## ⚙️ Installation & Setup

### Prerequisites
- Python 3.8+
- pip package manager
- Micropython 1.13+ (for esp32s3)

### Installation Steps (for emulation)

1. **Clone the repository:**
   ```bash
   git clone https://github.com/m-anish/telescope_sim.git
   cd telescope_sim
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the emulator:**
   ```bash
   python3 main.py
   ```

---

## 🎮 Controls

### Telescope Movement
| Key           | Action                        |
|---------------|-------------------------------|
| ← / → / A / D | Rotate Azimuth (continuous)   |
| ↑ / ↓ / W / S | Adjust Altitude (continuous)  |

### Mode Navigation
| Key       | Action                        |
|-----------|-------------------------------|
| Enter     | Confirm/Select/Next mode      |
| ↑ / ↓     | Navigate menus/lists          |
| Esc       | Back to menu/Quit             |

---

## 🖥️ User Interface

### Display Layout
```
+----------------------------------------+
| AZ:120.0°  ALT:45.0°                   | ← HUD (telemetry)
| Target→ AZ:150.0° ALT:47.0°            |
|                                        |
|        [starfield with tracking]       | ← Main view
|        *     ↑     *                   |
|         ↖   │   ↗                      |
|                                        |
| Align: Adjust to known star [ALIGN]    | ← Status bar
+----------------------------------------+
```

### User Flow
- On first start, go to **Menu mode** with the following items
  - Align (showing current status needed/aligned)
  - Select
  - Exit
- **Align mode**: Just move the telescope to a known Alt/Az point for now, navigating with arrow keys, and press enter to align. After pressing enter, show a message for a could of seconds that we are aligned, and revert to main menu
- **Select mode**: Scrollable list of some items (make a basic list for now), allowing user to navigate with arrow keys, and pressing enter to select. Upon pressing Enter, enter **Track mode**. Pressing Esc reverts to **Menu mode**
- **Track mode**: Only accessible from the **Select mode**, show the star field with arrows pointing towards the object. Pressing Esc reverts to **Select mode**

### Interface Elements
- **HUD**: Real-time telemetry (azimuth, altitude, target info)
- **Starfield**: Dynamic star display with magnitude-based brightness
- **Tracker**: Target crosshairs and directional arrows
- **Status Bar**: Current mode and instructions
- **Overlays**: Context menus, object lists, alignment guides

---

## 🔧 Configuration

Key settings in `config.py`:
- **Display**: 320×240 resolution, 30 FPS
- **Colors**: Night-vision red theme
- **Movement**: Speed and smoothing parameters
- **Starfield**: 200 stars, magnitude ranges
- **Sensors**: Noise levels and update rates

---

## 🌟 Technical Features

- **Modular Architecture**: Clean separation of concerns
- **Real-time Simulation**: Smooth 30 FPS rendering
- **Sensor Modeling**: Realistic IMU/compass behavior
- **Coordinate Systems**: Proper angular to screen conversion
- **State Management**: Robust mode transitions
- **Input Handling**: Continuous and discrete controls

---

## 🧠 Development Notes

This project serves as a **complete UX design sandbox** for embedded telescope tracking hardware. All interaction logic, visual feedback, and user flows are prototyped here before porting to the ESP32-S3 target platform.

### Architecture Principles
- **Separation of Concerns**: Each module has a single responsibility
- **Testability**: Modular design enables easy testing
- **Extensibility**: Clean interfaces for future enhancements
- **Performance**: Optimized for real-time rendering
- **Code Reuse**: The code should sense if it is in emulation mode (i.e. running on PC with pygame, numpy, python3 etc. or actual hardware). For now, we will only develop the logic for running on PC. If the code is run on actual hardware, right now it does nothing, but we want to reuse parts of the library there. 

---

## 📋 Roadmap Status

See [ROADMAP.md](ROADMAP.md) for detailed development phases:

- ✅ **Stage 1**: Emulator foundation (planned)
- 🔄 **Stage 2**: Enhanced sky simulation (planned)
- ⏳ **Stage 3**: Embedded port (planned)
- ⏳ **Stage 4-7**: Advanced features (planned)

---

## 🤝 Contributing

This is a personal project for prototyping embedded telescope tracking UX. The codebase is designed to be clean, well-documented, and easily extensible for future development phases.

---

**Author**: Anish Mangal
**License**: GPLv3
**Status**: Active Development
