from __future__ import annotations

import logging
import os
from enum import Enum

import spotipy
from dotenv import load_dotenv
from spotipy.oauth2 import SpotifyClientCredentials

# Load environment variables for SPOTIFY_CLIENT_ID/SECRET
load_dotenv()

# Module-level logger
logger = logging.getLogger(__name__)


class EntityType(str, Enum):
    """Allowed Spotify entity categories."""

    ARTIST = "artist"
    ALBUM = "album"
    TRACK = "track"
    PLAYLIST = "playlist"


def _client() -> spotipy.Spotify:
    cid = os.getenv("SPOTIFY_CLIENT_ID")
    secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    if not (cid and secret):
        logger.error("Missing Spotify credentials (SPOTIFY_CLIENT_ID and SPOTIFY_CLIENT_SECRET)")
        raise RuntimeError(
            "Missing Spotify credentials. Define SPOTIFY_CLIENT_ID and "
            "SPOTIFY_CLIENT_SECRET in the environment or a .env file."
        )
    logger.info("Creating Spotify client with provided credentials.")
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
        Restrict the search to a single category. If ``None`` (default),
        searches artists → albums → tracks → playlists in that order.

    Returns
    -------
    str | None
        ``https://open.spotify.com/<kind>/<id>`` if a match is found,
        otherwise ``None``.
    """
    logger.info("Resolving Spotify URL for query=%r, entity_type=%s", query, entity_type)
    sp = _client()

    # Determine search scope
    if entity_type:
        search_scope = entity_type.value
        preferred = (entity_type.value,)
        logger.debug("Restricted to entity type: %s", entity_type.value)
    else:
        search_scope = ",".join(e.value for e in EntityType)
        preferred = tuple(e.value for e in EntityType)
        logger.debug("Searching all entity types: %s", search_scope)

    try:
        results = sp.search(q=query, type=search_scope, limit=1)
        logger.info("Search API returned results for query %r", query)
    except Exception as e:
        logger.error("Spotify search failed for query %r: %s", query, e)
        raise

    # Look for preferred kind in results
    for kind in preferred:
        items = results.get(f"{kind}s", {}).get("items", [])
        if items:
            uri = items[0]["uri"]  # e.g. spotify:artist:3WrFJ7...
            _, _, spotify_id = uri.split(":")
            url = f"https://open.spotify.com/{kind}/{spotify_id}"
            logger.info("Resolved %r to URL: %s", query, url)
            return url

    logger.warning("No Spotify match found for query=%r, entity_type=%s", query, entity_type)
    return None
