import os, time, subprocess, ctypes, winsound

# Utilities

SOUNDS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "Sounds")


def play_sound(name):
    """Play a bundled sound from the project's Sounds folder."""
    path = os.path.join(SOUNDS_DIR, name)
    if not os.path.exists(path):
        return
    try:
        winsound.PlaySound(
            path,
            winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT
        )
    except Exception:
        pass


def play_completion():
    play_sound("completion.wav")


def list_components():
    clear_console()
    print("[1;38;2;124;77;255m                  --- FASTFETCH ---                          [0m")
    bar()
    time_start = time.time()

    try:
        result = subprocess.run(
            [
                "fastfetch",
                "--disable",
                "locale,battery,terminalfont,terminal,wmtheme,wm,shell,packages,de"
            ],
            capture_output=True,
            text=True,
            shell=False
        )

        if result.returncode == 0:
            print(result.stdout)
            try:
                subprocess.run("clip", input=result.stdout, text=True, shell=True)
                copied = True
            except Exception:
                copied = False
        else:
            print("[1;31m[error] Fastfetch could not be executed.[0m")
            print("Make sure Fastfetch is installed and available in PATH.")
            if result.stderr:
                print(result.stderr)
            copied = False

    except FileNotFoundError:
        print("[1;31m[error] Fastfetch is not installed or is not in PATH.[0m")
        print("[1;33mInstall it with:[0m")
        print("    winget install fastfetch")
        copied = False

    time_end = time.time()
    bar()
    print(f" [1;93mElapsed time: {time_end - time_start:.4f}[0m")
    if copied:
        print("  [1;92m           Copied Text Output to Clipboard...[0m")
    bar()
    play_completion()
    confirmation()

def shutdown():
    os.system("shutdown /s /f /t 0")

def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


def get_option():
    while True:
        opt = input("    \033[1;38;5;208mOption: \033[0m").strip()
        if opt == "":
            return 0
        try:
            return int(opt)
        except ValueError:
            valid()


def confirmation():
    answer = input("     \033[32mcontinue...\033[0m")


def valid():
    print("  \033[31mSelect a valid option...\033[0m")
    time.sleep(0.5)

def bar():
    print("\033[1m#========================================================#\033[0m")

def introduction():
    print("\n\033[1;38;2;124;77;255m Pinalto's Manager  '\033[0m")
    for i in range(4):
        clear_console();  bar()

        print(f"\033[1m |\033[1;34m --> {version}\033[0m")
        print(f"\033[1m |\033[1;34m Loading Windows Version{'.' * i}\033[0m");       bar()

        time.sleep(0.25)

def update_windows():

    t = time.time();    os.system("cls")
    print("\n\033[1;38;2;124;77;255m                  --- Updating ---                          \033[0m");        bar()
    cmd = (
        'winget upgrade --all --silent --accept-source-agreements --accept-package-agreements && '
        'DISM /Online /Cleanup-Image /StartComponentCleanup /ResetBase && '
        'cleanmgr /sagerun:1'
    )

    try:
        subprocess.run(cmd, shell=True, check=True)
        print("[ok] update + cleanup")
        play_completion()
    except subprocess.CalledProcessError:
        print("[error] update + cleanup")

    bar();  print(f"\033[1;93mElapsed time: {time.time() - t:.4f}\033[0m");     bar()

CREATE_NO_WINDOW = 0x08000000
def _run(cmd):
    subprocess.run(cmd, shell=True, capture_output=True, text=True,
                    creationflags=CREATE_NO_WINDOW)
def restart_explorer():
    _run("taskkill /f /im explorer.exe")
    time.sleep(1.5)
    subprocess.Popen("explorer.exe")
def restart_video_driver():
    user32 = ctypes.windll.user32
    KEYEVENTF_KEYUP = 0x0002
    keys = [0x11, 0x10, 0x5B, 0x42]  # Ctrl, Shift, Win, B
    for k in keys:
        user32.keybd_event(k, 0, 0, 0); time.sleep(0.03)
    time.sleep(0.15)
    for k in reversed(keys):
        user32.keybd_event(k, 0, KEYEVENTF_KEYUP, 0); time.sleep(0.03)
def clear_icon_cache():
    _run("taskkill /f /im explorer.exe")
    time.sleep(1)
    cache = os.path.expandvars(r"%LocalAppData%\Microsoft\Windows\Explorer")
    _run(f'del /a /q "{cache}\\iconcache_*.db"')
    time.sleep(1)
    subprocess.Popen("explorer.exe")
def flush_dns():
    _run("ipconfig /flushdns")
def restart_audio():
    _run("sc stop audiosrv")
    time.sleep(1)
    _run("sc start audiosrv")
def windows_refresh():
    restart_audio(); restart_video_driver(); flush_dns(); clear_icon_cache()
