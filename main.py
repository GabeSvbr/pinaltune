import os, time, msvcrt, winsound, subprocess, sys, ctypes, shutil

version = "2.2"

os.system(f"title PinalTune v{version}")

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


def confirmation():
    answer = input("     \033[32mcontinue...\033[0m")
    play_sound("Sounds/menu_back.wav")
    

ensure_admin()

import windows_debloat, setup_menu, youtube_downloader, pinterest_downloader, ani_cli
import theme


def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


volume = 30 # default volume (%)


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
    print(f"{theme.ansi()} --> Current volume: {volume}%\033[0m")
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
    print(theme.color("-" * 120))


def intro():
    print("\n" + theme.color(" Pinalto's Manager  '"))
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

        print(theme.color(title) + "\n")

        for i, option in enumerate(items, 1):
            if i == selected:
                if "Shutdown /s /f /t 0" in option:
                    print(f"        \033[1;38;2;255;0;0m➜ {option}\033[0m")
                elif "Exit" in option:
                    print(f"        \033[1;38;2;255;0;0m➜ {option}\033[0m")
                elif "Volume" in option or "Info" in option or "Dev Menu" in option:
                    print(f"        \033[1;34m➜ {option}\033[0m")
                else:
                    print(f"        {theme.ansi()}➜ {option}\033[0m")
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
                else:
                    play_sound(r"Sounds/menu_back.wav")
                    return None

            elif key == b'M':  # right arrow
                if "Volume" in items[selected - 1]:
                    adjust_volume_relative(10)
                    play_sound(r"Sounds/menu_down_up.wav")
                else:
                    play_sound(r"Sounds/select.wav")
                    return selected

        elif key in b'123456789':
            number = int(key.decode())

            if number <= len(items):
                selected = number

        elif key == b'0' and len(items) >= 10:
            selected = 10

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
        "4 >> List Machine Components",
        "5 >> Refresh Windows Explorer",
        f"6 >> Volume ({volume}%)",
        "7 >> Info",
        "8 >> Dev Menu",
        "9 >> Shutdown /s /f /t 0",
        "10 >> Exit"
    ]


setup_options = [
    "1 >> Download Utilitaries",
    "2 >> Download Worktools",
    "3 >> Download Gaming Stuff",
    "4 >> Pinalto's Config",
    "5 >> irm https://christitus.com/win | iex",
    "6 >> & ([scriptblock]::Create((irm https://debloat.raphi.re/)))",
    "7 >> Create Desktop Shortcut",
    "8 >> Install/Manage ani-cli"
]

dev_options = [
    "1 >> Test Sounds",
    "2 >> Change Menu Color"
]

