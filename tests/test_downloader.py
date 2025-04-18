from pathlib import Path
from abusify import download_song


def test_download_wrapper(monkeypatch, tmp_path):
    # create dummy mp3 path *inside* tmp_path to mimic spotDL behaviour
    dummy_mp3 = tmp_path / "The Beatles - Come Together.mp3"
    dummy_mp3.touch()

    # capture the settings arg to ensure output template starts with out_dir
    captured = {}

    class _DummyDL:
        def __init__(self, settings):  # noqa: D401, ANN001
            captured["settings"] = settings

        def download_song(self, song):  # noqa: ANN001
            return song, dummy_mp3

    monkeypatch.setattr("abusify.downloader.Downloader", _DummyDL)

    out = download_song("https://open.spotify.com/track/FAKE", out_dir=tmp_path)

    # Assertions
    assert out == dummy_mp3
    assert captured["settings"]["output"].startswith(str(tmp_path))
