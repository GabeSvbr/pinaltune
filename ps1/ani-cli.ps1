$ErrorActionPreference = 'Continue'
[Net.ServicePointManager]::SecurityProtocol = [Net.SecurityProtocolType]::Tls12

function Show-Menu {
    Clear-Host
    Write-Host "==========================================================" -ForegroundColor Cyan
    Write-Host "          ani-cli Installer Windows(10/11)           " -ForegroundColor Cyan
    Write-Host "            Made With Love              "  -ForegroundColor Cyan
    Write-Host "==========================================================" -ForegroundColor Cyan
    Write-Host " 1. INSTALL / REPAIR "
    Write-Host " 2. UPDATE (Refresh ani-cli, yt-dlp, and FFmpeg)"
    Write-Host " 3. DOWNLOAD VIDEOS (Save to PC)"
    Write-Host " 4. UNINSTALL "
    Write-Host " 5. EXIT"
    Write-Host "==========================================================" -ForegroundColor Cyan
    $choice = Read-Host "Select an option [1-5]"
    return $choice
}

function Terminate-Locks {
    Write-Host "`n[*] Terminating locked background processes to prevent errors..." -ForegroundColor Yellow
    $lockedProcesses = @("7z*", "git*", "bash", "yt-dlp", "aria2c", "ffmpeg", "mpv", "vlc")
    foreach ($proc in $lockedProcesses) {
        Get-Process -Name $proc -ErrorAction SilentlyContinue | Stop-Process -Force
    }
    Start-Sleep -Seconds 2
}

function Download-WithProgress {
    param([string]$Url, [string]$Destination)
    $fileName = Split-Path $Destination -Leaf
    Write-Host "`nDownloading $fileName..." -ForegroundColor Cyan
    $request = [System.Net.WebRequest]::Create($Url)
    $response = $request.GetResponse()
    $totalBytes = $response.ContentLength
    $stream = $response.GetResponseStream()
    $reader = New-Object System.IO.FileStream($Destination, [System.IO.FileMode]::Create)
    $buffer = New-Object byte[] 8192
    $downloadedBytes = 0
    while (($count = $stream.Read($buffer, 0, $buffer.Length)) -gt 0) {
        $reader.Write($buffer, 0, $count)
        $downloadedBytes += $count
        if ($totalBytes -gt 0) {
            $percentage = [math]::Round(($downloadedBytes / $totalBytes) * 100, 2)
            Write-Progress -Activity "Downloading $fileName" -Status "$percentage% Complete" -PercentComplete $percentage
        }
    }
    $reader.Close(); $stream.Close()
    Write-Progress -Activity "Downloading $fileName" -Completed
}

function Update-FFmpeg {
    Write-Host "`nFetching latest FFmpeg from BtbN GitHub..." -ForegroundColor Yellow
    $releases = Invoke-RestMethod -Uri 'https://api.github.com/repos/BtbN/FFmpeg-Builds/releases'
    $asset = $releases[0].assets | Where-Object { $_.name -match 'win64-gpl\.zip$' } | Select-Object -First 1
    $destZip = "$env:TEMP\$($asset.name)"
    
    if (Get-Command aria2c -ErrorAction SilentlyContinue) {
        Write-Host "Accelerating download with aria2c..." -ForegroundColor Cyan
        & aria2c -x 16 -s 16 -k 1M -d "$env:TEMP" -o "$($asset.name)" $asset.browser_download_url
    } else {
        Download-WithProgress -Url $asset.browser_download_url -Destination $destZip
    }

    $ffmpegDir = "$env:LOCALAPPDATA\ffmpeg_custom"
    if (Test-Path $ffmpegDir) { Remove-Item -Path $ffmpegDir -Recurse -Force }
    Write-Host "Extracting FFmpeg..." -ForegroundColor Cyan
    Expand-Archive -Path $destZip -DestinationPath $ffmpegDir -Force
    $ffmpegBinPath = (Get-ChildItem -Path $ffmpegDir -Filter "ffmpeg.exe" -Recurse).DirectoryName
    $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    if ($userPath -notmatch [regex]::Escape($ffmpegBinPath)) {
        [Environment]::SetEnvironmentVariable('Path', "$userPath;$ffmpegBinPath", 'User')
    }
    Write-Host "FFmpeg Updated Successfully." -ForegroundColor Green
}

