import logging
import time
from pathlib import Path
from typing import List, Optional, Union
from .exceptions import AbusifyException
from .downloader import download_spotify_url
from .organizer import organize_paths
from .spotify import EntityType, resolve_url

logger = logging.getLogger(__name__)


class Abusify:
    def __init__(self, out_dir: str | Path = "music"):
        self.out_dir = Path(out_dir).expanduser()

    def download(
        self, query: str, entity: Optional[EntityType] = None
    ) -> Union[Path, List[Path], None]:
        """
        Resolve → download → organize, with one 30‑second retry on failures.

        Returns
        -------
        Path           when a single track is fetched.
        List[Path]     for multi‑file entities (album / playlist / artist).
        None           if every attempt ultimately failed.
        """
        logger.info("Starting download for %r (entity=%s)", query, entity)

        # ── Step  1: resolve ─────────────────────────────────────────────
        url = resolve_url(query) if entity is None else resolve_url(query, entity)
        if url is None:
            logger.error("No Spotify match found for %r", query)
            return None
        logger.info("Resolved %r → %s", query, url)

        # ── Step  2: download (+retry) ───────────────────────────────────
        paths: List[Path] = []
        failed: List[str] = []

        try:
            paths.extend(download_spotify_url(url, out_dir=self.out_dir))
        except AbusifyException as exc:
            logger.warning("First attempt failed for %s: %s", exc.url, exc)
            failed.append(exc.url)

        if failed:
            logger.warning("Sleeping 30 s, then retrying %d failed URL(s)", len(failed))
            time.sleep(30)
            for u in failed:
                try:
                    paths.extend(download_spotify_url(u, out_dir=self.out_dir))
                    logger.info("Retry succeeded for %s", u)
                except AbusifyException as exc:  # still failing
                    logger.error("Retry failed for %s: %s", exc.url, exc)

        # ── Step  3: organize ────────────────────────────────────────────
        organized = organize_paths(paths, self.out_dir)
        logger.info("Finished: %d file(s) organized", len(organized))
        return organized[0] if len(organized) == 1 else organized
