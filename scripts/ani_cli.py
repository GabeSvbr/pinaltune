import os
import sys
import shutil
import subprocess
import winsound

_BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ANI_CLI_PS1 = os.path.join(_BASE_DIR, "ps1", "ani-cli.ps1")
SOUNDS_DIR = os.path.join(_BASE_DIR, "Sounds")


def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


def bar():
    print("\033[1m#========================================================#\033[0m")


def play_sound(filename):
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
    """
    Abre ani-cli em um processo novo SEM privilégios de admin.
    """
    clear_console()
    bar()
    print("\033[1;38;2;124;77;255m --> ani-cli\033[0m")
    bar()
    
    print(f"DEBUG: _BASE_DIR = {_BASE_DIR}")
    print(f"DEBUG: ANI_CLI_PS1 = {ANI_CLI_PS1}")
    print(f"DEBUG: Arquivo existe? {os.path.exists(ANI_CLI_PS1)}")
    
    if not os.path.exists(ANI_CLI_PS1):
        print(f"\033[31m[error] script not found: {ANI_CLI_PS1}\033[0m")
        confirmation()
        return

    try:
        # Abre em novo processo/console sem herdar admin
        ps_command = f'powershell -NoProfile -ExecutionPolicy Bypass -File "{ANI_CLI_PS1}"'
        print(f"DEBUG: Comando = {ps_command}")
        
        subprocess.Popen(
            ps_command,
            shell=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        
        print("\033[1;92m[ok] ani-cli aberto em janela separada (sem privilégios admin).\033[0m")
        print("DEBUG: Processo iniciado com sucesso")
        play_completion()
        
    except FileNotFoundError as e:
        print(f"\033[31m[error] PowerShell not found: {e}\033[0m")
    except Exception as e:
        print(f"\033[31m[error] failed: {e}\033[0m")
        print(f"DEBUG: Exception type = {type(e)}")
        import traceback
        traceback.print_exc()

    bar()
    confirmation()


def open_ani_cli():
    """Executa ani-cli se já estiver instalado."""
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
