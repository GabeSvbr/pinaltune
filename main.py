import os, time, msvcrt,winsound,subprocess, sys, ctypes

# A pasta 'scripts' fica ao lado deste arquivo (ou dentro do .exe empacotado)
_BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_BASE_DIR, "scripts"))


def ensure_admin():
    """Garante que o programa sempre rode como Administrador.
    Se não estiver elevado, reabre a si mesmo pedindo o UAC e encerra esta instância."""
    try:
        eh_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        eh_admin = False

    if eh_admin:
        return

    params = " ".join(f'"{arg}"' for arg in sys.argv)
    resultado = ctypes.windll.shell32.ShellExecuteW(
        None, "runas", sys.executable, params, None, 1
    )

    if resultado > 32:
        # UAC aceito: a instância elevada já foi aberta, encerra esta aqui
        sys.exit()
    else:
        # Usuário clicou "Não" no UAC (ou falhou por outro motivo)
        print("\033[1;31m[aviso] Elevação para Administrador cancelada/negada.\033[0m")
        print("\033[1;31m         Algumas funções podem falhar sem privilégios de admin.\033[0m")
        time.sleep(1.5)


ensure_admin()

import Utilities_pin,  windows_debloat , setup_menu
from Utilities_pin import bar, clear_console, get_option,confirmation


version = "2.0"

volume = 40  # volume padrão (%)


def resource_path(relative_path):
    """Resolve o caminho tanto rodando o .py quanto o .exe empacotado (PyInstaller)."""
    return os.path.join(_BASE_DIR, relative_path)


def set_system_volume(percent):
    """Ajusta o volume de saída de áudio do Windows (0-100%)."""
    global volume
    percent = max(0, min(100, percent))
    volume = percent
    nivel = int(percent / 100 * 0xFFFF)
    combinado = nivel | (nivel << 16)
    try:
        ctypes.windll.winmm.waveOutSetVolume(0, combinado)
    except Exception as e:
        print(f"\033[1;31m[aviso] não foi possível ajustar o volume: {e}\033[0m")


def ajustar_volume_relativo(delta):
    set_system_volume(volume + delta)


def ajustar_volume():
    clear_console()
    bar()
    print(f"\033[1;38;2;124;77;255m --> Volume atual: {volume}%\033[0m")
    print(" \033[1;34mDigite o novo volume (0-100) ou ENTER para cancelar:\033[0m")
    bar()
    entrada = input("    Volume: ").strip()
    if entrada == "":
        return
    try:
        novo = int(entrada)
    except ValueError:
        print("\033[31mValor inválido.\033[0m")
        time.sleep(0.8)
        return
    if not (0 <= novo <= 100):
        print("\033[31mO volume deve estar entre 0 e 100.\033[0m")
        time.sleep(0.8)
        return
    set_system_volume(novo)
    print(f"\033[1;92mVolume ajustado para {volume}%\033[0m")
    time.sleep(0.6)


# =========================
# FUNÇÕES
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
    caminho = resource_path(path)
    if not os.path.exists(caminho):
        print(f"\033[1;31m[aviso] som não encontrado: {caminho}\033[0m")
        return
    try:
        winsound.PlaySound(
            caminho,
            winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT
        )
    except Exception as e:
        print(f"\033[1;31m[aviso] falha ao tocar som ({caminho}): {e}\033[0m")


