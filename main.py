import os, time, msvcrt, winsound, subprocess, sys, ctypes

# The 'scripts' folder sits next to this file (or inside the packaged .exe)
_BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_BASE_DIR, "scripts"))


def ensure_admin():
    """Makes sure the program always runs as Administrator.
    If it isn't elevated, it relaunches itself asking for UAC and closes this instance."""
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        is_admin = False

    if is_admin:
        return

    params = " ".join(f'"{arg}"' for arg in sys.argv)
    result = ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, params, None, 1
    )

    if result > 32:
        # UAC accepted: the elevated instance was already opened, close this one
        sys.exit()
    else:
        # User clicked "No" on UAC (or it failed for another reason)
        print("\033[1;31m[warning] Elevation to Administrator canceled/denied.\033[0m")
        print("\033[1;31m         Some functions may fail without admin privileges.\033[0m")
        time.sleep(1.5)


ensure_admin()

import Utilities_pin, windows_debloat, setup_menu, youtube_downloader, pinterest_downloader
from Utilities_pin import bar, clear_console, get_option, confirmation


version = "2.0"

volume = 40  # default volume (%)


def resource_path(relative_path):
    """Resolve the path whether running the .py or the packaged .exe (PyInstaller)."""
    return os.path.join(_BASE_DIR, relative_path)


def set_system_volume(percent):
    """Adjusts Windows audio output volume (0-100%)."""
    global volume
    percent = max(0, min(100, percent))
    volume = percent
    level = int(percent / 100 * 0xFFFF)
    combined = level | (level << 16)
    try:
        ctypes.windll.winmm.waveOutSetVolume(0, combined)
    except Exception as e:
        print(f"\033[1;31m[warning] could not adjust volume: {e}\033[0m")


def adjust_volume_relative(delta):
    set_system_volume(volume + delta)


def adjust_volume():
    clear_console()
    bar()
    print(f"\033[1;38;2;124;77;255m --> Current volume: {volume}%\033[0m")
    print(" \033[1;34mEnter the new volume (0-100) or ENTER to cancel:\033[0m")
    bar()
    entry = input("    Volume: ").strip()
    if entry == "":
        return
    try:
        new_volume = int(entry)
    except ValueError:
        print("\033[31mInvalid value.\033[0m")
        time.sleep(0.8)
        return
    if not (0 <= new_volume <= 100):
        print("\033[31mVolume must be between 0 and 100.\033[0m")
        time.sleep(0.8)
        return
    set_system_volume(new_volume)
    print(f"\033[1;92mVolume set to {volume}%\033[0m")
    time.sleep(0.6)


# =========================
# FUNCTIONS
# =========================



def bar():
    print("\033[1;38;2;124;77;255m" + "-" * 60 + "\033[0m")


def intro():
    print("\n\033[1;38;2;124;77;255m Pinalto's Manager  '\033[0m")
    for i in range(4):
        clear_console()
        bar()
        print(f"\033[1m |\033[1;34m --> Version {version}\033[0m")
        print(f"\033[1m |\033[1;34m --> Loading Windows Version{'.' * i}\033[0m")
        bar()
        if i > 0:
            play_sound("Sounds/Sounds_dots.wav")
        time.sleep(0.25)


def play_sound(path):
    path_full = resource_path(path)
    if not os.path.exists(path_full):
        print(f"\033[1;31m[warning] sound not found: {path_full}\033[0m")
        return
    try:
        winsound.PlaySound(
            path_full,
            winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT
        )
    except Exception as e:
        print(f"\033[1;31m[warning] failed to play sound ({path_full}): {e}\033[0m")


