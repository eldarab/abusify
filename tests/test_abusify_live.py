import os

import pytest

from abusify import Abusify, EntityType


@pytest.mark.integration
@pytest.mark.skipif(
    not (os.getenv("SPOTIFY_CLIENT_ID") and os.getenv("SPOTIFY_CLIENT_SECRET")),
    reason="Spotify credentials not configured",
)
def test_download_track(tmp_path):
    ab = Abusify(out_dir=tmp_path)
    new_path = ab.download("Come Together", EntityType.TRACK)
    assert new_path.exists()


@pytest.mark.integration
@pytest.mark.skipif(
    not (os.getenv("SPOTIFY_CLIENT_ID") and os.getenv("SPOTIFY_CLIENT_SECRET")),
    reason="Spotify credentials not configured",
)
def test_download_album(tmp_path):
    ab = Abusify(out_dir=tmp_path)
    new_paths = ab.download("Abbey Road", EntityType.ALBUM)
    assert len(new_paths) > 0 and all(p.exists() for p in new_paths)
