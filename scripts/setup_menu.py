from Utilities_pin import bar, clear_console, get_option, confirmation, play_completion
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
    play_completion()

def download_gaming():
    install("Valve.Steam");     install("Discord.Discord");     install("PrismLauncher.PrismLauncher")
    install("th-ch.YouTubeMusic")
    play_completion()

def download_worktools():
    install("AnyDesk.AnyDesk");     install("Microsoft.VisualStudioCode");          install("OBSProject.OBSStudio")
    install("Rufus.Rufus")
    install("TheDocumentFoundation.LibreOffice")
    play_completion()


def windows_download_all():
    download_utilitaries();     download_worktools();       download_gaming()

def pinalto_configs():
    windows_debloat.main_auto_install()    

def run_winutil():
    subprocess.run(["powershell", "-Command", "irm https://christitus.com/win | iex"])

def raphi_debloat():
    subprocess.run(["powershell", "-Command", "& ([scriptblock]::Create((irm https://debloat.raphi.re/)))"])


# =========================
# DESKTOP SHORTCUT (.bat)
# =========================

def _project_root():
    """Project root folder (one level above 'scripts')."""
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _get_target():
    """Figures out what the .bat should run: the .exe (if built with PyInstaller)
    or main.py via python, if running from source.
    Always uses python.exe (with a console) — the program uses msvcrt/input()
    and needs a real console to work."""
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"', ""
    root = _project_root()
    main_py = os.path.join(root, "main.py")
    return f'"{sys.executable}"', f'"{main_py}"'


def create_shortcut():
    clear_console()
    bar()
    print("\033[1;38;2;124;77;255m --> Create Desktop Shortcut\033[0m")
    bar()

    root = _project_root()
    bat_path = os.path.join(root, "Pinalto_WMan.bat")

    exe_cmd, arg = _get_target()
    bat_content = f'@echo off\ncd /d "{root}"\n{exe_cmd} {arg}\n'
    try:
        with open(bat_path, "w", encoding="utf-8") as f:
            f.write(bat_content)
    except Exception as e:
        print(f"\033[31m[error] could not create the .bat file: {e}\033[0m")
        return

    print(f"\033[1;92m[ok]\033[0m .bat created at: {bat_path}")

    desktop = os.path.join(os.path.expanduser("~"), "Desktop")
    lnk_path = os.path.join(desktop, "Pinalto's WMan.lnk")

    # Shortcut icon, located relative to the project root (no hardcoded PC path)
    icon_path = os.path.join(root, "Sounds", "icon.ico")

    icon_line = f'$s.IconLocation = "{icon_path}"; ' if os.path.isfile(icon_path) else ""
    if not icon_line:
        print(f"\033[33m[warning]\033[0m icon.ico not found at: {icon_path} (shortcut will be created without a custom icon)")

    ps_script = (
        '$W = New-Object -ComObject WScript.Shell; '
        f'$s = $W.CreateShortcut("{lnk_path}"); '
        f'$s.TargetPath = "{bat_path}"; '
        f'$s.WorkingDirectory = "{root}"; '
        f'{icon_line}'
        '$s.Save()'
    )

    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps_script],
        capture_output=True, text=True
    )

    if result.returncode == 0:
        print(f"\033[1;92m[ok]\033[0m Shortcut created on the Desktop: {lnk_path}")
    else:
        print(f"\033[31m[error] failed to create shortcut:\033[0m {result.stderr.strip()}")
