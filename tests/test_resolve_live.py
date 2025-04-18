import os
import pytest
from abusify import resolve, EntityType


@pytest.mark.integration
@pytest.mark.skipif(
    not (os.getenv("SPOTIFY_CLIENT_ID") and os.getenv("SPOTIFY_CLIENT_SECRET")),
    reason="Spotify credentials not configured",
)
def test_resolve_artist_live(beatles_query, expected_beatles_artist_id):
    """
    Hits the real Spotify Web API.  Requires valid credentials in .env or env.
    """
    url = resolve(beatles_query, EntityType.ARTIST)
    assert url.endswith("/" + expected_beatles_artist_id)
