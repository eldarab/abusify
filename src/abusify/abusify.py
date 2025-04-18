from pathlib import Path
from typing import Optional, List, Union

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
    ) -> Union[Path, List[Path]]:
        """
        1. Resolve query to a Spotify URL
        2. Download audio via spotDL
        3. Organize files into artist/album folders
        """
        url = resolve_url(query) if entity is None else resolve_url(query, entity)
        if url is None:
            raise RuntimeError(f"No Spotify result for {query!r}")

        paths = download_spotify_url(url, out_dir=self.out_dir)
        # normalize to list
        if isinstance(paths, (list, tuple)):
            organize_paths(paths, self.out_dir)
        else:
            organize_paths([paths], self.out_dir)
        return paths
