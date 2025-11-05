# Telescope Tracker Emulator — Development Roadmap

## 🎯 Goal
A compact telescope-mounted assistant that helps users find and track celestial objects
using simple sensors (compass, accelerometer, gyro, GPS/RTC) and a clean night-vision UI.

---

## 🧱 Stage 1 — Emulator Foundation
**Status:** In Progress

### Features
- [ ] Pygame-based visual emulator (320×240)
- [ ] Night-mode display (red on black)
- [ ] Menu navigation system (Align / Select / Track / Exit)
- [ ] Basic starfield rendering and camera panning
- [ ] Target tracking arrow overlay
- [ ] Scrollable object list for “Select Object”

### Next Tasks
- [ ] Implement 1-star “alignment” offset logic
- [ ] Add smoother telescope movement (gradual instead of step-by-step)
- [ ] Simulate sensor noise (gyro/compass drift)

---

## 🧭 Stage 2 — Enhanced Sky Simulation
**Goal:** Make the emulator feel like a real sky map.

### Planned Features
- [ ] Load small star catalog (e.g., Bright Star Catalog subset or Hipparcos < 3.0 mag)
- [ ] Real-time clock → simulate Earth rotation (RA/Dec to Alt/Az)
- [ ] Optional FOV grid and coordinate overlay
- [ ] Display object info popup (name, type, magnitude)
- [ ] Zoom/FOV control (simulate narrow telescope view)

---

## ⚙️ Stage 3 — Embedded Port (ESP32-S3)
**Goal:** Migrate to microcontroller hardware for real telescope use.

### Hardware Targets
- MCU: ESP32-S3 (dual-core, Wi-Fi/BLE, good graphics support)
- Display: 2.4–2.8″ TFT (ST7789/ILI9341)
- Sensors: LSM6DS3 (gyro+accel), HMC5883L or LIS3MDL (compass), DS3231 (RTC)
- GPS: optional NEO-6M or user-input lat/lon

### Software Tasks
- [ ] Port Pygame UI → TFT graphics (e.g., LovyanGFX or TFT_eSPI)
- [ ] Abstract input methods (buttons / rotary encoder / touchscreen)
- [ ] Implement persistent settings storage (EEPROM or flash)
- [ ] Integrate IMU + compass fusion for pointing vector
- [ ] Add GPS/time sync

---

## 🔭 Stage 4 — Alignment & Calibration
**Goal:** Accurate pointing advice based on known-star calibration.

### Tasks
- [ ] Implement 1-star alignment (offset correction)
- [ ] Implement 2-star alignment (rotation + offset)
- [ ] Show alignment progress / success UI feedback
- [ ] Option to save calibration data between sessions

---

## 🌌 Stage 5 — Object Database & Guidance
**Goal:** Intelligent guidance with visual feedback.

### Planned Features
- [ ] Filter visible objects by date/time/location
- [ ] “Tonight’s Best Objects” auto list
- [ ] Real-time arrow guidance with distance-to-target metric
- [ ] Optional “Starfield mode” to browse the sky manually

---

## 🧪 Stage 6 — UX Polishing
**Goal:** Refine the interaction for simplicity and field usability.

### Planned Features
- [ ] Night-mode toggle (red / white)
- [ ] Smoothed transitions and animations
- [ ] Optional joystick support
- [ ] On-screen FOV circle showing telescope pointing
- [ ] “Center target” confirmation prompt

---

## 🛰️ Stage 7 — Expansion & Connectivity
**Goal:** Optional extensions once core is stable.

### Ideas
- [ ] Bluetooth link to mobile app (for richer object database)
- [ ] Wi-Fi update mode
- [ ] Serial/USB debugging overlay
- [ ] Integration with motorized alt-az mounts for auto-tracking

---

## 🧩 Stretch Goals
- [ ] Support for equatorial mount coordinate mode
- [ ] Basic astrophotography framing helper
- [ ] Cross-platform desktop build (PyInstaller .exe or .app)
- [ ] Multi-language support (UI localization)

---

## 📅 Suggested Development Order
| Phase | Feature Area | Priority |
|:------|:--------------|:----------|
| 1 | Basic emulator and UI loop | ⭐⭐⭐⭐ |
| 2 | Alignment simulation and offsets | ⭐⭐⭐ |
| 3 | Star catalog and dynamic sky | ⭐⭐⭐ |
| 4 | Embedded port + display driver | ⭐⭐⭐⭐ |
| 5 | Real sensor integration (IMU, compass) | ⭐⭐⭐⭐ |
| 6 | UX polish and field testing | ⭐⭐ |
| 7 | Expansion features | ⭐ |

---

**Author:** Anish Mangal  
**Project Type:** Personal / Open hardware  
**License:** TBD (likely MIT or Apache 2.0)

