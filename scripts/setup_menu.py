from Utilities_pin import bar, clear_console, get_option,confirmation
import windows_debloat
import subprocess
import os
import sys

def install(package_id):
    print(f"\033[1;38;2;124;77;255m>>  Now Installing ➜  \033[1;38;2;255;105;180m({package_id})\033[0m")
    subprocess.run([
        "winget", "install",
        "--accept-source-agreements",
        "--accept-package-agreements",
        "-e", "--id", package_id
    ])

def download_utilitaries():
    install("Python.Python.3.13");  install("ImputNet.Helium");   install("Mozilla.Firefox")
    install("RARLab.WinRAR");install("VideoLAN.VLC");
    install("Klocman.BulkCrapUninstaller");install("AntibodySoftware.WizTree")

def download_gaming():
    install("Valve.Steam");     install("Discord.Discord");     install("PrismLauncher.PrismLauncher")
    install("th-ch.YouTubeMusic")

def download_worktools():
    install("AnyDesk.AnyDesk");     install("Microsoft.VisualStudioCode");          install("OBSProject.OBSStudio")
    install("Rufus.Rufus")
    install("TheDocumentFoundation.LibreOffice")


def windows_download_all():
    download_utilitaries();     download_worktools();       download_gaming()

def pinalto_configs():
    windows_debloat.main_auto_install()    

def run_winutil():
    subprocess.run(["powershell", "-Command", "irm https://christitus.com/win | iex"])

def raphi_debloat():
    subprocess.run(["powershell", "-Command", "& ([scriptblock]::Create((irm https://debloat.raphi.re/)))"])


# =========================
# ATALHO (.bat) NA ÁREA DE TRABALHO
# =========================

def _project_root():
    """Pasta raiz do projeto (uma acima de 'scripts')."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _get_target():
    """Descobre o que o .bat deve executar: o .exe (se compilado com PyInstaller)
    ou o main.py via python, se estiver rodando o código-fonte.
    Usa sempre python.exe (com console) — o programa usa msvcrt/input()
    e precisa de um console de verdade pra funcionar."""
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"', ""
    root = _project_root()
    main_py = os.path.join(root, "main.py")
    return f'"{sys.executable}"', f'"{main_py}"'


def create_shortcut():
    clear_console()
    bar()
    print("\033[1;38;2;124;77;255m --> Criar Atalho na Área de Trabalho\033[0m")
    bar()

    root = _project_root()
    bat_path = os.path.join(root, "Pinalto_WMan.bat")

    exe_cmd, arg = _get_target()
    conteudo_bat = f'@echo off\ncd /d "{root}"\n{exe_cmd} {arg}\n'
    try:
        with open(bat_path, "w", encoding="utf-8") as f:
            f.write(conteudo_bat)
    except Exception as e:
        print(f"\033[31m[erro] não foi possível criar o .bat: {e}\033[0m")
        return

    print(f"\033[1;92m[ok]\033[0m .bat criado em: {bat_path}")

    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    lnk_path = os.path.join(desktop, "Pinalto's WMan.lnk")

    # Ícone do atalho, localizado relativamente à raiz do projeto (sem caminho fixo do PC)
    icon_path = os.path.join(root, "Sounds", "icon.ico")

    icon_line = f'$s.IconLocation = "{icon_path}"; ' if os.path.isfile(icon_path) else ""
    if not icon_line:
        print(f"\033[33m[aviso]\033[0m icon.ico não encontrado em: {icon_path} (atalho será criado sem ícone customizado)")

    ps_script = (
        '$W = New-Object -ComObject WScript.Shell; '
        f'$s = $W.CreateShortcut("{lnk_path}"); '
        f'$s.TargetPath = "{bat_path}"; '
        f'$s.WorkingDirectory = "{root}"; '
        f'{icon_line}'
        '$s.Save()'
    )

    resultado = subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps_script],
        capture_output=True, text=True
    )

    if resultado.returncode == 0:
        print(f"\033[1;92m[ok]\033[0m Atalho criado na Área de Trabalho: {lnk_path}")
    else:
        print(f"\033[31m[erro] falha ao criar atalho:\033[0m {resultado.stderr.strip()}")
