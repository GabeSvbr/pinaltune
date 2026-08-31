import os
import subprocess
import sys
import importlib
import msvcrt
import winsound

_BASE_DIR = getattr(sys, "_MEIPASS", os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SOUNDS_DIR = os.path.join(_BASE_DIR, "Sounds")
DOWNLOADS_DIR = os.path.join(os.path.expanduser("~"), "Downloads", "output")


def clear_console():
    os.system("cls" if os.name == "nt" else "clear")


def bar():
    print("\033[1m#========================================================#\033[0m")


def confirmation():
    input("     \033[32mcontinue...\033[0m")
    _play_sound_safe(os.path.join(SOUNDS_DIR, "menu_back.wav"))


def _play_sound_safe(path):
    """Plays a short UI sound if the file exists; fails silently otherwise."""
    if not os.path.exists(path):
        return
    try:
        winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC | winsound.SND_NODEFAULT)
    except Exception:
        pass


def play_completion():
    _play_sound_safe(os.path.join(SOUNDS_DIR, "completion.wav"))


def arrow_menu(title, options):
    """Simple arrow-key menu: Up/Down arrows move the selection, Enter confirms,
    Esc/Backspace cancels (returns None)."""
    selected = 1

    while True:
        clear_console()
        bar()
        print(f"\033[1;38;2;124;77;255m{title}\033[0m")
        bar()

        for i, option in enumerate(options, 1):
            if i == selected:
                print(f"        \033[1;38;2;124;77;255m➜ {option}\033[0m")
            else:
                print(f"    {option}")

        key = msvcrt.getch()

        if key == b'\xe0':
            key = msvcrt.getch()
            if key == b'H':  # up arrow
                selected -= 1
            elif key == b'P':  # down arrow
                selected += 1

        elif key in b'123456789':
            number = int(key.decode())
            if number <= len(options):
                selected = number

        elif key == b'\r':
            return selected

        elif key in (b'\x1b', b'\x08'):
            return None

        selected = (selected - 1) % len(options) + 1


def _ensure_ytdlp():
    """Makes sure the 'yt-dlp' package is installed (pip)."""
    try:
        importlib.import_module("yt_dlp")
        return True
    except ImportError:
        print("\033[1;38;2;124;77;255m>>  yt-dlp not found, installing...\033[0m")
        try:
            subprocess.run(
                [sys.executable, "-m", "pip", "install", "-U", "yt-dlp"],
                check=True
            )
            importlib.invalidate_caches()
            importlib.import_module("yt_dlp")
            return True
        except Exception as e:
            print(f"\033[31m[error] could not install yt-dlp: {e}\033[0m")
            confirmation()
            return False


def _progress_hook(d):
    if d.get("status") == "downloading":
        pct = d.get("_percent_str", "").strip()
        speed = d.get("_speed_str", "").strip()
        eta = d.get("_eta_str", "").strip()
        print(f"\r\033[1;38;2;124;77;255m>> {pct}  {speed}  ETA {eta}   \033[0m", end="", flush=True)
    elif d.get("status") == "finished":
        print("\n\033[1;92m[ok] Download finished, processing...\033[0m")


def _download(url, audio_only=False):
    from yt_dlp import YoutubeDL

    os.makedirs(DOWNLOADS_DIR, exist_ok=True)

    options = {
        "outtmpl": os.path.join(DOWNLOADS_DIR, "%(title)s.%(ext)s"),
        "progress_hooks": [_progress_hook],
        "noplaylist": True,
        "quiet": True,
        "no_warnings": True,
    }

    if audio_only:
        options.update({
            "format": "bestaudio/best",
            "postprocessors": [{
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }],
        })
    else:
        options.update({
            "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
            "merge_output_format": "mp4",
        })

    try:
        with YoutubeDL(options) as ydl:
            ydl.download([url])
        print(f"\033[1;92m[ok] Saved to: {DOWNLOADS_DIR}\033[0m")
        play_completion()
    except Exception as e:
        print(f"\n\033[31m[error] failed to download: {e}\033[0m")


def youtube_download():
    clear_console()
    bar()
    print("\033[1;38;2;124;77;255m --> Download YouTube Video\033[0m")
    bar()

    if not _ensure_ytdlp():
        return

    url = input("    Paste the video URL (or ENTER to cancel): ").strip()
    if url == "":
        return

    choice = arrow_menu(
        "----< Choose Download Type >----",
        ["1 >> Download video (MP4)", "2 >> Download audio only (MP3)"]
    )

    if choice is None:
        return

    clear_console()
    bar()
    print(f"\033[1;38;2;124;77;255m>>  Downloading from: \033[1;38;2;255;105;180m{url}\033[0m")
    bar()

    _download(url, audio_only=(choice == 2))

    bar()
    confirmation()
