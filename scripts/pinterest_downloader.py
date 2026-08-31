import os
import subprocess
import sys
import importlib
import msvcrt
import winsound

_BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SOUNDS_DIR = os.path.join(_BASE_DIR, "Sounds")
DOWNLOADS_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "output")


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


def arrow_menu(title, options):
    """Simple arrow-key menu: Up/Down arrows move the selection, Enter confirms,
    Esc/Backspace cancels (returns None)."""
    selected = 1

    while True:
        clear_console()
        bar()
        print(f"\033[1;38;2;124;77;255m{title}\033[0m")
        bar()

        for i, option in enumerate(options, 1):
            if i == selected:
                print(f"        \033[1;38;2;124;77;255m➜ {option}\033[0m")
            else:
                print(f"    {option}")

        key = msvcrt.getch()

        if key == b'\xe0':
            key = msvcrt.getch()
            if key == b'H':  # up arrow
                selected -= 1
            elif key == b'P':  # down arrow
                selected += 1

        elif key in b'123456789':
            number = int(key.decode())
            if number <= len(options):
                selected = number

        elif key == b'\r':
            return selected

        elif key in (b'\x1b', b'\x08'):
            return None

        selected = (selected - 1) % len(options) + 1


def _ensure_gallery_dl():
    """Makes sure the 'gallery-dl' package is installed (pip)."""
    try:
        importlib.import_module("gallery_dl")
        return True
    except ImportError:
        print("\033[1;38;2;124;77;255m>>  gallery-dl not found, installing...\033[0m")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-U", "gallery-dl"],
                check=True
            )
            importlib.invalidate_caches()
            importlib.import_module("gallery_dl")
            return True
        except Exception as e:
            print(f"\033[31m[error] could not install gallery-dl: {e}\033[0m")
            confirmation()
            return False


def _download(url):
    os.makedirs(DOWNLOADS_DIR, exist_ok=True)

    cmd = [
        sys.executable, "-m", "gallery_dl",
        "--dest", DOWNLOADS_DIR,
        url
    ]

    try:
        subprocess.run(cmd, check=True)
        print(f"\033[1;92m[ok] Saved to: {DOWNLOADS_DIR}\033[0m")
        play_completion()
    except subprocess.CalledProcessError as e:
        print(f"\n\033[31m[error] failed to download: {e}\033[0m")
    except Exception as e:
        print(f"\n\033[31m[error] unexpected failure: {e}\033[0m")


def pinterest_download():
    clear_console()
    bar()
    print("\033[1;38;2;124;77;255m --> Download Pinterest Image (High Resolution)\033[0m")
    bar()

    if not _ensure_gallery_dl():
        return

    url = input("    Paste the Pin or Board URL (or ENTER to cancel): ").strip()
    if url == "":
        return

    clear_console()
    bar()
    print(f"\033[1;38;2;124;77;255m>>  Downloading from: \033[1;38;2;255;105;180m{url}\033[0m")
    print(" \033[1;34m(a single Pin URL downloads one image; a Board URL downloads all pins)\033[0m")
    bar()

    _download(url)

    bar()
    confirmation()
