from Utilities_pin import bar, clear_console, get_option,confirmation
import windows_debloat
import subprocess

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