def menu(title, options):
    selected = 1

    while True:
        items = options() if callable(options) else options

        clear_console()

        print(f"\033[1;38;2;124;77;255m{title}\033[0m\n")

        for i, option in enumerate(items, 1):
            if i == selected:
                if "Shutdown" in option:
                    print(f"        \033[1;38;2;255;0;0m➜ {option}\033[0m")
                elif "Exit" in option:
                    print(f"        \033[1;38;2;255;0;0m➜ {option}\033[0m")
                else:
                    print(f"        \033[1;38;2;124;77;255m➜ {option}\033[0m")
            else:
                print(f"    {option}")

        key = msvcrt.getch()

        if key == b'\xe0':
            key = msvcrt.getch()

            if key == b'H':
                play_sound(r"Sounds/menu_down_up.wav")
                selected -= 1

            elif key == b'P':
                play_sound(r"Sounds/menu_down_up.wav")
                selected += 1

            elif key == b'K':  # left arrow
                if "Volume" in items[selected - 1]:
                    adjust_volume_relative(-10)
                    play_sound(r"Sounds/menu_down_up.wav")

            elif key == b'M':  # right arrow
                if "Volume" in items[selected - 1]:
                    adjust_volume_relative(10)
                    play_sound(r"Sounds/menu_down_up.wav")

        elif key in b'123456789':
            number = int(key.decode())

            if number <= len(items):
                selected = number

        elif key == b'\r':
            play_sound(r"Sounds/select.wav")
            return selected

        elif key in (b'\x1b', b'\x08'):
            play_sound("Sounds/menu_back.wav")
            return None

        selected = (selected - 1) % len(items) + 1


# =========================
# MENUS
# =========================

def build_options():
    return [
        "1 >> Update Windows",
        "2 >> Setup Options",
        "3 >> Media",
        "4 >> Test Sounds",
        "5 >> List Machine Components",
        "6 >> Refresh Windows Explorer",
        f"7 >> Volume ({volume}%)",
        "8 >> Shutdown",
        "9 >> Exit"
    ]


setup_options = [
    "1 >> Download Utilitaries",
    "2 >> Download Worktools",
    "3 >> Download Gaming Stuff",
    "4 >> Pinalto's Config",
    "5 >> irm https://christitus.com/win | iex",
    "6 >> & ([scriptblock]::Create((irm https://debloat.raphi.re/)))",
    "7 >> Create Desktop Shortcut"
]

media_options = [
    "1 >> Download YouTube Video",
    "2 >> Download Pinterest Image (High Res)"
]

sound_files = [
    "menu_in.wav",
    "Sounds_dots.wav",
    "v_cut.wav",
    "menu_back.wav",
    "intro_load.wav",
    "menu_down_up.wav",
    "select.wav",
    "completion.wav",
]


def silent_menu(title, options):
    """Same navigation as menu(), but stays silent while moving the selection.
    Enter returns the selected index (menu stays open); Esc/Backspace returns None."""
    selected = 1

    while True:
        items = options() if callable(options) else options

        clear_console()

        print(f"\033[1;38;2;124;77;255m{title}\033[0m\n")

        for i, option in enumerate(items, 1):
            if i == selected:
                print(f"        \033[1;38;2;124;77;255m➜ {option}\033[0m")
            else:
                print(f"    {option}")

        key = msvcrt.getch()

        if key == b'\xe0':
            key = msvcrt.getch()
            if key == b'H':
                selected -= 1
            elif key == b'P':
                selected += 1

        elif key in b'123456789':
            number = int(key.decode())
            if number <= len(items):
                selected = number

        elif key == b'\r':
            return selected

        elif key in (b'\x1b', b'\x08'):
            return None

        selected = (selected - 1) % len(items) + 1


def setup_menu_loop():

    while True:

        choice = menu(
            "----< Setup Menu >----",
            setup_options
        )

        # ESC
        if choice is None:
            return
        elif choice == 1:
            setup_menu.download_utilitaries()
        elif choice == 2:
            setup_menu.download_worktools()
        elif choice == 3:
            setup_menu.download_gaming()
        elif choice == 4:
            setup_menu.pinalto_configs()
        elif choice == 5:
            setup_menu.run_winutil()
        elif choice == 6:
            setup_menu.raphi_debloat()
        elif choice == 7:
            setup_menu.create_shortcut()


        clear_console()
        print(f"You chose: {setup_options[choice - 1]}")
        confirmation()


