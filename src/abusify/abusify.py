from pathlib import Path
from typing import List, Optional, Union

from .downloader import download_spotify_url
from .organizer import organize_paths
from .spotify import resolve_url, EntityType


class Abusify:
    """
    High‑level OOP wrapper:  resolve → download → organize.
    """

    def __init__(self, out_dir: str | Path = "music"):
        self.out_dir = Path(out_dir).expanduser()

    def download(
        self,
        query: str,
        entity: Optional[EntityType] = None,
    ) -> Union[Path, List[Path]]:  # ← NEW type hint
        """
        Resolve → download → organize.

        Returns
        -------
        Path
            when a single track is downloaded.
        List[Path]
            for album / artist / playlist downloads.
        """
        url = resolve_url(query) if entity is None else resolve_url(query, entity)
        if url is None:
            raise RuntimeError(f"No Spotify result for {query!r}")

        paths = download_spotify_url(url, out_dir=self.out_dir)

        # Normalise to list
        if isinstance(paths, (list, tuple)):
            new_paths = organize_paths(paths, self.out_dir)
            return new_paths
        else:
            new_path = organize_paths([paths], self.out_dir)[0]
            return new_path
