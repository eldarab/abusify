from __future__ import annotations

import os
from enum import Enum

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials

load_dotenv()  # reads SPOTIFY_CLIENT_ID / SECRET from .env or environment


class EntityType(str, Enum):
    """Allowed Spotify entity categories."""

    ARTIST = "artist"
    ALBUM = "album"
    TRACK = "track"
    PLAYLIST = "playlist"


def _client() -> spotipy.Spotify:
    cid, secret = os.getenv("SPOTIFY_CLIENT_ID"), os.getenv("SPOTIFY_CLIENT_SECRET")
    if not (cid and secret):
        raise RuntimeError(
            "Missing Spotify credentials.  Define SPOTIFY_CLIENT_ID and "
            "SPOTIFY_CLIENT_SECRET in the environment or a .env file."
        )
    return spotipy.Spotify(
        auth_manager=SpotifyClientCredentials(client_id=cid, client_secret=secret)
    )


def resolve_url(
    query: str,
    entity_type: EntityType | None = None,
) -> str | None:
    """
    Resolve *query* to the canonical Spotify HTTPS URL.

    Parameters
    ----------
    query : str
        Anything Spotify can understand (e.g. band name, track title, raw URI).
    entity_type : EntityType | None, optional
        Restrict the search to a single category.  If ``None`` (default),
        searches artists → albums → tracks → playlists in that order.

    Returns
    -------
    str | None
        ``https://open.spotify.com/<kind>/<id>`` if a match is found,
        otherwise ``None``.
    """
    sp = _client()

    if entity_type:
        search_scope = entity_type.value
        preferred = (entity_type.value,)
    else:
        search_scope = ",".join(e.value for e in EntityType)
        preferred = ("artist", "album", "track", "playlist")

    results = sp.search(q=query, type=search_scope, limit=1)

    for kind in preferred:
        items = results.get(f"{kind}s", {}).get("items", [])
        if items:
            uri = items[0]["uri"]  # e.g. spotify:artist:3WrFJ7...
            _, _, spotify_id = uri.split(":")
            return f"https://open.spotify.com/{kind}/{spotify_id}"

    return None