function Run-Install {
    Terminate-Locks

    Write-Host "`n[1/6] Checking Scoop and Git..." -ForegroundColor Yellow
    if (!(Get-Command scoop -ErrorAction SilentlyContinue)) {
        Invoke-RestMethod -Uri https://get.scoop.sh | Invoke-Expression
    }
    scoop config aria2-enabled false
    scoop config aria2-warning-enabled false
    
    scoop install git
    scoop update
    scoop bucket add extras

    $gitBinPath = "$env:USERPROFILE\scoop\apps\git\current\bin"
    $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    if ($userPath -notmatch [regex]::Escape($gitBinPath)) {
        [Environment]::SetEnvironmentVariable('Path', "$userPath;$gitBinPath", 'User')
        $env:Path = "$env:Path;$gitBinPath"
    }
    $bashExe = "$gitBinPath\bash.exe"

    Write-Host "`n[2/6] Installing ani-cli, fzf, yt-dlp, aria2, and deno..." -ForegroundColor Yellow
    scoop install ani-cli fzf yt-dlp aria2 deno
    
    Write-Host "`nRemoving mpv to force VLC playback..." -ForegroundColor Yellow
    scoop uninstall mpv -p

    Write-Host "`n[3/6] Setting up high-speed FFmpeg..." -ForegroundColor Yellow
    Update-FFmpeg

    Write-Host "`n[4/6] Configuring VLC and Git Bash Shims..." -ForegroundColor Yellow
    $vlcPath = if (Test-Path "C:\Program Files\VideoLAN\VLC") { "C:\Program Files\VideoLAN\VLC" } else { "C:\Program Files (x86)\VideoLAN\VLC" }
    if (Test-Path "$vlcPath\vlc.exe") {
        $bashVlc = "/" + $vlcPath.Substring(0,1).ToLower() + $vlcPath.Substring(2).Replace('\', '/') + "/vlc.exe"
        $tempSh = "$env:TEMP\setup.sh"
        @"
echo '#!/bin/bash' > ~/scoop/shims/vlc.exe
echo '"$bashVlc" "`$@"' >> ~/scoop/shims/vlc.exe
chmod +x ~/scoop/shims/vlc.exe
rm -f ~/.bashrc
echo "alias ani-cli='ani-cli -v'" > ~/.bashrc
"@ | Set-Content -Path $tempSh -Encoding Ascii
        & $bashExe $tempSh
        Remove-Item $tempSh
    }

    Write-Host "`n[5/6] Applying Speed Hacks..." -ForegroundColor Yellow
    $configDir = "$env:APPDATA\yt-dlp"
    if (!(Test-Path $configDir)) { New-Item -ItemType Directory -Force -Path $configDir | Out-Null }
    Set-Content -Path "$configDir\config" -Value "--downloader aria2c`n--downloader-args aria2c:`"-x 16 -s 16 -k 1M`"" -Encoding ASCII

    Write-Host "`n[6/6] Building PowerShell/CMD Wrappers..." -ForegroundColor Yellow
    $psProfile = $PROFILE.CurrentUserAllHosts
    if (!(Test-Path (Split-Path $psProfile))) { New-Item -ItemType Directory -Path (Split-Path $psProfile) -Force }
    $psFunc = "`nfunction ani-cli { & ani-cli.cmd -v `$args }"
    if (!(Test-Path $psProfile) -or !(Select-String "function ani-cli" $psProfile)) { Add-Content $psProfile $psFunc }
    Set-Content -Path "$env:USERPROFILE\scoop\shims\ani-cli.bat" -Value "@echo off`n`"%~dp0ani-cli.cmd`" -v %*" -Encoding Ascii

    Write-Host "`nSetup Complete! Restart your terminal and type 'ani-cli'." -ForegroundColor Green
    Pause
}

function Run-Update {
    Terminate-Locks
    Write-Host "`n[1/2] Updating Scoop packages..." -ForegroundColor Yellow
    scoop update
    scoop update *
    Write-Host "`n[2/2] Updating custom FFmpeg build..." -ForegroundColor Yellow
    Update-FFmpeg
    Write-Host "`nAll components updated!" -ForegroundColor Green
    Pause
}

function Run-Download {
    $anime = Read-Host "`nEnter Anime name to download"
    if ($anime) {
        Write-Host "`nStarting Download Mode for: $anime" -ForegroundColor Cyan
        & ani-cli.cmd -d $anime
    }
    Pause
}

function Run-Uninstall {
    Clear-Host
    Write-Host "==========================================================" -ForegroundColor Red
    Write-Host "          COMMENCING FULL UNINSTALLATION...               " -ForegroundColor Red
    Write-Host "==========================================================" -ForegroundColor Red

    Terminate-Locks

    Write-Host "`n[1/5] Removing PowerShell profile wrappers..." -ForegroundColor Yellow
    $psProfile = $PROFILE.CurrentUserAllHosts
    if (Test-Path $psProfile) {
        $profileContent = Get-Content -Path $psProfile -Raw
        $funcString = "`nfunction ani-cli { & ani-cli.cmd -v `$args }"
        
        if ($profileContent.Contains($funcString)) {
            $newProfileContent = $profileContent.Replace($funcString, "")
            Set-Content -Path $psProfile -Value $newProfileContent -Encoding Ascii
            Write-Host " -> PowerShell wrapper removed." -ForegroundColor Green
        } else {
            Write-Host " -> No PowerShell wrapper found." -ForegroundColor DarkGray
        }
    }

    Write-Host "`n[2/5] Removing configurations (.bashrc & yt-dlp)..." -ForegroundColor Yellow
    if (Test-Path "$env:APPDATA\yt-dlp") { 
        Remove-Item "$env:APPDATA\yt-dlp" -Recurse -Force 
        Write-Host " -> yt-dlp configurations removed." -ForegroundColor Green
    }
    if (Test-Path "$env:USERPROFILE\.bashrc") { 
        Remove-Item "$env:USERPROFILE\.bashrc" -Force 
        Write-Host " -> .bashrc alias removed." -ForegroundColor Green
    }

    Write-Host "`n[3/5] Removing custom FFmpeg and Temp files..." -ForegroundColor Yellow
    $ffmpegDir = "$env:LOCALAPPDATA\ffmpeg_custom"
    if (Test-Path $ffmpegDir) { 
        Remove-Item $ffmpegDir -Recurse -Force 
        Write-Host " -> Custom FFmpeg folder removed." -ForegroundColor Green
    }
    Get-ChildItem -Path "$env:TEMP" -Filter "*ffmpeg*win64-gpl.zip" -ErrorAction SilentlyContinue | Remove-Item -Force
    Write-Host " -> FFmpeg temp downloads cleared." -ForegroundColor Green

    Write-Host "`n[4/5] Removing Scoop and all installed packages..." -ForegroundColor Yellow
    $scoopDir = "$env:USERPROFILE\scoop"
    if (Test-Path $scoopDir) { 
        # Bulletproof deletion method using native Windows cmd to bypass read-only Git files
        cmd.exe /c "rmdir /s /q `"$scoopDir`""
        if (Test-Path $scoopDir) {
            Remove-Item $scoopDir -Recurse -Force -ErrorAction SilentlyContinue 
        }
        Write-Host " -> Scoop and all CLI tools (ani-cli, yt-dlp, etc.) removed." -ForegroundColor Green
    }

    Write-Host "`n[5/5] Cleaning Environment Variables (PATH)..." -ForegroundColor Yellow
    $userPath = [Environment]::GetEnvironmentVariable('Path', 'User')
    if ($userPath) {
        $cleanPathArray = $userPath -split ';' | Where-Object { 
            -not [string]::IsNullOrWhiteSpace($_) -and 
            $_ -notmatch [regex]::Escape("\scoop\") -and 
            $_ -notmatch [regex]::Escape("ffmpeg_custom") 
        }
        $cleanPath = $cleanPathArray -join ';'
        [Environment]::SetEnvironmentVariable('Path', $cleanPath, 'User')
        Write-Host " -> System PATH restored to original state." -ForegroundColor Green
    }

    Write-Host "`n==========================================================" -ForegroundColor Red
    Write-Host " Uninstallation Complete! All system changes are undone." -ForegroundColor Green
    Write-Host "==========================================================" -ForegroundColor Red
    Pause
}

do {
    $userChoice = Show-Menu
    if ($userChoice -eq '1') { Run-Install }
    elseif ($userChoice -eq '2') { Run-Update }
    elseif ($userChoice -eq '3') { Run-Download }
    elseif ($userChoice -eq '4') { Run-Uninstall }
} while ($userChoice -ne '5')