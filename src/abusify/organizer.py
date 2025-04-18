from __future__ import annotations
from pathlib import Path
import shutil
from typing import Iterable, List

from mutagen.id3 import ID3, ID3NoHeaderError


def _metadata_for(file: Path) -> tuple[str, str, str]:
    """
    Return (artist, album_artist, title) from ID3 tags, falling back to "Unknown".
    """
    try:
        tags = ID3(file)
        artist = tags.get("TPE1", ["Unknown Artist"])[0]
        album_artist = tags.get("TPE2", [tags.get("TALB", ["Unknown Album"])[0]])[0]
        title = tags.get("TIT2", [file.stem])[0]
    except ID3NoHeaderError:
        artist, album_artist, title = "Unknown Artist", "Unknown Album", file.stem

    # sanitise path‑breaking chars
    clean = lambda s: s.replace("/", "_").strip()
    return clean(artist), clean(album_artist), clean(title)


def organize_paths(
        paths: Iterable[Path],
        root: str | Path = "music",
) -> List[Path]:
    """
    Move files so they live under:

        root / <Artist> / <Album‑Artist> / <filename>

    Returns the new paths so callers can act on them.
    """
    root = Path(root).expanduser().resolve()
    new_paths: List[Path] = []

    for p in paths:
        if not p.exists() or not p.is_file():
            continue

        artist, album_artist, _ = _metadata_for(p)
        dest_dir = root / artist / album_artist
        dest_dir.mkdir(parents=True, exist_ok=True)

        dest_path = dest_dir / p.name
        shutil.move(str(p), dest_path)
        new_paths.append(dest_path)

    return new_paths
