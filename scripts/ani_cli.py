import os
import sys
import shutil
import subprocess
import winsound

# The 'ps1' folder sits next to main.py (one level above 'scripts'),
# or inside the packaged .exe when frozen with PyInstaller.
_BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ANI_CLI_PS1 = os.path.join(_BASE_DIR, "ps1", "ani-cli.ps1")
SOUNDS_DIR = os.path.join(_BASE_DIR, "Sounds")


def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


def bar():
    print("\033[1m#========================================================#\033[0m")


def play_sound(filename):
    """Play a sound file from the Sounds directory"""
    path = os.path.join(SOUNDS_DIR, filename)
    if not os.path.exists(path):
        return
    try:
        winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
    except Exception:
        pass


def confirmation():
    input("     \033[32mcontinue...\033[0m")
    play_sound("menu_back.wav")


def play_completion():
    path = os.path.join(SOUNDS_DIR, "completion.wav")
    if not os.path.exists(path):
        return
    try:
        winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
    except Exception:
        pass


def run_ani_cli():
    """Launches the ani-cli.ps1 installer/manager in an interactive PowerShell session."""
    clear_console()
    bar()
    print("\033[1;38;2;124;77;255m --> ani-cli\033[0m")
    bar()

    if not os.path.exists(ANI_CLI_PS1):
        print(f"\033[31m[error] script not found: {ANI_CLI_PS1}\033[0m")
        confirmation()
        return

    try:
        subprocess.run(
            [
                "powershell",
                "-NoProfile",
                "-ExecutionPolicy", "Bypass",
                "-File", ANI_CLI_PS1,
            ],
            check=False,
        )
        play_completion()
    except FileNotFoundError:
        print("\033[31m[error] PowerShell not found on this system.\033[0m")
    except Exception as e:
        print(f"\033[31m[error] failed to run ani-cli.ps1: {e}\033[0m")

    bar()
    confirmation()


def open_ani_cli():
    """Clears the console and runs the 'ani-cli' command directly, as if the
    user had typed it themselves. If the command isn't installed, tells the
    user to install it from the Setup menu instead."""
    clear_console()

    if shutil.which("ani-cli") is None:
        bar()
        print("\033[31m[error] ani-cli is not installed.\033[0m")
        print("\033[1;33mGo to Setup Options >> Install/Manage ani-cli to install it.\033[0m")
        bar()
        confirmation()
        return

    try:
        subprocess.run("ani-cli", shell=True)
    except Exception as e:
        print(f"\033[31m[error] failed to run ani-cli: {e}\033[0m")
        confirmation()
