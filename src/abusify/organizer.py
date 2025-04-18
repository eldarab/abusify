import shutil
from pathlib import Path


def organize_paths(paths, root: str | Path = "music") -> None:
    """
    Move files so they live under root/Artist/<Unknown Album>/Title.ext.

    Very naive: parses "Artist - Title.ext". If filename doesn't conform,
    leaves the file untouched.
    """
    root = Path(root).expanduser()
    for p in paths:
        if not p.is_file():
            continue
        name = p.stem
        if " - " not in name:
            continue
        artist, title = name.split(" - ", 1)
        dest_dir = root / artist / "Unknown Album"
        dest_dir.mkdir(parents=True, exist_ok=True)
        shutil.move(str(p), dest_dir / p.name)
