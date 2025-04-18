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
    Download one or more URLs via spotdl CLI.
    Returns list of files that now exist.
    """
    out_dir.mkdir(parents=True, exist_ok=True)
    paths_before = set(out_dir.glob("**/*"))

    for url in urls:
        cmd = _build_command(url, out_dir)
        # run without automatic text decoding; capture raw bytes
        completed = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=300,
        )
        raw_out = completed.stdout  # bytes
        raw_err = completed.stderr  # bytes

        # decode for human-readable logs, ignoring any bad bytes
        decoded_out = raw_out.decode('utf-8', errors='ignore')
        decoded_err = raw_err.decode('utf-8', errors='ignore')

        # log the decoded output
        logger.info("spotdl output for %s:\n%s", url, decoded_out)
        if decoded_err:
            logger.error("spotdl errors for %s:\n%s", url, decoded_err)

        if completed.returncode != 0:
            # raise with decoded logs; raw_out/raw_err still available for dead-letter
            error_msg = (
                f"spotdl failed for {url}\n"
                f"--- decoded stdout ---\n{decoded_out}\n"
                f"--- decoded stderr ---\n{decoded_err}"
            )
            logger.error(error_msg)
            raise RuntimeError(error_msg)

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
