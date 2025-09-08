# app/main_window.py
# This file defines the main user interface (the "View") of the application.
# It is responsible for creating all widgets, handling UI events, and displaying
# information received from the logic component.

import os
import sys
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout,
    QLabel,
    QTextEdit, QLineEdit, QPushButton, QSizePolicy, QApplication
)
from PySide6.QtCore import Signal, QObject, Qt, QRectF, QSize
from PySide6.QtGui import (
    QFont, QColor, QPalette, QIcon, QTextCursor
)

def resource_path(relative_path):
    """
    Gets the absolute path to a resource, which works for both development
    mode and for a bundled PyInstaller executable.
    """
    try:
        # PyInstaller creates a temp folder and stores its path in _MEIPASS.
        base_path = sys._MEIPASS
    except Exception:
        # In development, the base path is the current working directory.
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

class LogSignal(QObject):
    """A signal object to safely pass log messages across threads."""
    log_message = Signal(str, str)  # Emits: message, message_type

class ProgressSignal(QObject):
    """A signal object to safely pass download progress data across threads."""
    started = Signal(str)      # Emits when a download starts -> sends app_name
    progress = Signal(dict)    # Emits during download -> sends progress data dictionary
    finished = Signal()        # Emits when a download is finished or has failed

class StatusSignal(QObject):
    """A signal object to safely pass online/offline status across threads."""
    online_status_changed = Signal(bool) # Emits True for online, False for offline

