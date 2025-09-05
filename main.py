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

# Define the absolute path to the project's root directory.
# This is crucial for finding assets and fixing working directory issues when elevated.
ROOT_DIR = os.path.dirname(os.path.realpath(__file__))


def main():
    """Initializes, connects, and runs the main application components."""

    # CRITICAL FIX: Set the current working directory to the project root.
    # This solves issues where elevated processes default to C:\Windows\System32.
    os.chdir(ROOT_DIR)

    # Initialize the core Qt application instance.
    app = QApplication(sys.argv)

    # Create the main window (the "View") and pass it the project's root directory.
    window = SilentInstallerApp(root_dir=ROOT_DIR)

    # Create the command processor (the "Logic") and inject the window's
    # signal emitters so the logic can communicate back to the UI.
    processor = CommandProcessor(
        log_emitter=window.log_message,
        progress_emitter=window.progress_signal
    )

    # Link the main window to its command processor.
    window.set_command_processor(processor)

    # Display the main window to the user.
    window.show()

    # Start the application's event loop and ensure a clean exit.
    sys.exit(app.exec())


if __name__ == "__main__":
    # This standard Python construct ensures that main() is called
    # only when this script is executed directly.
    main()