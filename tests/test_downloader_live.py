import os
import pytest
from pathlib import Path
from abusify import resolve, EntityType, download_song


@pytest.mark.integration
@pytest.mark.skipif(
    not (os.getenv("SPOTIFY_CLIENT_ID") and os.getenv("SPOTIFY_CLIENT_SECRET")),
    reason="Spotify credentials not configured",
)
def test_download_song_live(tmp_path, come_together_query):
    url = resolve(come_together_query, EntityType.TRACK)
    path = download_song(url, out_dir=tmp_path)
    assert isinstance(path, Path) and path.exists()
