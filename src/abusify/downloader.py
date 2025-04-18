from __future__ import annotations

import asyncio
import os
from pathlib import Path
from typing import Iterable, List, Optional

import nest_asyncio
from dotenv import load_dotenv
from spotdl.download.downloader import Downloader
from spotdl.types.album import Album
from spotdl.types.artist import Artist
from spotdl.types.playlist import Playlist
from spotdl.types.song import Song
from spotdl.utils.spotify import SpotifyClient, SpotifyError

load_dotenv()


def _ensure_event_loop_is_nestable() -> None:
    """
    In Jupyter/IPython an event loop is already running.
    `spotdl` will call `asyncio.run`, which normally fails.
    `nest_asyncio.apply()` makes nested loops legal.
    Safe to call repeatedly.
    """
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        # No loop yet → script mode; nothing to patch.
        return
    else:
        # We're inside a live loop (likely a notebook)
        nest_asyncio.apply()


def _ensure_spotify_client() -> None:
    _ensure_event_loop_is_nestable()  # ← NEW

    if getattr(SpotifyClient, "_client", None) is not None:
        return
    cid, secret = os.getenv("SPOTIFY_CLIENT_ID"), os.getenv("SPOTIFY_CLIENT_SECRET")
    if not (cid and secret):
        raise RuntimeError("Missing Spotify credentials.")
    try:
        SpotifyClient.init(client_id=cid, client_secret=secret, user_auth=False)
    except SpotifyError as err:
        if "already been initialized" not in str(err).lower():
            raise


def _make_downloader(out_dir: Path) -> Downloader:
    settings = {
        "output": str(out_dir / "{artists} - {title}.{output-ext}"),
        "progress": False,  # ← avoids LiveError in loops
    }
    return Downloader(settings)


def _download_many(songs: Iterable[Song], out_dir: Path) -> List[Path]:
    """
    Core routine shared by all public helpers.
    Returns paths for the songs that actually downloaded (skips None).
    """
    dl = _make_downloader(out_dir)
    results = dl.download_multiple_songs(list(songs))
    return [path for _, path in results if path is not None]


def download_song(url: str, *, out_dir: str | Path = "music") -> Optional[Path]:
    """
    Download a **single track** URL.  Return its path, or None on failure.
    """
    _ensure_spotify_client()
    out_dir = Path(out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    song = Song.from_url(url)
    dl = _make_downloader(out_dir)
    _, path = dl.download_song(song)
    return path


def download_album(url: str, *, out_dir: str | Path = "music") -> List[Path]:
    """
    Download every track from an **album** URL.  Returns list of paths.
    """
    _ensure_spotify_client()
    out_dir = Path(out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    album = Album.from_url(url)  # fetch_songs=True by default
    return _download_many(album.songs, out_dir)


def download_artist(url: str, *, out_dir: str | Path = "music") -> List[Path]:
    """
    Download *all* songs from an **artist** URL (covers the artist’s albums).
    """
    _ensure_spotify_client()
    out_dir = Path(out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    artist = Artist.from_url(url)  # yields songs across albums
    return _download_many(artist.songs, out_dir)


def download_playlist(url: str, *, out_dir: str | Path = "music") -> List[Path]:
    """
    Download every track in a **playlist** URL.  Returns list of paths.
    """
    _ensure_spotify_client()
    out_dir = Path(out_dir).expanduser().resolve()
    out_dir.mkdir(parents=True, exist_ok=True)

    playlist = Playlist.from_url(url)
    return _download_many(playlist.songs, out_dir)
