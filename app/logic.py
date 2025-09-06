# app/logic.py
# This file contains the core application logic (the "Controller").
# It handles user commands, manages state (like the shopping cart),
# performs background tasks (downloading, installing), and communicates
# results back to the UI via signals.

import subprocess
import threading
import os
import requests
import time
from urllib.parse import urlparse
from packaging.version import parse as parse_version

# --- Configuration Constants ---

# The URL to your online file containing the list of available applications.
# This should point to the raw version of your installer_garbage.py on a Gist or GitHub.
APP_LIST_URL = "https://gist.githubusercontent.com/Oenm176/6139afb6a8874015c6b72cc1970423d5/raw/gistfile1.txt"

# The URL to your online file containing the latest application version info.
VERSION_CHECK_URL = "https://raw.githubusercontent.com/Oenm176/Initverify/main/version.json"

# The current version of this application. Increment this for each new release.
CURRENT_VERSION = "1.0.0"


class CommandProcessor:
    """
    Handles all application logic, including command processing, state management (cart),
    and background tasks like downloading and installing.
    """
    def __init__(self, log_emitter, progress_emitter, status_emitter):
        """
        Initializes the CommandProcessor.

        Args:
            log_emitter (function): A callable to emit log messages to the UI.
            progress_emitter (QObject): A signal object for download progress.
            status_emitter (QObject): A signal object for online/offline status.
        """
        self.log_emitter = log_emitter
        self.progress_emitter = progress_emitter
        self.status_emitter = status_emitter
        self.apps_database = self._load_app_database()
        self.shopping_cart = set()
        self.awaiting_confirmation = False

        # Start background threads for checking app updates and internet connectivity.
        threading.Thread(target=self.check_for_updates, daemon=True).start()
        threading.Thread(target=self._check_connectivity_loop, daemon=True).start()

    def _check_connectivity_loop(self):
        """
        Periodically checks for internet connectivity in a background thread and
        emits a signal with the current status (online/offline).
        """
        while True:
            try:
                # Send a lightweight HEAD request to a highly available server (Google).
                requests.head("http://www.google.com", timeout=5)
                self.status_emitter.online_status_changed.emit(True)
            except (requests.ConnectionError, requests.Timeout):
                self.status_emitter.online_status_changed.emit(False)
            
            # Wait for 10 seconds before the next check.
            time.sleep(10)

    def _load_app_database(self):
        """
        Tries to load the application list from the online URL (APP_LIST_URL).
        If the online fetch fails for any reason (no internet, bad URL), it
        falls back to using the local, bundled `installer_garbage.py` file.
        """
        try:
            self.log_emitter("Fetching latest application list from the internet...", "info")
            response = requests.get(APP_LIST_URL, timeout=5)
            response.raise_for_status()

            # Safely execute the downloaded text to extract the AVAILABLE_APPS dictionary.
            local_scope = {}
            exec(response.text, {}, local_scope)
            apps = local_scope.get("AVAILABLE_APPS", {})

            if apps:
                self.log_emitter("Successfully fetched the latest application list.", "success")
                return apps
            else:
                raise ValueError("AVAILABLE_APPS variable not found in the online file.")

        except Exception as e:
            self.log_emitter(f"Failed to fetch online list: {e}", "warning")
            self.log_emitter("Using bundled (offline) application list as a fallback.", "warning")
            from .installer_garbage import AVAILABLE_APPS
            return AVAILABLE_APPS

    def check_for_updates(self):
        """
        Checks for a new application version from the VERSION_CHECK_URL in a
        background thread. If a newer version is found, it emits a log message
        to notify the user.
        """
        try:
            time.sleep(2)  # Small delay to not interfere with startup.
            response = requests.get(VERSION_CHECK_URL, timeout=5)
            response.raise_for_status()
            data = response.json()

            latest_version_str = data.get("latest_version")
            download_url = data.get("download_url")

            if not latest_version_str:
                return

            # Use the 'packaging' library to reliably compare semantic versions.
            if parse_version(latest_version_str) > parse_version(CURRENT_VERSION):
                if download_url:
                    update_message = (
                        f"Update available! Version {latest_version_str} is ready to download.\n"
                        f"Download here: <a href='{download_url}' style='color: #00BCD4;'>{download_url}</a>"
                    )
                else:
                    update_message = (
                        f"Update available! Version {latest_version_str} has been released.\n"
                        f"Please check the Releases page on the GitHub repository to download."
                    )
                self.log_emitter(update_message, "update")
        except Exception as e:
            # Fails silently to not interrupt the user if there's no internet.
            print(f"Failed to check for updates: {e}")

    def _find_app_url(self, app_name_to_find):
        """
        Searches for an application's URL within the nested dictionary structure
        of the app database.
        """
        for category in self.apps_database.values():
            if app_name_to_find in category:
                return category[app_name_to_find]
        return None

    def process_command(self, command_text):
        """
        The main command router. Parses user input from the UI and calls the
        appropriate handler function based on the command.
        """
        if self.awaiting_confirmation:
            self.handle_install_confirmation(command_text)
            return

        parts = command_text.split()
        command = parts[0].lower() if parts else ""
        args = parts[1:]

        command_map = {
            "show-apps": self.show_available_apps,
            "add": self.add_to_cart,
            "cart": self.show_cart,
            "remove": self.remove_from_cart,
            "remove-all": self.clear_cart,
            "install": self.initiate_installation,
            "help": self.show_help,
            "clear": lambda: self.log_emitter("clear_screen", "system_command"),
            "restart": lambda: self.log_emitter("restart_app", "system_command"),
        }

        handler = command_map.get(command)
        if handler:
            if command in ["add", "remove"]:
                handler(args)
            else:
                handler()
        else:
            self.log_emitter(f"Error: Command '{command}' not recognized. Type 'help' for assistance.", "error")

    def show_available_apps(self):
        """
        Formats and displays the list of available applications in a
        multi-column grid by generating an HTML table.
        """
        self.log_emitter("Available applications to install:", "info")
        
        if not self.apps_database:
            self.log_emitter("No application lists available.", "warning")
            return

        html_output = "<table style='width:100%'>"
        column_count = 0
        categories = list(self.apps_database.items())
        
        for i, (category_name, apps) in enumerate(categories):
            if column_count % 3 == 0:
                html_output += "<tr>"

            html_output += "<td style='vertical-align:top; padding-right: 20px; width:33%;'>"
            html_output += f"<b>--- {category_name} ---</b><br/>"
            
            for app_name in apps.keys():
                html_output += f"- {app_name}<br/>"
            
            html_output += "</td>"
            column_count += 1

            if column_count % 3 == 0 or i == len(categories) - 1:
                html_output += "</tr>"

        html_output += "</table>"
        self.log_emitter(html_output, "info")
        self.log_emitter("\nUse the 'add &lt;app_name1&gt; [app_name2] ...' command to add items.", "info")

    def add_to_cart(self, app_names):
        """Adds one or more specified applications to the shopping cart."""
        if not app_names:
            self.log_emitter("Error: Please specify an app name. Example: add steam vscode", "error")
            return
        for app_name in app_names:
            if self._find_app_url(app_name):
                if app_name in self.shopping_cart:
                    self.log_emitter(f"'{app_name}' is already in the cart.", "warning")
                else:
                    self.shopping_cart.add(app_name)
                    self.log_emitter(f"'{app_name}' has been added to the cart.", "success")
            else:
                self.log_emitter(f"Error: Application '{app_name}' was not found.", "error")
        self.show_cart()

    def show_cart(self):
        """Displays the current contents of the shopping cart to the user."""
        if not self.shopping_cart:
            self.log_emitter("Your shopping cart is currently empty.", "info")
        else:
            self.log_emitter("Current items in cart:", "info")
            for app_name in sorted(list(self.shopping_cart)):
                self.log_emitter(f"  - {app_name}", "info")
            self.log_emitter("\nUse 'install' to begin, 'remove &lt;app_name&gt;' to remove an item, or 'remove-all' to clear the cart.", "info")

    def remove_from_cart(self, app_names):
        """Removes one or more specified applications from the shopping cart."""
        if not app_names:
            self.log_emitter("Error: Please specify the app name to remove.", "error")
            return
        for app_name in app_names:
            if app_name in self.shopping_cart:
                self.shopping_cart.remove(app_name)
                self.log_emitter(f"'{app_name}' has been removed from the cart.", "success")
            else:
                self.log_emitter(f"Error: '{app_name}' is not in the cart.", "error")
        self.show_cart()

    def clear_cart(self):
        """Removes all items from the shopping cart."""
        if not self.shopping_cart:
            self.log_emitter("The cart is already empty.", "warning")
        else:
            self.shopping_cart.clear()
            self.log_emitter("All items have been removed from the cart.", "success")

    def initiate_installation(self):
        """
        Starts the installation confirmation process by listing cart items
        and asking for user confirmation (y/n).
        """
        if not self.shopping_cart:
            self.log_emitter("Cart is empty. Nothing to install.", "warning")
            return
        self.log_emitter("The following applications will be installed:", "info")
        for app_name in sorted(list(self.shopping_cart)):
            self.log_emitter(f"  - {app_name}", "info")
        self.log_emitter("\nDo you wish to continue? (y/n)", "user")
        self.awaiting_confirmation = True

    def handle_install_confirmation(self, response):
        """
        Handles the user's 'y/n' response. If 'yes', it starts the main
        installation process in a new thread.
        """
        response = response.lower()
        self.awaiting_confirmation = False
        if response in ['y', 'yes']:
            self.log_emitter("Confirmation received. Starting download and installation process...", "success")
            install_thread = threading.Thread(target=self.run_full_installation, daemon=True)
            install_thread.start()
        else:
            self.log_emitter("Installation cancelled. Your cart remains unchanged.", "warning")
            self.show_cart()

    def run_full_installation(self):
        """
        Manages the entire installation workflow for all apps in the cart.
        This runs in a background thread to keep the UI responsive.
        """
        download_folder = "installer_downloads"
        os.makedirs(download_folder, exist_ok=True)
        apps_to_install = list(self.shopping_cart)
        
        for app_name in apps_to_install:
            self.log_emitter(f"\n--- Processing '{app_name}' ---", "command")
            
            installer_url = self._find_app_url(app_name)
            if not installer_url:
                self.log_emitter(f"Could not find URL for '{app_name}'. Skipping.", "error")
                continue

            file_path = self._download_file(installer_url, download_folder, app_name)
            
            if not file_path:
                self.log_emitter(f"Failed to download '{app_name}'. Skipping to the next app.", "error")
                continue
            
            success = self._run_installer(file_path)
            
            if success:
                self.log_emitter(f"✅ Installation of '{app_name}' completed successfully.", "success")
                self.shopping_cart.remove(app_name)
            else:
                self.log_emitter(f"⚠️ Installation of '{app_name}' was likely cancelled or failed.", "warning")
        
        self.log_emitter("\n--- All installation processes have finished. ---", "info")
        if self.shopping_cart:
            self.log_emitter("Some applications remain in your cart:", "warning")
            self.show_cart()
        else:
            self.log_emitter("The shopping cart is now empty.", "success")

    def _download_file(self, url, folder, app_name):
        """
        Downloads a file from a URL, emitting progress signals along the way.
        It uses a browser-like User-Agent to avoid being blocked.
        """
        self.progress_emitter.started.emit(app_name)
        local_filepath = None
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }

            with requests.get(url, stream=True, allow_redirects=True, timeout=30, headers=headers) as r:
                r.raise_for_status()
                total_size = int(r.headers.get('content-length', 0))
                
                if 'content-disposition' in r.headers:
                    filename = r.headers['content-disposition'].split('filename=')[-1].strip("'\"")
                else:
                    filename = os.path.basename(urlparse(r.url).path) or f"{app_name}_installer.tmp"
                
                local_filepath = os.path.join(folder, filename)
                downloaded_size = 0
                start_time = time.time()
                last_update_time = start_time

                with open(local_filepath, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                        downloaded_size += len(chunk)
                        current_time = time.time()
                        
                        # Throttle progress updates to avoid overwhelming the UI.
                        if current_time - last_update_time > 0.2:
                            elapsed_time = current_time - start_time
                            if total_size > 0 and elapsed_time > 0:
                                speed = downloaded_size / elapsed_time
                                eta = (total_size - downloaded_size) / speed if speed > 0 else 0
                                percentage = (downloaded_size / total_size) * 100
                                
                                progress_data = {
                                    'percent': int(percentage),
                                    'downloaded': downloaded_size / (1024 * 1024),  # in MB
                                    'total': total_size / (1024 * 1024),      # in MB
                                    'speed': speed / (1024 * 1024),          # in MB/s
                                    'eta': eta                               # in seconds
                                }
                                self.progress_emitter.progress.emit(progress_data)
                                last_update_time = current_time

            self.log_emitter(f"Successfully downloaded to: {local_filepath}", "success")
            return local_filepath
        except Exception as e:
            self.log_emitter(f"Error during download: {e}", "error")
            return None
        finally:
            self.progress_emitter.finished.emit()
            if local_filepath and total_size > 0:
                 self.progress_emitter.progress.emit({
                     'percent': 100, 
                     'downloaded': total_size / (1024*1024), 
                     'total': total_size / (1024*1024), 
                     'speed': 0, 
                     'eta': 0
                })

    def _run_installer(self, file_path):
        """
        Runs an installer (.exe or .msi) and waits for it to complete.
        It intelligently chooses the correct execution method based on file extension.
        """
        self.log_emitter(f"Running installer: {file_path}", "command")
        self.log_emitter("Please complete the setup process in the window that appears...", "info")
        
        command_list = []
        if file_path.lower().endswith(".msi"):
            # Use the dedicated Windows Installer executable for .msi files.
            command_list = ["msiexec", "/i", file_path]
        else:
            # Execute .exe files directly.
            command_list = [file_path]
            
        try:
            # subprocess.run waits for the command to complete.
            process = subprocess.run(command_list, check=False)
            return process.returncode == 0
        except Exception as e:
            self.log_emitter(f"Failed to run installer: {e}", "error")
            return False

    def show_help(self):
        """Displays the help message with all available commands."""
        help_text = (
            "Available commands:\n"
            "  - show-apps                : Lists all available applications.\n"
            "  - add <app> [app2] ...     : Adds one or more apps to the cart.\n"
            "  - remove <app> [app2]...   : Removes apps from the cart.\n"
            "  - remove-all               : Removes all apps from the cart.\n"
            "  - cart                     : Shows the current contents of the cart.\n"
            "  - install                  : Starts the installation for items in the cart.\n"
            "  - clear                    : Clears the output screen.\n"
            "  - restart                  : Restarts the application.\n" 
            "  - help                     : Displays this help message."
        )
        self.log_emitter(help_text, "info")