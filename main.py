# main.py
# This is the main entry point for the application.
# Its primary role is to initialize the application components (View and Logic),
# connect them, and start the event loop.

import sys
import os
from PySide6.QtWidgets import QApplication

# Import the main application classes from the 'app' package
from app.main_window import SilentInstallerApp
from app.logic import CommandProcessor

# --- Define the project's root directory ---
# This logic correctly determines the root path for both development (.py)
# and deployed (.exe) modes.
if getattr(sys, 'frozen', False):
    # If the application is run as a bundled executable by PyInstaller,
    # sys.executable points to the .exe file itself.
    ROOT_DIR = os.path.dirname(sys.executable)
else:
    # If running as a .py script, __file__ points to this script.
    ROOT_DIR = os.path.dirname(os.path.realpath(__file__))
# -------------------------------------------


def main():
    """Initializes, connects, and runs the main application components."""

    # CRITICAL FIX: Set the current working directory to the project root.
    # This solves issues where elevated processes default to C:\Windows\System32
    # and ensures files like 'architecture.json' are saved in the correct place.
    os.chdir(ROOT_DIR)

    # Initialize the core Qt application instance.
    app = QApplication(sys.argv)

    # Create the main window (the "View") and pass it the project's root directory.
    window = SilentInstallerApp(root_dir=ROOT_DIR)

    # Create the command processor (the "Logic") and inject the window's
    # signal emitters and the root_dir so the logic can communicate back to the UI
    # and create files in the correct location.
    processor = CommandProcessor(
        log_emitter=window.log_message,
        progress_emitter=window.progress_signal,
        status_emitter=window.status_signal,
        root_dir=ROOT_DIR
    )

    # Link the main window to its command processor.
    window.set_command_processor(processor)

    # Display the main window to the user.
    window.show()

    # Start the application's event loop. When the app closes, this will
    # return an exit code (e.g., 0 for normal exit, 5 for restart).
    return app.exec()


if __name__ == "__main__":
    # This standard Python construct ensures that main() is called
    # only when this script is executed directly.
    exit_code = main()
    # Exit the script with the code provided by the application.
    # The run.py script will read this code to decide whether to restart.
    sys.exit(exit_code)