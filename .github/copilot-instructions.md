<!-- .github/copilot-instructions.md for telescope_sim -->
# Copilot Instructions — Telescope Tracker Emulator

Keep guidance focused and actionable. This project is a modern Pygame-based desktop emulator for prototyping telescope tracking UX. Focus on the modular architecture and prefer clean, well-documented changes.

## Key Architecture Facts

**Entry Point**: `main.py` — Contains `TelescopeEmulator` class with proper initialization, game loop, and cleanup.

**Core Modules**:
- `config.py` — All constants, colors, and configuration
- `sensors.py` — Sensor simulation with noise and drift
- `modes.py` — ModeManager class handling state transitions
- `input_handler.py` — InputHandler class for keyboard controls
- `starfield.py` — Starfield rendering with celestial coordinates
- `tracker.py` — Coordinate conversion and tracking visuals
- `ui.py` — UIManager class for all UI rendering

**Coordinate Systems**:
- **Angular**: Azimuth (0-360°), Altitude (-90° to 90°)
- **Screen**: Pixels relative to starfield center
- **Conversion**: Tracker class handles angular ↔ screen mapping

## Common Edit Patterns

**UI Changes**:
- Add telemetry: Edit `ui.py` UIManager.draw_hud()
- Change status text: Edit `modes.py` ModeManager._update_status_text()
- Modify menus: Edit `ui.py` UIManager.draw_menu/draw_object_list()

**Visual Changes**:
- Star appearance: Edit `starfield.py` Starfield class
- Tracker indicators: Edit `tracker.py` Tracker class
- Colors/themes: Edit `config.py` COLORS dictionary

**Behavior Changes**:
- Movement speed: Edit `config.py` AZ_SPEED/ALT_SPEED
- Sensor behavior: Edit `sensors.py` SensorSimulator class
- Mode logic: Edit `modes.py` ModeManager methods

**Input Changes**:
- Add controls: Edit `input_handler.py` InputHandler._handle_keydown()
- Movement mapping: Edit `input_handler.py` InputHandler._update_continuous_movement()

## Integration Notes

**Thread Safety**: All modules are designed for single-threaded Pygame use.

**Performance**: Keep rendering under 33ms/frame (30 FPS target).

**State Sync**: ModeManager.target automatically syncs with tracker via main.py.

**Error Handling**: Use try/except in I/O operations, validate inputs.

**Testing**: Run `python main.py` after changes to verify functionality.

## Development Workflow

1. **Local Testing**: `python main.py` (requires pygame>=2.5.0)
2. **Fast Iteration**: Modify rendering modules, restart immediately
3. **State Verification**: Check mode transitions and coordinate conversions
4. **Performance Check**: Monitor FPS in console output

## Examples

**Add new telemetry field**:
```python
# In ui.py UIManager.draw_hud()
telemetry_lines.append(f"Battery: {battery_level}%")
```

**Implement new mode**:
```python
# In modes.py ModeManager.__init__()
self.modes.append("calibrate")

# In modes.py ModeManager.set_mode()
elif new_mode == "calibrate":
    self.status_text = "Calibrate: Follow instructions"
```

**Add star catalog**:
```python
# In starfield.py Starfield.__init__()
self.catalog = load_star_catalog()  # RA, Dec, magnitude

# In starfield.py Starfield.draw_starfield()
for star_data in self.catalog:
    pos = self._catalog_star_to_screen(star_data, az, alt)
```

## Constraints

**Do Not Change Without Confirmation**:
- Main game loop structure in `main.py`
- Core coordinate conversion logic
- Global constants in `config.py` (unless theming)
- Module interfaces (function signatures)

**Always Preserve**:
- Night-vision red color scheme
- 320×240 resolution compatibility
- Real-time 30 FPS performance
- Modular separation of concerns

## Searchable Anchors

Primary files: `main.py`, `modes.py`, `ui.py`, `tracker.py`, `starfield.py`
Config files: `config.py`, `sensors.py`, `input_handler.py`
Docs: `README.md`, `ROADMAP.md`

## Clarification Questions

- Coordinate system preferences?
- Performance vs. feature trade-offs?
- Target hardware constraints?
- UI/UX design priorities?

End of instructions.