def test_sounds_menu():
    options = [f"{i} >> {name}" for i, name in enumerate(sound_files, 1)]

    while True:
        choice = silent_menu(
            "----< Test Sounds (Enter plays, Esc exits) >----",
            options
        )

        # ESC
        if choice is None:
            return

        play_sound(f"Sounds/{sound_files[choice - 1]}")


def media_menu_loop():

    while True:

        choice = menu(
            "----< Media Menu >----",
            media_options
        )

        # ESC
        if choice is None:
            return
        elif choice == 1:
            youtube_downloader.youtube_download()
        elif choice == 2:
            pinterest_downloader.pinterest_download()


def update():
    t = time.time()
    clear_console()
    print("\n\033[1;38;2;124;77;255m                  --- Updating ---                          \033[0m")
    bar()
    cmd = (
        'winget upgrade --all --silent --accept-source-agreements --accept-package-agreements && '
    )
    try:
        subprocess.run(cmd, shell=True, check=True)
        print("[ok] update + cleanup")
    except subprocess.CalledProcessError:
        print("[error] update + cleanup")
    bar()
    print(f"\033[1;93mElapsed time: {time.time() - t:.4f}\033[0m")
    bar()
    

def get_info():

    clear_console()
    print("Loading...")
    time.sleep(0.8)


    play_sound("Sounds\completion.wav")
    clear_console()
    print("[1;38;2;124;77;255m                  --- FASTFETCH ---                          [0m")
    bar()

    try:
        result = subprocess.run(
            [
                "fastfetch",
                "--structure-disabled",
                "locale:battery:terminalfont:terminal:wmtheme:wm:shell:packages:de:colors"
            ],
            capture_output=True,
            text=True,
            shell=False
        )

        if result.returncode == 0:
            print(result.stdout)
        else:
            print("[1;31m[error] Fastfetch could not be executed.[0m")
            print("Make sure Fastfetch is installed and available in PATH.")
            if result.stderr:
                print(result.stderr)
    except FileNotFoundError:
        print("[1;31m[error] Fastfetch is not installed or is not in PATH.[0m")
        print("[1;33mInstall it with:[0m")
        print("    winget install fastfetch")

    bar()
    confirmation()

def shutdown():
    clear_console()
    print("\033[1;38;2;255;0;0mShutting down the computer...\033[0m")
    os.system("shutdown /s /f /t 0")


def refresh_explorer():
    clear_console()
    print("Restarting Windows Explorer...")
    subprocess.run("taskkill /f /im explorer.exe", shell=True)
    subprocess.Popen("explorer.exe", shell=True)
    print("Done!")
    confirmation()


# =========================
# MAIN MENU
# =========================

set_system_volume(volume)  # applies the default volume on startup
play_sound("Sounds\\intro_load.wav")
intro()
play_sound("Sounds\\menu_in.wav")

while True:

    choice = menu(
        "----< Pinalto's Windows Manager >----",
        build_options
    )

    # ESC
    if choice is None:
        break

    # Exit
    if choice == 9:
        break

    # Update Windows
    elif choice == 1:
        Utilities_pin.update_windows()

    # Setup Options
    elif choice == 2:
        setup_menu_loop()

    # Media
    elif choice == 3:
        media_menu_loop()

    # Test Sounds
    elif choice == 4:
        test_sounds_menu()

    # List Machine Components
    elif choice == 5:
        get_info()

    # Refresh Windows Explorer
    elif choice == 6:
        Utilities_pin.restart_explorer()

    # Volume
    elif choice == 7:
        adjust_volume()

    # Shutdown
    elif choice == 8:
        Utilities_pin.shutdown()

    # Other options (Info, etc.)
    else:

        clear_console()

        print(f"You chose: {build_options()[choice - 1]}")

        confirmation()
