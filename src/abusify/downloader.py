from __future__ import annotations

import logging
import subprocess
import sys
from pathlib import Path
from typing import List

from dotenv import load_dotenv

# Initialize .env vars for SPOTIFY_CLIENT_ID/SECRET
load_dotenv()

# Module-level logger
logger = logging.getLogger(__name__)

# accepted Spotify entity URL prefixes
_KIND_PREFIXES = {
    "track": "https://open.spotify.com/track/",
    "album": "https://open.spotify.com/album/",
    "artist": "https://open.spotify.com/artist/",
    "playlist": "https://open.spotify.com/playlist/",
}


def _build_command(url: str, out_dir: Path) -> List[str]:
    """
    Return the spotdl CLI command for a single *entity* URL.

    The output template reproduces `{title}.ext` in caller dir.
    """
    return [
        sys.executable,
        "-m",
        "spotdl",
        url,
        "--simple-tui",
        "--output",
        str(out_dir / "{title}.{output-ext}"),
        "--ffmpeg",
        "ffmpeg",  # rely on PATH
    ]


def _run_spotdl(urls: List[str], out_dir: Path) -> List[Path]:
    """
    Download one or more URLs via spotdl CLI, streaming logs live.
    Returns list of files that now exist.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    paths_before = set(out_dir.glob("**/*"))

    for url in urls:
        cmd = _build_command(url, out_dir)
        logger.info("Starting spotdl for %s", url)

        # Stream stdout and stderr combined, decode as utf-8, ignoring errors
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            text=True,
            encoding='utf-8',
            errors='ignore',
        )
        assert process.stdout is not None
        for line in process.stdout:
            logger.info("[spotdl] %s", line.rstrip())

        return_code = process.wait(timeout=300)
        if return_code != 0:
            logger.error("spotdl failed for %s with exit code %d", url, return_code)
            raise RuntimeError(f"spotdl failed for {url} (exit code {return_code})")

    paths_after = set(out_dir.glob("**/*"))
    return [p for p in paths_after - paths_before if p.is_file()]


def download_spotify_url(
        url: str, *, out_dir: str | Path = "music"
) -> List[Path]:
    """
    Download *any* Spotify entity URL (track/album/artist/playlist).

    Returns
    -------
    List[Path]
    """
    url = url.strip()
    kind = next((k for k, p in _KIND_PREFIXES.items() if url.startswith(p)), None)
    if kind is None:
        msg = "URL does not look like a Spotify track/album/artist/playlist"
        logger.error(msg)
        raise ValueError(msg)

    paths = _run_spotdl([url], Path(out_dir).expanduser())
    return paths
