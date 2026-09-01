import json
import os

THEMES = [
    ("Roxo", (124, 77, 255)),
    ("Azul", (0, 140, 255)),
    ("Ciano", (0, 220, 220)),
    ("Verde", (50, 205, 100)),
    ("Lima", (170, 255, 0)),
    ("Amarelo", (255, 210, 0)),
    ("Laranja", (255, 140, 0)),
    ("Vermelho", (255, 60, 70)),
    ("Rosa", (255, 70, 170)),
    ("Branco", (235, 235, 235)),
    ("Dourado", (255, 190, 60)),
    ("Lavanda", (190, 120, 255)),
]

_CONFIG_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "Pinaltune")
_CONFIG_FILE = os.path.join(_CONFIG_DIR, "config.json")


def get_theme_index():
    try:
        with open(_CONFIG_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        index = int(data.get("theme", 0))
        if 0 <= index < len(THEMES):
            return index
    except Exception:
        pass
    return 0


def set_theme_index(index):
    os.makedirs(_CONFIG_DIR, exist_ok=True)
    with open(_CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"theme": int(index)}, f)


def get_rgb():
    return THEMES[get_theme_index()][1]


def ansi():
    r, g, b = get_rgb()
    return f"\033[1;38;2;{r};{g};{b}m"


def color(text):
    return f"{ansi()}{text}\033[0m"
