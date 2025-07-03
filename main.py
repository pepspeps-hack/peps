# Main application file

# The primary CLI logic has been moved to gui/app_gui.py for integration.
# This file will now just launch the GUI.

from gui.app_gui import start_gui

if __name__ == "__main__":
    start_gui()
