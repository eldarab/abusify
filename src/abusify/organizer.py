from __future__ import annotations

import logging
import shutil
from pathlib import Path
from typing import Iterable, List

from mutagen.id3 import ID3, ID3NoHeaderError

# Module-level logger
logger = logging.getLogger(__name__)


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
    except ID3NoHeaderError:
        logger.warning("No ID3 header found for %s; using default metadata", file.name)
        album_artist, album_name, title = "Unknown Artist", "Unknown Album", file.stem

    cleaned = (_clean(album_artist), _clean(album_name), _clean(title))
    logger.debug("Metadata for %s: artist=%r, album=%r, title=%r", file.name, *cleaned)
    return cleaned


def organize_paths(
        paths: Iterable[Path],
        root: str | Path = "music",
) -> List[Path]:
    """
    Move files to: root / <Album‑Artist> / <Album‑Name> / <filename>
    and return the **new** file paths.
    """
    root = Path(root).expanduser().resolve()
    logger.info("Organizing %d paths into %s", len(list(paths)), root)
    new_paths: List[Path] = []

    for p in paths:
        if not p.exists():
            logger.warning("Path does not exist, skipping: %s", p)
            continue
        if not p.is_file():
            logger.warning("Path is not a file, skipping: %s", p)
            continue

        album_artist, album_name, _ = _metadata_for(p)
        dest_dir = root / album_artist / album_name
        dest_dir.mkdir(parents=True, exist_ok=True)

        dest_path = dest_dir / p.name
        shutil.move(str(p), dest_path)
        logger.info("Moved %s to %s", p, dest_path)
        new_paths.append(dest_path)

    logger.info("Organization complete. %d files moved.", len(new_paths))
    return new_paths
