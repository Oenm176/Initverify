# run.py
# This is the launcher script and the primary entry point for the user.
# Its sole purpose is to ensure the application is run with Administrator
# privileges, which are required for installing software.
# It also handles the application restart logic.

import sys
import ctypes
import subprocess
import os

# Get the absolute directory where this launcher script is located.
script_dir = os.path.dirname(os.path.realpath(__file__))


def is_admin():
    """Checks if the script is currently running with Administrator privileges."""
    try:
        # Call the Windows API to check for admin status.
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


if __name__ == "__main__":
    # This block runs only when the script is executed directly.

    if is_admin():
        # This block runs if the script ALREADY has admin rights.
        
        # Set initial exit_code to our special restart code (5)
        # to ensure the loop runs at least once.
        exit_code = 5
        
        # Keep relaunching the app as long as it exits with the restart code.
        while exit_code == 5:
            print("Administrator privileges granted. Starting the main application...")

            # 1. Define the absolute path to the python.exe inside the virtual environment.
            python_executable_in_venv = os.path.join(script_dir, "venv", "Scripts", "python.exe")

            # 2. Define the absolute path to the main application script.
            main_script_path = os.path.join(script_dir, "main.py")

            # 3. Launch the main application and wait for it to close,
            #    then capture its exit code.
            process = subprocess.Popen([python_executable_in_venv, main_script_path])
            exit_code = process.wait()
            
            if exit_code == 5:
                print("Restart signal received. Relaunching application...")

        # If the loop finishes (exit code is not 5), exit the launcher.
        sys.exit(exit_code)

    else:
        # This block runs if the script DOES NOT have admin rights.
        # Re-launch this same script (run.py) with an elevation request,
        # which will trigger the Windows UAC (User Account Control) prompt.
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)