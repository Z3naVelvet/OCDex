from pathlib import Path
import base64, io, json, os, re
from PIL import Image

APPDATA = Path(os.environ.get("APPDATA", Path.home())) / "OCDEX"
UNIVERSES = APPDATA / "universes"
SETTINGS = APPDATA / "settings.json"
MAX_ARTWORK_SIZE = (768, 768)

DEFAULT_TYPES = [
    "Normal","Fire","Water","Electric","Grass","Ice","Fighting","Poison",
    "Ground","Flying","Psychic","Bug","Rock","Ghost","Dragon","Dark",
    "Steel","Fairy"
]

def ensure_storage():
    UNIVERSES.mkdir(parents=True, exist_ok=True)

def slugify(name):
    return re.sub(r"[^a-zA-Z0-9_-]+", "_", name.strip()).strip("_") or "universe"

def universe_path(name):
    return UNIVERSES / f"{slugify(name)}.json"

def image_to_data_uri(path, remove_background=False):
    """Load, optionally remove the background, resize, and embed artwork safely."""
    with Image.open(path) as source:
        original = source.convert("RGBA")

    img = original.copy()

    if remove_background:
        try:
            from rembg import remove
            result = remove(original.copy())

            if isinstance(result, Image.Image):
                img = result.convert("RGBA")
            elif isinstance(result, (bytes, bytearray)):
                with Image.open(io.BytesIO(result)) as processed:
                    img = processed.convert("RGBA")
            else:
                try:
                    img = Image.fromarray(result).convert("RGBA")
                except Exception:
                    img = original.copy()
        except Exception:
            # Background removal is optional; never let it break saving.
            img = original.copy()

    img.thumbnail(MAX_ARTWORK_SIZE, Image.Resampling.LANCZOS)
    buf = io.BytesIO()
    img.save(buf, format="PNG", optimize=True)
    encoded = base64.b64encode(buf.getvalue()).decode("ascii")
    return "data:image/png;base64," + encoded

def data_uri_to_image(uri):
    return Image.open(io.BytesIO(base64.b64decode(uri.split(",", 1)[1]))).convert("RGBA")

def load_universes():
    ensure_storage()
    result = {}
    for p in UNIVERSES.glob("*.json"):
        try:
            d = json.loads(p.read_text(encoding="utf-8"))
            result[d.get("name", p.stem)] = d
        except Exception:
            pass
    return result

def load_universe(name):
    p = universe_path(name)
    if not p.exists():
        return {"name": name, "creatures": []}
    return json.loads(p.read_text(encoding="utf-8"))

def save_universe(data):
    ensure_storage()
    universe_path(data["name"]).write_text(
        json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8"
    )

def create_universe(name):
    d = {"name": name, "creatures": []}
    save_universe(d)
    return d

def next_number(creatures):
    nums = [int(c["number"]) for c in creatures if str(c.get("number","")).isdigit()]
    return max(nums, default=0) + 1

def load_settings():
    ensure_storage()
    if SETTINGS.exists():
        try:
            return json.loads(SETTINGS.read_text(encoding="utf-8"))
        except Exception:
            pass
    d = {"types": DEFAULT_TYPES}
    save_settings(d)
    return d

def save_settings(data):
    ensure_storage()
    SETTINGS.write_text(json.dumps(data, indent=2), encoding="utf-8")
