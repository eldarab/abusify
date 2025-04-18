from pathlib import Path

import pytest


@pytest.fixture
def temp_music_dir(tmp_path_factory) -> Path:
    """
    Unique temp directory per test for download output.
    """
    return tmp_path_factory.mktemp("music")


@pytest.fixture
def beatles_query() -> str:
    """A canonical search term we’ll reuse."""
    return "the beatles"


@pytest.fixture
def expected_beatles_artist_id() -> str:
    # Stable Spotify ID for “The Beatles”
    return "3WrFJ7ztbogyGnTHbHJFl2"


@pytest.fixture
def come_together_query() -> str:
    """Canonical track query used in live‑download tests."""
    return "Come Together"


# ---------- stubbing fixture for UNIT tests ----------
@pytest.fixture
def stub_artist_url(monkeypatch, expected_beatles_artist_id):
    """
    Replace the internal Spotipy client with a dummy that returns exactly
    one artist hit.  Used by offline unit tests.
    """

    class _Dummy:
        def search(self, q, type, limit):
            uri = f"spotify:artist:{expected_beatles_artist_id}"
            return {
                "artists": {"items": [{"uri": uri}]},
                "albums": {},
                "tracks": {},
                "playlists": {},
            }

    from abusify import spotify

    monkeypatch.setattr(spotify, "_client", lambda: _Dummy())
