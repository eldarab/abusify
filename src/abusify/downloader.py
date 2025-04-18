"""
downloader.py – robust helpers that shell out to `spotdl` CLI.

Works identically in scripts and Jupyter notebooks
(no event‑loop or rich.Live collisions).
"""
from __future__ import annotations
import os
import subprocess
import sys
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv

load_dotenv()  # for SPOTIFY_CLIENT_ID/SECRET


# ------------------------------------------------------------------ #
# Shared helpers
# ------------------------------------------------------------------ #
def _build_command(url: str, out_dir: Path) -> List[str]:
    """
    Return the spotdl CLI command for a single *entity* URL.

    The output template reproduces `{artist} - {title}.ext` in caller dir.
    """
    return [
        sys.executable, "-m", "spotdl",
        url,
        "--output", str(out_dir / "{artists} - {title}.{output-ext}"),
        "--ffmpeg", "ffmpeg",  # rely on PATH
    ]


def _run_spotdl(urls: List[str], out_dir: Path) -> List[Path]:
    """
    Download one or more URLs via spotdl CLI.
    Returns list of files that now exist.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    paths_before = set(out_dir.glob("**/*"))

    for url in urls:
        cmd = _build_command(url, out_dir)
        completed = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True
        )
        if completed.returncode != 0:
            raise RuntimeError(
                f"spotdl failed for {url}\n--- stdout+stderr ---\n{completed.stdout}"
            )

    paths_after = set(out_dir.glob("**/*"))
    return [p for p in paths_after - paths_before if p.is_file()]


# ------------------------------------------------------------------ #
# Public API
# ------------------------------------------------------------------ #
def download_song(url: str, *, out_dir: str | Path = "music") -> Optional[Path]:
    paths = _run_spotdl([url], Path(out_dir).expanduser())
    return paths[0] if paths else None


def download_album(url: str, *, out_dir: str | Path = "music") -> List[Path]:
    return _run_spotdl([url], Path(out_dir).expanduser())


def download_artist(url: str, *, out_dir: str | Path = "music") -> List[Path]:
    return _run_spotdl([url], Path(out_dir).expanduser())


def download_playlist(url: str, *, out_dir: str | Path = "music") -> List[Path]:
    return _run_spotdl([url], Path(out_dir).expanduser())
