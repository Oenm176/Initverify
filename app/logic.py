# app/logic.py

import subprocess
import threading
import os
import requests
import time
import json
import sys
import platform
import psutil
from urllib.parse import urlparse
from packaging.version import parse as parse_version

# --- Configuration Constants ---
APP_LIST_URL = "https://gist.githubusercontent.com/Oenm176/6139afb6a8874015c6b72cc1970423d5/raw/gistfile1.txt"
VERSION_CHECK_URL = "https://raw.githubusercontent.com/Oenm176/Initverify/main/version.json"
CURRENT_VERSION = "1.0.0"

class CommandProcessor:
    def __init__(self, log_emitter, progress_emitter, status_emitter):
        self.log_emitter = log_emitter
        self.progress_emitter = progress_emitter
        self.status_emitter = status_emitter
        self.apps_database = self._load_app_database()
        self.shopping_cart = set()
        self.awaiting_confirmation = False
        threading.Thread(target=self.check_for_updates, daemon=True).start()
        threading.Thread(target=self._check_connectivity_loop, daemon=True).start()

    def _check_connectivity_loop(self):
        while True:
            try:
                requests.head("http://www.google.com", timeout=5)
                self.status_emitter.online_status_changed.emit(True)
            except (requests.ConnectionError, requests.Timeout):
                self.status_emitter.online_status_changed.emit(False)
            time.sleep(10)

    def _load_app_database(self):
        try:
            self.log_emitter("Fetching latest application list from the internet...", "info")
            response = requests.get(APP_LIST_URL, timeout=5)
            response.raise_for_status()
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
        try:
            time.sleep(2)
            response = requests.get(VERSION_CHECK_URL, timeout=5)
            response.raise_for_status()
            data = response.json()
            latest_version_str = data.get("latest_version")
            download_url = data.get("download_url")
            if not latest_version_str: return
            if parse_version(latest_version_str) > parse_version(CURRENT_VERSION):
                if download_url:
                    update_message = (f"Pembaruan tersedia! Versi {latest_version_str} siap diunduh.\n"
                                      f"Download di sini: <a href='{download_url}' style='color: #00BCD4;'>{download_url}</a>")
                else:
                    update_message = (f"Pembaruan tersedia! Versi {latest_version_str} telah dirilis.\n"
                                      f"Silakan periksa halaman Rilis di repositori GitHub untuk men-download.")
                self.log_emitter(update_message, "update")
        except Exception as e:
            print(f"Failed to check for updates: {e}")

    def _is_64bit_windows(self):
        return platform.machine().endswith('64')
        
    def _find_app_url(self, app_name_to_find):
        is_64bit = self._is_64bit_windows()
        for category in self.apps_database.values():
            if app_name_to_find in category:
                app_data = category[app_name_to_find]
                if is_64bit:
                    return app_data.get("url_64") or app_data.get("url_32")
                else:
                    return app_data.get("url_32")
        return None

    def process_command(self, command_text):
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
            "sys-info": self.create_system_profile,
            "show-sys-info": self.show_system_profile,
        }
        handler = command_map.get(command)
        if handler:
            if command in ["add", "remove"]: handler(args)
            else: handler()
        else:
            self.log_emitter(f"Error: Command '{command}' not recognized. Type 'help' for assistance.", "error")

    def create_system_profile(self):
        try:
            self.log_emitter("Mengumpulkan profil sistem...", "info")
            ram = psutil.virtual_memory()
            disk = psutil.disk_usage('C:')
            system_info = {
                "operating_system": { "system": platform.system(), "release": platform.release(), "version": platform.version() },
                "hardware": {
                    "architecture": platform.architecture()[0], "processor": platform.processor(),
                    "ram_total_gb": round(ram.total / (1024**3), 1),
                    "disk_c": { "total_gb": round(disk.total / (1024**3), 1), "free_gb": round(disk.free / (1024**3), 1) }
                },
                "python_environment": { "version": sys.version }
            }
            file_path = "architecture.json"
            with open(file_path, 'w') as f:
                json.dump(system_info, f, indent=4)
            self.log_emitter(f"Profil sistem berhasil disimpan ke {file_path}", "success")
        except Exception as e:
            self.log_emitter(f"Gagal membuat profil sistem: {e}", "error")

    def show_system_profile(self):
        try:
            file_path = "architecture.json"
            with open(file_path, 'r') as f:
                data = json.load(f)
            formatted_json = json.dumps(data, indent=4)
            self.log_emitter("Menampilkan isi dari architecture.json:", "info")
            self.log_emitter(f"<pre>{formatted_json}</pre>", "info")
        except FileNotFoundError:
            self.log_emitter(f"Error: File '{file_path}' tidak ditemukan.", "error")
            self.log_emitter("Silakan jalankan perintah 'sys-info' terlebih dahulu.", "info")
        except Exception as e:
            self.log_emitter(f"Gagal membaca file profil sistem: {e}", "error")

    def show_help(self):
        help_text = (
            "Available commands:\n"
            "  - show-apps                : Lists all available applications.\n"
            "  - add <app> [app2] ...   : Adds one or more apps to the cart.\n"
            "  - remove <app> [app2]... : Removes apps from the cart.\n"
            "  - remove-all               : Removes all apps from the cart.\n"
            "  - cart                     : Shows the current contents of the cart.\n"
            "  - install                  : Starts the installation for items in the cart.\n"
            "  - clear                    : Clears the output screen.\n"
            "  - restart                  : Restarts the application.\n"
            "  - sys-info                 : Creates/updates the system profile file (architecture.json).\n"
            "  - show-sys-info            : Displays the content of architecture.json.\n"
            "  - help                     : Displays this help message."
        )
        self.log_emitter(help_text, "info")

    def show_available_apps(self):
        self.log_emitter("Available applications to install:", "info")
        if not self.apps_database:
            self.log_emitter("No application lists available.", "warning")
            return
        html_output = "<table style='width:100%'>"
        column_count = 0
        categories = list(self.apps_database.items())
        for i, (category_name, apps) in enumerate(categories):
            if column_count % 3 == 0: html_output += "<tr>"
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
        self.log_emitter("\nUse the 'add &lt;nama_app1&gt; [nama_app2] ...' command to add items.", "info")

    def add_to_cart(self, app_names):
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
        if not self.shopping_cart: self.log_emitter("Your shopping cart is currently empty.", "info")
        else:
            self.log_emitter("Current items in cart:", "info")
            for app_name in sorted(list(self.shopping_cart)):
                self.log_emitter(f"  - {app_name}", "info")
            self.log_emitter("\nUse 'install' to begin, 'remove &lt;nama_aplikasi&gt;' to remove an item, or 'remove-all' to clear the cart.", "info")

    def remove_from_cart(self, app_names):
        if not app_names:
            self.log_emitter("Error: Please specify the app name to remove.", "error"); return
        for app_name in app_names:
            if app_name in self.shopping_cart:
                self.shopping_cart.remove(app_name)
                self.log_emitter(f"'{app_name}' has been removed from the cart.", "success")
            else:
                self.log_emitter(f"Error: '{app_name}' is not in the cart.", "error")
        self.show_cart()

    def clear_cart(self):
        if not self.shopping_cart: self.log_emitter("The cart is already empty.", "warning")
        else: self.shopping_cart.clear(); self.log_emitter("All items have been removed from the cart.", "success")

    def initiate_installation(self):
        if not self.shopping_cart: self.log_emitter("Cart is empty. Nothing to install.", "warning"); return
        self.log_emitter("The following applications will be installed:", "info")
        for app_name in sorted(list(self.shopping_cart)):
            self.log_emitter(f"  - {app_name}", "info")
        self.log_emitter("\nDo you wish to continue? (y/n)", "user")
        self.awaiting_confirmation = True

    def handle_install_confirmation(self, response):
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
        download_folder = "installer_downloads"
        os.makedirs(download_folder, exist_ok=True)
        apps_to_install = list(self.shopping_cart)
        for app_name in apps_to_install:
            self.log_emitter(f"\n--- Processing '{app_name}' ---", "command")
            installer_url = self._find_app_url(app_name)
            if not installer_url:
                self.log_emitter(f"Could not find URL for '{app_name}'. Skipping.", "error"); continue
            file_path = self._download_file(installer_url, download_folder, app_name)
            if not file_path:
                self.log_emitter(f"Failed to download '{app_name}'. Skipping to the next app.", "error"); continue
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
        self.progress_emitter.started.emit(app_name)
        local_filepath = None
        try:
            headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
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
                        if current_time - last_update_time > 0.2:
                            elapsed_time = current_time - start_time
                            if total_size > 0 and elapsed_time > 0:
                                speed = downloaded_size / elapsed_time
                                eta = (total_size - downloaded_size) / speed if speed > 0 else 0
                                percentage = (downloaded_size / total_size) * 100
                                progress_data = {'percent': int(percentage), 'downloaded': downloaded_size / (1024 * 1024), 'total': total_size / (1024 * 1024), 'speed': speed / (1024 * 1024), 'eta': eta }
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
                 self.progress_emitter.progress.emit({'percent': 100, 'downloaded': total_size / (1024*1024), 'total': total_size/ (1024*1024), 'speed': 0, 'eta': 0})

    def _run_installer(self, file_path):
        self.log_emitter(f"Running installer: {file_path}", "command")
        self.log_emitter("Please complete the setup process in the window that appears...", "info")
        command_list = []
        if file_path.lower().endswith(".msi"):
            command_list = ["msiexec", "/i", file_path]
        else:
            command_list = [file_path]
        try:
            process = subprocess.run(command_list, check=False)
            return process.returncode == 0
        except Exception as e:
            self.log_emitter(f"Failed to run installer: {e}", "error")
            return False