from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import List, Union, Optional

from dotenv import load_dotenv

# accepted Spotify entity URL prefixes
_KIND_PREFIXES = {
    "track": "https://open.spotify.com/track/",
    "album": "https://open.spotify.com/album/",
    "artist": "https://open.spotify.com/artist/",
    "playlist": "https://open.spotify.com/playlist/",
}
load_dotenv()  # for SPOTIFY_CLIENT_ID/SECRET


def _build_command(url: str, out_dir: Path) -> List[str]:
    """
    Return the spotdl CLI command for a single *entity* URL.

    The output template reproduces `{artist} - {title}.ext` in caller dir.
    """
    return [
        sys.executable,
        "-m",
        "spotdl",
        url,
        "--output",
        str(out_dir / "{artists} - {title}.{output-ext}"),
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
        completed = subprocess.run(
            cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True
        )
        if completed.returncode != 0:
            raise RuntimeError(
                f"spotdl failed for {url}\n--- stdout+stderr ---\n{completed.stdout}"
            )

    paths_after = set(out_dir.glob("**/*"))
    return [p for p in paths_after - paths_before if p.is_file()]


def download_spotify_url(
    url: str, *, out_dir: str | Path = "music"
) -> Union[Optional[Path], List[Path]]:
    """
    Download *any* Spotify entity URL (track/album/artist/playlist).

    Returns
    -------
    Path | None
        for track URLs (single file)
    List[Path]
        for album/artist/playlist URLs (multiple files)
    """
    url = url.strip()
    kind = next((k for k, p in _KIND_PREFIXES.items() if url.startswith(p)), None)
    if kind is None:
        raise ValueError("URL does not look like a Spotify track/album/artist/playlist")

    paths = _run_spotdl([url], Path(out_dir).expanduser())
    return paths[0] if kind == "track" else paths
