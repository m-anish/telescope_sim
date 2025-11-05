# Placeholder for mode management.
# This module will handle state transitions between Menu, Align, Select, and Track modes.
# For now, it's empty as the current task focuses on the visualizer.

class ModeManager:
    """Manages the different application modes."""
    def __init__(self):
        self.current_mode = "MENU" # Default mode

    def switch_mode(self, new_mode):
        """Switches the application to a new mode."""
        self.current_mode = new_mode
        print(f"Switched to mode: {self.current_mode}")

    def get_current_mode(self):
        """Returns the current mode."""
        return self.current_mode
