from abusify import resolve, EntityType


def test_resolve_artist_offline(stub_artist_url, beatles_query, expected_beatles_artist_id):
    url = resolve(beatles_query, EntityType.ARTIST)
    assert url.endswith("/" + expected_beatles_artist_id)
