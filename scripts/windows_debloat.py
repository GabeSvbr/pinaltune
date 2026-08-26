import ctypes, os, subprocess, time , winreg , sys, ctypes
from Utilities_pin import bar, clear_console, get_option,confirmation


#   CUSTOM WINDOWS SETUP (Commercial and Private)

def log(m): print(f"\033[1;38;2;124;77;255m>>\033[1;38;2;255;105;180m {m}\033[0m")

def set_reg(hive,path,name,tipo,valor):
    try:
        k=winreg.CreateKeyEx(hive,path,0,winreg.KEY_ALL_ACCESS);winreg.SetValueEx(k,name,0,tipo,valor);winreg.CloseKey(k);return True
    except PermissionError: print(f"Sem permissão para gravar {name} em {path}")
    except OSError as e: print(f"Falha ao gravar {name} em {path}: {e}")
    return False

#       "ls" poweshell shortcut

def create_ls_shortcut():
    log("Creating 'ls' shortcut for PowerShell")
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("Execute como Administrador."); return
    ps_path = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
    set_reg(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\ls.exe", "", winreg.REG_SZ, ps_path)
    ps_path = r"C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe"
    set_reg(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\ps.exe", "", winreg.REG_SZ, ps_path)


#       Restart Explorer

def restart_explorer():
    log("Restarting Explorer")
    subprocess.run(["taskkill","/F","/IM","explorer.exe"],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    subprocess.Popen(["explorer.exe"])

#       Align Taskbar to the left

def align_taskbar_left():
    log("Aligning Taskbar to the left")
    set_reg(winreg.HKEY_CURRENT_USER,r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced","TaskbarAl",winreg.REG_DWORD,0)

#       Debloat Windows

def debloat_windows():
    log("Debloating Windows")
    if not ctypes.windll.shell32.IsUserAnAdmin():
        params = " ".join(f'"{arg}"' for arg in sys.argv)
        if ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, params, None, 1
        ) <= 32:
            return
        sys.exit()

    ps_script = r'''
$packages = "Microsoft.3DBuilder","Microsoft.BingNews","Microsoft.BingSearch","Microsoft.BingWeather","Microsoft.GetHelp","Microsoft.Getstarted","Microsoft.GamingApp","Microsoft.Microsoft3DViewer","Microsoft.MicrosoftEdge.Stable","Microsoft.MicrosoftOfficeHub","Microsoft.MicrosoftSolitaireCollection","Microsoft.MicrosoftStickyNotes","Microsoft.MixedReality.Portal","Microsoft.NotePad","Microsoft.Office.OneNote","Microsoft.OneDrive","Microsoft.MSPaint","Microsoft.OutlookForWindows","Microsoft.Paint","Microsoft.People","Microsoft.PowerAutomateDesktop","Microsoft.SkypeApp","Microsoft.Todos","Microsoft.Wallet","Microsoft.Whiteboard","Microsoft.WindowsAlarms","Microsoft.WindowsCamera","Microsoft.Windows.DevHome","Microsoft.WindowsFeedbackHub","Microsoft.WindowsMaps","Microsoft.WindowsSoundRecorder","Microsoft.YourPhone","Microsoft.AAD.BrokerPlugin","Microsoft.Advertising.Xaml","Microsoft.Cortana","Microsoft.Services.Store.Engagement","Microsoft.Windows.Cortana","Microsoft.Win32WebViewHost","Microsoft.WindowsCommunicationsApps","Microsoft.Windows.ContentDeliveryManager","Microsoft.Windows.NarratorQuickStart","Microsoft.Windows.ParentalControls","Microsoft.Windows.PeopleExperienceHost","Microsoft.Windows.PinningConfirmationDialog","Microsoft.Windows.SecureAssessmentBrowser","Microsoft.Windows.XGpuEjectDialog","Microsoft.Windows.OOBENetworkCaptivePortal","Microsoft.Windows.OOBENetworkConnectionFlow"

foreach ($p in $packages) {
    Get-AppxPackage -AllUsers | Where-Object Name -like $p | Remove-AppxPackage -AllUsers -Confirm:$false -ErrorAction SilentlyContinue
    $pn = (Get-AppxProvisionedPackage -Online | Where-Object DisplayName -like $p).PackageName
    if ($pn) { dism.exe /Online /Remove-ProvisionedAppxPackage /PackageName:$pn *> $null }
}

"msedge","edgeupdate","edgewebview2","edgecore" | ForEach-Object { Stop-Process -Name $_ -Force -ErrorAction SilentlyContinue }
Start-Sleep 2
"msedge","edgeupdate","edgewebview2","edgecore" | ForEach-Object { Stop-Process -Name $_ -Force -ErrorAction SilentlyContinue }

"C:\Program Files (x86)\Microsoft\Edge","C:\Program Files (x86)\Microsoft\EdgeUpdate","C:\Program Files (x86)\Microsoft\EdgeWebView","C:\Program Files (x86)\Microsoft\EdgeCore","C:\Program Files\Microsoft\Edge","C:\Program Files\Microsoft\EdgeUpdate","$env:LOCALAPPDATA\Microsoft\Edge","$env:PROGRAMDATA\Microsoft\Edge" | ForEach-Object {
    if (Test-Path $_) {
        takeown /f $_ /r /d Y *> $null
        icacls $_ /grant Administrators:F /t /c /l /q *> $null
        Remove-Item $_ -Recurse -Force -ErrorAction SilentlyContinue
    }
}

New-Item "HKLM:\SOFTWARE\Microsoft\EdgeUpdate" -Force | Out-Null
New-ItemProperty "HKLM:\SOFTWARE\Microsoft\EdgeUpdate" -Name DoNotUpdateToEdgeWithChromium -Value 1 -PropertyType DWord -Force | Out-Null
"edgeupdate","edgeupdatem" | ForEach-Object { Get-Service -Name $_ -ErrorAction SilentlyContinue | Set-Service -StartupType Disabled -ErrorAction SilentlyContinue; Stop-Service -Name $_ -Force -ErrorAction SilentlyContinue }
"\Microsoft\EdgeUpdate\EdgeUpdateTaskMachineCore","\Microsoft\EdgeUpdate\EdgeUpdateTaskMachineUA" | ForEach-Object { schtasks /Change /TN $_ /Disable *> $null }
New-Item "HKLM:\SOFTWARE\Policies\Microsoft\EdgeUpdate" -Force | Out-Null
New-ItemProperty "HKLM:\SOFTWARE\Policies\Microsoft\EdgeUpdate" -Name InstallDefault -Value 0 -PropertyType DWord -Force | Out-Null

"DiagTrack","dmwappushservice","Wecsvc","RemoteRegistry" | ForEach-Object { Stop-Service $_ -Force -ErrorAction SilentlyContinue; Set-Service $_ -StartupType Disabled -ErrorAction SilentlyContinue }

reg add "HKLM\Software\Policies\Microsoft\Windows\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection" /v AllowTelemetry /t REG_DWORD /d 0 /f >nul 2>&1

reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\Windows Search" /v AllowCortana /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\Search" /v CortanaConsent /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications" /v GlobalUserDisabled /t REG_DWORD /d 1 /f >nul 2>&1

reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v ContentDeliveryAllowed /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v OemPreInstalledAppsEnabled /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v PreInstalledAppsEnabled /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v SilentInstalledAppsEnabled /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v SystemPaneSuggestionsEnabled /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\ContentDeliveryManager" /v SubscribedContent-338393Enabled /t REG_DWORD /d 0 /f >nul 2>&1
reg add "HKLM\SOFTWARE\Policies\Microsoft\Windows\CloudContent" /v DisableWindowsSpotlightFeatures /t REG_DWORD /d 1 /f >nul 2>&1
'''
    script_path = os.path.join(os.getenv("TEMP", "."), "debloat_temp.ps1")
    with open(script_path, "w", encoding="utf-8") as f:
        f.write(ps_script)
    try:
        subprocess.run(
            ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", script_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
    finally:
        if os.path.exists(script_path):
            os.remove(script_path)

#       Disable Widgets and Disable search box

def disable_widgets_and_search_box():
    log("Disabling Windows Widgets")
    log("Disabling Search Box")
    try:
        chave_path = r"SOFTWARE\Policies\Microsoft\Dsh"
        chave = winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, chave_path, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(chave, "AllowNewsAndInterests", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(chave)
    except Exception as e:
        pass
    try:
        chave_path_user = r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced"
        chave = winreg.CreateKeyEx(winreg.HKEY_CURRENT_USER, chave_path_user, 0, winreg.KEY_WRITE)
        winreg.SetValueEx(chave, "TaskbarDa", 0, winreg.REG_DWORD, 0)
        winreg.CloseKey(chave)
    except Exception as e:
        pass

    set_reg(winreg.HKEY_CURRENT_USER,r"Software\Microsoft\Windows\CurrentVersion\Search","SearchboxTaskbarMode",winreg.REG_DWORD,0)

#       Show file extensions (.exe | .py | .txt)

def show_file_extensions():
    log("Show File Extensions")
    set_reg(winreg.HKEY_CURRENT_USER,r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced","HideFileExt",winreg.REG_DWORD,0)
    set_reg(winreg.HKEY_CURRENT_USER,r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced","Hidden",winreg.REG_DWORD,1)

#       Enable ending task Through Taskbar function

def enable_end_task():
    log("Enabling Taskbar End Task")
    set_reg(
        winreg.HKEY_CURRENT_USER,
        r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced\TaskbarDeveloperSettings",
        "TaskbarEndTask",
        winreg.REG_DWORD,
        1
    )
#       Enable windows dark mode

def enable_dark_mode():
    log("Enabling Dark Mode")
    for v in ("AppsUseLightTheme","SystemUsesLightTheme"):
        set_reg(winreg.HKEY_CURRENT_USER,r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",v,winreg.REG_DWORD,0)

#       Disable Windows Telemetry

def disable_telemetry():
    log("Disabling Telemtry")
    set_reg(winreg.HKEY_LOCAL_MACHINE,r"SOFTWARE\Policies\Microsoft\Windows\DataCollection","AllowTelemetry",winreg.REG_DWORD,0)
    ps="""Set-Service -Name DiagTrack -StartupType Disabled -ErrorAction SilentlyContinue
    Stop-Service -Name DiagTrack -Force -ErrorAction SilentlyContinue
    Set-Service -Name dmwappushservice -StartupType Disabled -ErrorAction SilentlyContinue
    Stop-Service -Name dmwappushservice -Force -ErrorAction SilentlyContinue"""
    subprocess.run(["powershell","-NoProfile","-ExecutionPolicy","Bypass","-Command",ps])

#       Clear Taskbar

def clear_taskbar():
    log("Cleaning Taskbar")
    ps=r'''$shell=New-Object -ComObject Shell.Application
    $apps=$shell.Namespace("shell:::{4234d49b-0245-4df3-b780-3893943456e1}").Items()
    $manter=@("File Explorer","Files","Explorador de Arquivos","Configurações","Terminal","Helium","Steam","Discord","VS Code","Kate")
    foreach($item in $apps){if($manter -contains $item.Name){$item.InvokeVerb("taskbarpin")}else{$item.InvokeVerb("taskbarunpin")}}'''
    subprocess.run(["powershell","-NoProfile","-ExecutionPolicy","Bypass","-Command",ps])

#       Set power plan to high performance

def power_plan_high_performance():
    log("Energy Plan to High Performance")
    guid="8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"
    subprocess.run(["powercfg","-duplicatescheme",guid],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
    subprocess.run(["powercfg","/setactive",guid])

#       Disable Startup Delay

def disable_startup_delay():
    log("Disabling Startup Delay")
    set_reg(winreg.HKEY_CURRENT_USER,r"Software\Microsoft\Windows\CurrentVersion\Explorer\Serialize","StartupDelayInMSec",winreg.REG_DWORD,0)

#       Clear Startup Menu

def reset_pins():
    log("Reseting pinned apps")
    la = os.getenv("LOCALAPPDATA")
    for p in ("explorer.exe", "StartMenuExperienceHost.exe"):
        subprocess.run(["taskkill", "/f", "/im", p], capture_output=True)
    time.sleep(1)
    s2 = f"{la}\\Packages\\Microsoft.Windows.StartMenuExperienceHost_cw5n1h2txyewy\\LocalState\\start2.bin"
    if os.path.isfile(s2): os.remove(s2)
    def rm_key(hive, path):
        try: k = winreg.OpenKey(hive, path, 0, winreg.KEY_ALL_ACCESS)
        except FileNotFoundError: return
        while True:
            try: rm_key(hive, f"{path}\\{winreg.EnumKey(k, 0)}")
            except OSError: break
        winreg.CloseKey(k); winreg.DeleteKey(hive, path)
    rm_key(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\CloudStore")


import os, ctypes, shutil, urllib.request, winreg

def lockscreen(url):
    if not ctypes.windll.shell32.IsUserAnAdmin():
        print("Execute como Administrador."); return

    url = url.replace("https://github.com/", "https://raw.githubusercontent.com/").replace("/blob/", "/")
    path = r"C:\Windows\Web\Screen\lockscreen_custom.png"

    try:
        tmp = os.path.join(os.environ["TEMP"], "lockscreen.png")
        urllib.request.urlretrieve(url, tmp)
        shutil.copyfile(tmp, path)

        key = winreg.CreateKey(winreg.HKEY_LOCAL_MACHINE,
            r"SOFTWARE\Policies\Microsoft\Windows\Personalization")
        winreg.SetValueEx(key, "LockScreenImage", 0, winreg.REG_SZ, path)
        winreg.SetValueEx(key, "LockScreenImageStatus", 0, winreg.REG_DWORD, 1)
        winreg.CloseKey(key)

        print("Lockscreen aplicada!")
    except Exception as e:
        print(f"Erro: {e}")


def main_auto_install():
    clear_console(); log("It is advised NOT to interact with the terminal until process is finished.")
    create_ls_shortcut(); align_taskbar_left();   clear_taskbar(); power_plan_high_performance ();    enable_dark_mode(); reset_pins();   disable_widgets_and_search_box();   disable_startup_delay()
    reset_pins();   enable_end_task();    show_file_extensions(); restart_explorer() 
    log("Process Finished!"); confirmation()

def download_and_apply_wallpaper(url):
    log(f"Applying Custom Wallpaper from {url}")
    if "github.com" in url and "/blob/" in url:
        url=url.replace("https://github.com/","https://raw.githubusercontent.com/").replace("/blob/","/")
    wp=os.path.join(os.environ["TEMP"],"wallpaper.jpg")
    urllib.request.urlretrieve(url,wp)
    ctypes.windll.user32.SystemParametersInfoW(20,0,wp,3)

def update():

    t = time.time()
    print(
        "\n\033[1;38;2;124;77;255m"
        "                  --- Updating ---"
        "\033[0m"
    )

    cmd = (
        'winget upgrade --all --silent '
        '--accept-source-agreements --accept-package-agreements '
        '--exclude Microsoft.Edge '
        '--exclude Microsoft.EdgeWebView2Runtime '
        '--exclude Microsoft.WindowsTerminal '
        '--exclude Microsoft.PowerShell '
        '--exclude Microsoft.VCRedist*'
    )

    try:
        subprocess.run(cmd, shell=True, check=True)
        print("Concluded")
    except subprocess.CalledProcessError:
        print("SubProcessError.")

    print(
        f"\033[1;93mElapsed time: "
        f"{time.time() - t:.4f}\033[0m"
    )








    