def menu(titulo, opcoes):
    selecionada = 1

    while True:
        lista = opcoes() if callable(opcoes) else opcoes

        clear_console()

        print(f"\033[1;38;2;124;77;255m{titulo}\033[0m\n")

        for i, opcao in enumerate(lista, 1):
            if i == selecionada:
                if "Shutdown" in opcao:
                    print(f"        \033[1;38;2;255;0;0m➜ {opcao}\033[0m")
                elif "Sair" in opcao:
                    print(f"        \033[1;38;2;255;0;0m➜ {opcao}\033[0m")
                else:
                    print(f"        \033[1;38;2;124;77;255m➜ {opcao}\033[0m")
            else:
                print(f"    {opcao}")

        tecla = msvcrt.getch()

        if tecla == b'\xe0':
            tecla = msvcrt.getch()

            if tecla == b'H':
                play_sound(r"Sounds/V3_SE_367 (1).wav")
                selecionada -= 1

            elif tecla == b'P':
                play_sound(r"Sounds/V3_SE_367 (1).wav")
                selecionada += 1

            elif tecla == b'K':  # seta esquerda
                if "Volume" in lista[selecionada - 1]:
                    ajustar_volume_relativo(-10)
                    play_sound(r"Sounds/V3_SE_367 (1).wav")

            elif tecla == b'M':  # seta direita
                if "Volume" in lista[selecionada - 1]:
                    ajustar_volume_relativo(10)
                    play_sound(r"Sounds/V3_SE_367 (1).wav")

        elif tecla in b'123456789':
            numero = int(tecla.decode())

            if numero <= len(lista):
                selecionada = numero

        elif tecla == b'\r':
            play_sound(r"Sounds/V3_SE_368 (1).wav")
            return selecionada

        elif tecla in (b'\x1b', b'\x08'):
            play_sound("Sounds/V3_SE_339.wav")
            return None

        selecionada = (selecionada - 1) % len(lista) + 1


# =========================
# MENUS
# =========================

def build_opcoes():
    return [
        "1 >> Update Windows",
        "2 >> Setup Options",
        "3 >> List Machine Components",
        "4 >> Refresh Windows Explorer",
        f"5 >> Volume ({volume}%)",
        "6 >> Shutdown",
        "7 >> Sair"
    ]


opcoes_setup = [
    "1 >> Download Utilitaries",
    "2 >> Download Worktools",
    "3 >> Download Gaming Stuff",
    "4 >> Pinalto's Config",
    "5 >> irm https://christitus.com/win | iex",
    "6 >> & ([scriptblock]::Create((irm https://debloat.raphi.re/)))"
]


def menu_setup():

    while True:

        escolha = menu(
            "----< Setup Menu >----",
            opcoes_setup
        )

        # ESC
        if escolha is None:
            return
        elif escolha == 1:
            setup_menu.download_utilitaries()
        elif escolha == 2:
            setup_menu.download_worktools()
        elif escolha == 3:
            setup_menu.download_gaming()
        elif escolha == 4:
            setup_menu.pinalto_configs()
        elif escolha == 5:
            setup_menu.run_winutil()
        elif escolha == 6:
            setup_menu.raphi_debloat()


        clear_console()
        print(f"Você escolheu: {opcoes_setup[escolha - 1]}")
        confirmation()



def update():
    t = time.time()
    clear_console()
    print("\n\033[1;38;2;124;77;255m                  --- Updating ---                          \033[0m")
    bar()
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
    bar()
    print(f"\033[1;93mElapsed time: {time.time() - t:.4f}\033[0m")
    bar()
    


def get_info():
    clear_console()
    print(subprocess.getoutput("powershell -Command Get-ComputerInfo"))
    confirmation()


def shutdown():
    clear_console()
    print("\033[1;38;2;255;0;0mDesligando o computador...\033[0m")
    os.system("shutdown /s /f /t 0")


def refresh_explorer():
    clear_console()
    print("Reiniciando o Windows Explorer...")
    subprocess.run("taskkill /f /im explorer.exe", shell=True)
    subprocess.Popen("explorer.exe", shell=True)
    print("Feito!")
    confirmation()


# =========================
# MENU PRINCIPAL
# =========================

set_system_volume(volume)  # aplica o volume padrão (70%) ao iniciar
play_sound("Sounds\V3_SE_341.wav")
intro()
play_sound("Sounds\HS_SE_110.wav")

while True:

    escolha = menu(
        "----< Pinalto's Windows Manager >----",
        build_opcoes
    )

    # ESC
    if escolha is None:
        break

    # Sair
    if escolha == 7:
        break

    # Update Windows
    elif escolha == 1:
        Utilities_pin.update_windows()

    # Setup Options
    elif escolha == 2:
        menu_setup()

    # List Machine Components
    elif escolha == 3:
        Utilities_pin.list_components()

    # Refresh Windows Explorer
    elif escolha == 4:
        Utilities_pin.reiniciar_explorer()

    # Volume
    elif escolha == 5:
        ajustar_volume()

    # Shutdown
    elif escolha == 6:
        Utilities_pin.shutdown()

    # Outras opções (Info, etc.)
    else:

        clear_console()

        print(f"Você escolheu: {build_opcoes()[escolha - 1]}")

        confirmation()
