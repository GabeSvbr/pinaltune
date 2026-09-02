"""
Standalone script to create a desktop shortcut for Pinaltune
WITHOUT running the main application
"""

import os
import sys
import subprocess
import ctypes

version = "2.3"

# The 'scripts' folder sits next to this file
_BASE_DIR = os.path.dirname(os.path.abspath(__file__))


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
        sys.exit()
    else:
        print("\033[1;31m[warning] Elevation to Administrator canceled/denied.\033[0m")
        sys.exit(1)


def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


def bar():
    print("\033[1;38;2;124;77;255m" + "-" * 120 + "\033[0m")


def _project_root():
    """Project root folder."""
    return _BASE_DIR


def _get_target():
    """Figures out the program target for the desktop shortcut."""
    if getattr(sys, "frozen", False):
        return f'"{sys.executable}"', ""
    root = _project_root()
    main_py = os.path.join(root, "main.py")
    return f'"{sys.executable}"', f'"{main_py}"'


def create_shortcut():
    """Create desktop shortcut for Pinaltune"""
    clear_console()
    bar()
    print(f"\033[1;38;2;124;77;255m --> Create Desktop Shortcut (Pinaltune v{version})\033[0m")
    bar()
    print()

    root = _project_root()

    exe_cmd, arg = _get_target()

    exe_cmd = exe_cmd.strip().strip('"')
    arg = arg.strip()

    if arg.startswith('"') and arg.endswith('"'):
        arg = arg[1:-1]

    target_path = exe_cmd

    icon_path = os.path.join(root, "Sounds", "icon.ico")

    if os.path.isfile(icon_path):
        icon_line = f'$s.IconLocation = "{icon_path}"; '
    else:
        icon_line = ""
        print(f"\033[33m[warning]\033[0m icon.ico not found at:")
        print(f"    {icon_path}")
        print("    (shortcut will be created without a custom icon)")
        print()

    ps_script = f'''
$W = New-Object -ComObject WScript.Shell
$desktop = $W.SpecialFolders("Desktop")
$lnkPath = Join-Path $desktop "Pinaltune.lnk"

$s = $W.CreateShortcut($lnkPath)
$s.TargetPath = "{target_path}"
$s.Arguments = '"{arg}"'
$s.WorkingDirectory = "{root}"
{icon_line}
$s.Description = "Pinaltune"
$s.Save()

Write-Output $lnkPath
'''

    result = subprocess.run(
        ["powershell", "-NoProfile", "-Command", ps_script],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace"
    )

    if result.returncode == 0:
        real_lnk_path = result.stdout.strip()

        print(f"\033[1;92m[ok]\033[0m Shortcut created on Desktop:")
        print(f"    {real_lnk_path}")
        print()
        print("\033[1;92m✓ Shortcut created successfully!\033[0m")

        return True

    print("\033[31m[error] failed to create shortcut:\033[0m")
    print(f"    {result.stderr.strip()}")
    print()

    return False


if __name__ == "__main__":
    ensure_admin()
    success = create_shortcut()
    print()
    time.sleep(2)