media_options = [
    "1 >> ani-cli",
    "2 >> Download YouTube Video",
    "3 >> Download Pinterest Image (High Res)"
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


def silent_menu(title, options, navigation_sounds=False):
    """Menu with optional navigation sounds."""
    selected = 1

    while True:
        items = options() if callable(options) else options

        clear_console()

        print(theme.color(title) + "\n")

        for i, option in enumerate(items, 1):
            if i == selected:
                print(f"        {theme.ansi()}➜ {option}\033[0m")
            else:
                print(f"    {option}")

        key = msvcrt.getch()

        if key == b'\xe0':
            key = msvcrt.getch()
            if key == b'H':
                selected -= 1
                if navigation_sounds:
                    play_sound(r"Sounds/menu_down_up.wav")
            elif key == b'P':
                selected += 1
                if navigation_sounds:
                    play_sound(r"Sounds/menu_down_up.wav")
            elif key == b'K':
                if navigation_sounds:
                    play_sound(r"Sounds/menu_back.wav")
                return None
            elif key == b'M':
                if navigation_sounds:
                    play_sound(r"Sounds/select.wav")
                return selected

        elif key in b'123456789':
            number = int(key.decode())
            if number <= len(items):
                selected = number
                if navigation_sounds:
                    play_sound(r"Sounds/menu_down_up.wav")

        elif key == b'0' and len(items) >= 10:
            selected = 10
            if navigation_sounds:
                play_sound(r"Sounds/menu_down_up.wav")

        elif key == b'\r':
            if navigation_sounds:
                play_sound(r"Sounds/select.wav")
            return selected

        elif key in (b'\x1b', b'\x08'):
            if navigation_sounds:
                play_sound(r"Sounds/menu_back.wav")
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
            setup_menu.play_completion()
        elif choice == 8:
            ani_cli.run_ani_cli()
            continue


def dev_menu_loop():
    while True:
        choice = menu(
            "----< Dev Menu >----",
            dev_options
        )

        if choice is None:
            return
        elif choice == 1:
            test_sounds_menu()
        elif choice == 2:
            change_theme_menu()


def change_theme_menu():
    while True:
        options = [f"{i} >> {name}" for i, (name, _) in enumerate(theme.THEMES, 1)]
        choice = silent_menu("----< Menu Color >----", options, navigation_sounds=True)
        if choice is None:
            return
        theme.set_theme_index(choice - 1)
        clear_console()
        print(theme.color("----< Menu Color >----"))
        print()
        print(theme.color(f">> Color changed to: {theme.THEMES[choice - 1][0]}"))
        print()
        print("     \033[32mcontinue...\033[0m")
        msvcrt.getch()
        return


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
            ani_cli.open_ani_cli()
        elif choice == 2:
            youtube_downloader.youtube_download()
        elif choice == 3:
            pinterest_downloader.pinterest_download()

def update():
    t = time.time()
    clear_console()

    print(theme.color("\n                  --- Updating ---                          "))
    bar()

    blacklist = [
        "Microsoft.Edge",
        "Microsoft.EdgeWebView2Runtime",
        "Microsoft.OneDrive",
        "Microsoft.Teams",
        "Microsoft.BingSearch",
        "Microsoft.549981C3F5F10",
        "Microsoft.GetHelp",
        "Microsoft.Getstarted",
    ]

    try:
        result = subprocess.run(
            ["winget", "upgrade", "--all",
             "--accept-source-agreements",
             "--accept-package-agreements"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="ignore"
        )

        output = result.stdout + result.stderr

        if result.returncode == 0:
            print("\n\033[1;92m[ok] Update done.\033[0m")
        else:
            print("\n\033[1;91m[error] Some updates failed.\033[0m")

        if output.strip():
            print(output)

    except FileNotFoundError:
        print("\033[1;91m[error] winget not found.\033[0m")

    except Exception as e:
        print(f"\033[1;91m[error] update: {e}\033[0m")

    bar()
    print(f"\033[1;93mElapsed time: {time.time() - t:.4f}\033[0m")
    bar()
    confirmation()


def get_info():
    clear_console()
    print("Loading...")
    time.sleep(0.8)
    play_sound("Sounds\\completion.wav")
    clear_console()

    print(theme.color(" --- FASTFETCH --- "))
    bar()

    # Checks if fastfetch is available in PATH
    if shutil.which("fastfetch") is None:
        print("\033[1;33m[info] Fastfetch not found. Installing automatically...\033[0m")
        try:
            install = subprocess.run(
                ["winget", "install", "-e", "--id", "Fastfetch-cli.Fastfetch",
                 "--silent", "--accept-source-agreements", "--accept-package-agreements"],
                capture_output=True,
                text=True,
                shell=False
            )
            if install.returncode == 0:
                print("\033[1;92m[ok] Fastfetch installed successfully.\033[0m")
            else:
                print("\033[1;31m[error] Failed to install Fastfetch automatically.\033[0m")
                if install.stderr:
                    print(install.stderr)
                bar()
                confirmation()
                return
        except FileNotFoundError:
            print("\033[1;31m[error] Winget is not available on this system.\033[0m")
            print("Install winget or Fastfetch manually to continue.")
            bar()
            confirmation()
            return

        # Reloads PATH inside this same process/session so the newly
        # installed binary can be found without restarting the app
        os.environ["PATH"] = (
            subprocess.run(
                ["powershell", "-NoProfile", "-Command",
                 "[System.Environment]::GetEnvironmentVariable('Path','Machine') + ';' + "
                 "[System.Environment]::GetEnvironmentVariable('Path','User')"],
                capture_output=True, text=True
            ).stdout.strip()
        )

        if shutil.which("fastfetch") is None:
            print("\033[1;31m[warning] Fastfetch was installed but isn't visible in PATH yet.\033[0m")
            print("You may need to restart Pinaltune for it to be detected.")
            bar()
            confirmation()
            return

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
            print("\033[1;31m[error] Fastfetch could not be executed.\033[0m")
            if result.stderr:
                print(result.stderr)
    except FileNotFoundError:
        print("\033[1;31m[error] Fastfetch is not installed or is not in PATH.\033[0m")

    bar()
    confirmation()

def info():
    clear_console()
    print(theme.color("────────────────────────────────────────────────────────────────────────"))
    print(theme.color("                          PINALTUNE 2.2"))
    print("\033[1;34m                       System Management Utility\033[0m")
    print(theme.color("────────────────────────────────────────────────────────────────────────"))
    print()
    print(" >>  Version: 2.2")
    print(" >>  Platform: Windows")
    print(" >>  Creator: pinalto")
    print(" >>  Repo: https://github.com/GabeSvbr/pinaltune")
    print(" >>  Languages: Python, PowerShell")
    print()
    print(theme.color("────────────────────────────────────────────────────────────────────────"))
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
        update()

    # Setup Options
    elif choice == 2:
        setup_menu_loop()

    # Media
    elif choice == 3:
        media_menu_loop()

    # List Machine Components
    elif choice == 4:
        get_info()

    # Refresh Windows Explorer
    elif choice == 5:
        refresh_explorer()

    # Volume
    elif choice == 6:
        adjust_volume()

    # Info
    elif choice == 7:
        info()

    # Dev Menu
    elif choice == 8:
        dev_menu_loop()

    # Shutdown
    elif choice == 9:
        shutdown()


