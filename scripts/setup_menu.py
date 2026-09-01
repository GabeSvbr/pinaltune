import windows_debloat
import subprocess
import os
import sys
import winsound
import theme

_BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SOUNDS_DIR = os.path.join(_BASE_DIR, "Sounds")


def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


def bar():
    print("\033[1m#========================================================#\033[0m")


def confirmation():
    input("     \033[32mcontinue...\033[0m")
    play_sound("menu_back.wav")


def play_sound(filename):
    """Play a sound file from the Sounds directory"""
    path = os.path.join(SOUNDS_DIR, filename)
    if not os.path.exists(path):
        return
    try:
        winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
    except Exception:
        pass


def play_completion():
    play_sound("completion.wav")

def install(package_id):
    print(f"{theme.ansi()}>>  Now Installing ➜  \033[1;38;2;255;105;180m({package_id})\033[0m")
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
# DESKTOP SHORTCUT
# =========================

def _project_root():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def _ps_quote(value):
    return "'" + value.replace("'", "''") + "'"


def create_shortcut():
    clear_console()
    bar()
    print(theme.color(" --> Create Desktop Shortcut (Pinaltune v2.2)"))
    bar()
    print()

    root = _project_root()

    target_path = sys.executable
    arguments = ""

    if not getattr(sys, "frozen", False):
        main_py = os.path.join(root, "main.py")
        arguments = f'"{main_py}"'

    icon_path = os.path.join(root, "Sounds", "icon.ico")

    ps_script = f"""
$W = New-Object -ComObject WScript.Shell
$desktop = $W.SpecialFolders("Desktop")
$lnkPath = Join-Path $desktop "Pinaltune.lnk"
$s = $W.CreateShortcut($lnkPath)
$s.TargetPath = {_ps_quote(target_path)}
$s.Arguments = {_ps_quote(arguments)}
$s.WorkingDirectory = {_ps_quote(root)}
"""
    if os.path.isfile(icon_path):
        ps_script += f"$s.IconLocation = {_ps_quote(icon_path)}\n"

    ps_script += """
$s.Description = "Pinaltune"
$s.Save()
Write-Output $lnkPath
"""

    try:
        result = subprocess.run(
            ["powershell", "-NoProfile", "-Command", ps_script],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"
        )

        if result.returncode == 0:
            print("\033[1;92m[ok]\033[0m Shortcut created on the Desktop:")
            print(f"    {result.stdout.strip()}")
            print()
            print("\033[1;92m✓ Shortcut created successfully!\033[0m")
        else:
            print("\033[31m[error] failed to create shortcut:\033[0m")
            print(f"    {result.stderr.strip()}")

    except Exception as e:
        print(f"\033[31m[error] failed to create shortcut: {e}\033[0m")

