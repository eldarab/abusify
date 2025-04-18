from __future__ import annotations

import shutil
from pathlib import Path
from typing import Iterable, List

from mutagen.id3 import ID3, ID3NoHeaderError


def _clean(text: str) -> str:
    """Remove slashes & trim whitespace so the string is path‑safe."""
    return text.replace("/", "_").strip() or "Unknown"


def _metadata_for(file: Path) -> tuple[str, str, str]:
    """
    Return (album_artist, album_name, title) using ID3 tags, with fallbacks.
    """
    try:
        tags = ID3(file)
        album_artist = tags.get("TPE2", [tags.get("TPE1", ["Unknown Artist"])[0]])[0]
        album_name = tags.get("TALB", ["Unknown Album"])[0]
        title = tags.get("TIT2", [file.stem])[0]
    except ID3NoHeaderError:  # no ID3 at all
        album_artist, album_name, title = "Unknown Artist", "Unknown Album", file.stem

    return _clean(album_artist), _clean(album_name), _clean(title)


def organize_paths(
    paths: Iterable[Path],
    root: str | Path = "music",
) -> List[Path]:
    """
    Move files to:  root / <Album‑Artist> / <Album‑Name> / <filename>
    and return the **new** file paths.
    """
    root = Path(root).expanduser().resolve()
    new_paths: List[Path] = []

    for p in paths:
        if not p.exists() or not p.is_file():
            continue

        album_artist, album_name, _ = _metadata_for(p)
        dest_dir = root / album_artist / album_name
        dest_dir.mkdir(parents=True, exist_ok=True)

        dest_path = dest_dir / p.name
        shutil.move(str(p), dest_path)
        new_paths.append(dest_path)

    return new_paths
