import os,time,subprocess, ctypes

# Utilities

def list_components():
    clear_console();    print("\n\033[1;38;2;124;77;255m                  --- COMPONENTS ---                          \033[0m");        bar()
    time_start = time.time()

    result = subprocess.run(
        "systeminfo",
        capture_output=True,
        text=True,
        shell=True
    )
    text = result.stdout
    print(text)
    subprocess.run("clip", input=result.stdout, text=True, shell=True)
    time_end = time.time()
    bar();  print(f" \033[1;93mElapsed time: {time_end - time_start:.4f}\033[0m\n  \033[1;92m           Copied Text Output to Clipboard...\033[0m");   bar();confirmation()


def shutdown():
    os.system("shutdown /s /f /t 0")

def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


def get_option():
    while True:
        opc = input("    \033[1;38;5;208mOption: \033[0m").strip()
        if opc == "":
            return 0
        try:
            return int(opc)
        except ValueError:
            valid()


def confirmation():
    resposta = input("     \033[32mcontinue...\033[0m")


def valid():
    print("  \033[31mSelect Valid Option...\033[0m")
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
    except subprocess.CalledProcessError:
        print("[erro] update + cleanup")

    bar();  print(f"\033[1;93mElapsed time: {time.time() - t:.4f}\033[0m");     bar()

CREATE_NO_WINDOW = 0x08000000
def _rodar(cmd):
    subprocess.run(cmd, shell=True, capture_output=True, text=True,
                    creationflags=CREATE_NO_WINDOW)
def reiniciar_explorer():
    _rodar("taskkill /f /im explorer.exe")
    time.sleep(1.5)
    subprocess.Popen("explorer.exe")
def reiniciar_driver_video():
    user32 = ctypes.windll.user32
    KEYEVENTF_KEYUP = 0x0002
    teclas = [0x11, 0x10, 0x5B, 0x42]  # Ctrl, Shift, Win, B
    for t in teclas:
        user32.keybd_event(t, 0, 0, 0); time.sleep(0.03)
    time.sleep(0.15)
    for t in reversed(teclas):
        user32.keybd_event(t, 0, KEYEVENTF_KEYUP, 0); time.sleep(0.03)
def limpar_cache_icones():
    _rodar("taskkill /f /im explorer.exe")
    time.sleep(1)
    cache = os.path.expandvars(r"%LocalAppData%\Microsoft\Windows\Explorer")
    _rodar(f'del /a /q "{cache}\\iconcache_*.db"')
    time.sleep(1)
    subprocess.Popen("explorer.exe")
def flush_dns():
    _rodar("ipconfig /flushdns")
def reiniciar_audio():
    _rodar("sc stop audiosrv")
    time.sleep(1)
    _rodar("sc start audiosrv")
def windows_refresh():
    reiniciar_audio(); reiniciar_driver_video(); flush_dns(); limpar_cache_icones()