class SilentInstallerApp(QWidget):
    """The main application window class."""

    def __init__(self, root_dir):
        """
        Initializes the main window.

        Args:
            root_dir (str): The absolute path to the project's root directory.
        """
        super().__init__()
        self.root_dir = root_dir
        self.command_processor = None
        
        # Instantiate the signal objects for cross-thread communication.
        self.log_signal = LogSignal()
        self.progress_signal = ProgressSignal()
        self.status_signal = StatusSignal()

        # Connect signals to their corresponding handler methods (slots).
        self.log_signal.log_message.connect(self.append_log)
        self.progress_signal.started.connect(self.on_download_started)
        self.progress_signal.progress.connect(self.on_progress_updated)
        self.progress_signal.finished.connect(self.on_download_finished)
        self.status_signal.online_status_changed.connect(self.update_status_indicator)
        
        # Initialize the user interface.
        self.init_ui()

    def set_command_processor(self, processor):
        """
        Links this View to its Logic controller (CommandProcessor).
        This is a form of dependency injection set up by main.py.
        """
        self.command_processor = processor
        self.command_input.returnPressed.connect(self._handle_command_entered)

    def _handle_command_entered(self):
        """
        Slot that triggers when the user presses Enter in the command input field.
        It forwards the command to the logic processor for handling.
        """
        if not self.command_processor: return
        command_text = self.command_input.text().strip()
        if not command_text: return

        # Avoid logging confirmation answers (like 'y' or 'n') as if they were commands.
        if not self.command_processor.awaiting_confirmation:
            self.log_message(f"> {command_text}", "user")
        
        self.command_processor.process_command(command_text)
        self.command_input.clear()

    def init_ui(self):
        """Creates and arranges all the widgets in the main window."""
        # --- Main Window Setup ---
        self.setWindowTitle('InitVerify.')
        self.setGeometry(100, 100, 800, 600)
        
        # Use the resource_path helper to ensure the icon is found in the bundled .exe
        icon_path = resource_path("logo_ico.ico")
        self.setWindowIcon(QIcon(icon_path))
        
        # --- Dark Theme Palette ---
        dark_palette = self.palette()
        dark_palette.setColor(QPalette.ColorRole.Window, QColor(40, 44, 52))
        dark_palette.setColor(QPalette.ColorRole.WindowText, QColor(200, 200, 200))
        dark_palette.setColor(QPalette.ColorRole.Base, QColor(25, 29, 36))
        dark_palette.setColor(QPalette.ColorRole.AlternateBase, QColor(35, 39, 46))
        dark_palette.setColor(QPalette.ColorRole.Text, QColor(200, 200, 200))
        dark_palette.setColor(QPalette.ColorRole.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.ColorRole.HighlightedText, QColor(0, 0, 0))
        self.setPalette(dark_palette)
        
        # --- Layouts ---
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # --- Header Widget ---
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: #2D4059; padding: 10px; border-bottom: 1px solid #21252B;")
        header_layout = QVBoxLayout(header_widget) 
        header_title = QLabel("INITVERIFY - CLI")
        header_title.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
        header_title.setStyleSheet("color: #E0FBFC; background: transparent; border: none;")
        header_layout.addWidget(header_title)
        main_layout.addWidget(header_widget)
        
        # --- Output Display (QTextEdit) ---
        self.output_display = QTextEdit()
        self.output_display.setReadOnly(True)
        self.output_display.setStyleSheet("background-color: #282C34; color: #ABB2BF; border: none; padding: 10px; font-family: 'Consolas'; font-size: 10pt;")
        main_layout.addWidget(self.output_display, 1)
        
        # --- Input Container ---
        input_container = QWidget()
        input_container.setStyleSheet("background-color: #21252B; padding: 10px;")
        input_layout = QVBoxLayout(input_container)
        # Set margins (left, top, right, bottom). The right margin is larger for padding.
        input_layout.setContentsMargins(10, 5, 20, 10)
        input_layout.setSpacing(5)

        # --- Prompt Bar (contains "Command Prompt" label and status indicator) ---
        prompt_bar_layout = QHBoxLayout()
        prompt_bar_layout.setContentsMargins(0,0,0,0)
        
        command_label = QLabel("Command Prompt")
        command_label.setFont(QFont("Segoe UI", 9))
        
        # Use a simple QLabel for the status indicator, as its text is set with rich HTML.
        self.status_indicator = QLabel()
        
        # Arrange the prompt bar: [Label] -> [Expanding Space] -> [Indicator]
        prompt_bar_layout.addWidget(command_label)
        prompt_bar_layout.addStretch()
        prompt_bar_layout.addWidget(self.status_indicator)
        
        input_layout.addLayout(prompt_bar_layout)
        
        # --- Command Input (QLineEdit) ---
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Type the command here.")
        self.command_input.setStyleSheet("""
            QLineEdit { background-color: #282C34; color: #D3D7DF; border: 1px solid #3E4A51; 
                         padding: 8px; border-radius: 4px; font-family: 'Consolas'; font-size: 10pt; }""")
        
        input_layout.addWidget(self.command_input)
        main_layout.addWidget(input_container)

        # --- Finalize Layout ---
        self.setLayout(main_layout)
        self.log_message("The terminal is ready. Type ‘help’ to see a list of commands.", "info")
        self.update_status_indicator(False) # Set initial status to Offline

    def update_status_indicator(self, is_online):
        """Slot to update the online/offline status indicator using rich text."""
        if is_online:
            # Combine a unicode character (●) and text into a single HTML string.
            rich_text = "<span style='font-size: 14pt; color: lime;'>●</span> <b style='color: #4CAF50;'>Online</b>"
        else:
            rich_text = "<span style='font-size: 14pt; color: red;'>●</span> <b style='color: #F44336;'>Offline</b>"
        
        self.status_indicator.setText(rich_text)

    def on_download_started(self, app_name):
        """Slot to handle the start of a download. Disables the command input."""
        self.append_log(f"Downloading {app_name}...", "info")
        self.output_display.append("") # Add a blank line for the progress bar
        self.command_input.setEnabled(False)

    def on_progress_updated(self, progress_data):
        """Slot to handle progress updates. Redraws the text-based progress bar."""
        progress_string = self._format_progress_string(progress_data)
        
        # Use QTextCursor to overwrite the last line of the text edit.
        cursor = self.output_display.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.select(QTextCursor.SelectionType.BlockUnderCursor)
        cursor.removeSelectedText()
        cursor.insertBlock()
        cursor.insertHtml(progress_string) # Use insertHtml to render colored text.
        self.output_display.setTextCursor(cursor)

    def on_download_finished(self):
        """Slot to handle the end of a download. Re-enables the command input."""
        self.command_input.setEnabled(True)
        self.command_input.setFocus()

    def _format_progress_string(self, data):
        """Helper function to create the formatted HTML string for the progress bar."""
        percent = data.get('percent', 0)
        bar_length = 40
        filled_length = int(bar_length * percent // 100)
        bar = '█' * filled_length + '░' * (bar_length - filled_length)
        
        downloaded = f"{data.get('downloaded', 0):.1f}"
        total = f"{data.get('total', 0):.1f}"
        speed = f"{data.get('speed', 0):.1f}"
        eta = data.get('eta', 0)
        eta_str = f"{int(eta // 60):02d}:{int(eta % 60):02d}"

        # Return a formatted HTML string with colors.
        return (f"<span style='color: #d55fde;'>{bar}</span> "
                f"<span style='color: #4CAF50;'>{downloaded}/{total} MB</span> "
                f"<span style='color: #4CAF50;'>{speed} MB/s</span> "
                f"<span style='color: #00BCD4;'>eta {eta_str}</span>")

    def append_log(self, message, message_type="info"):
        """
        Slot that appends a colored, formatted message to the output display.
        Also handles special system commands like 'clear' and 'restart'.
        """
        if message_type == "system_command":
            if message == "clear_screen":
                self.output_display.clear()
                return
            elif message == "restart_app":
                # Exit the application with the special restart code (5).
                QApplication.instance().exit(5)
                return
        
        color_map = {
            "info": "#ABB2BF", "success": "#98C379", "warning": "#E5C07B", 
            "error": "#E06C75", "command": "#61AFEF", "user": "#E5C07B",
            "update": "#E0FBFC"
        }
        color = color_map.get(message_type, "#ABB2BF")
        self.output_display.append(f"<span style='white-space: pre-wrap; color: {color};'>{message}</span>")

    def log_message(self, message, msg_type):
        """Helper method to safely emit a log signal."""
        self.log_signal.log_message.emit(message, msg_type)