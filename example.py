import logging
from pathlib import Path

from dotenv import load_dotenv

from abusify import Abusify, EntityType

# ─── Logging setup ─────────────────────────────────────────────────────────────
# 1. Prepare log directory
logs_dir = Path("D:/abusify/logs")
logs_dir.mkdir(parents=True, exist_ok=True)

# 2. Get root logger and clear existing handlers
logger = logging.getLogger()
logger.handlers.clear()
logger.setLevel(logging.INFO)

# 3. Console handler
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(
    logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
)
logger.addHandler(ch)

# 4. File handler
fh = logging.FileHandler(logs_dir / "abusify.log", encoding="utf-8")
fh.setLevel(logging.INFO)
fh.setFormatter(
    logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")
)
logger.addHandler(fh)
# ────────────────────────────────────────────────────────────────────────────────

load_dotenv()


def main() -> None:
    ab = Abusify("D:/abusify")
    ab.download("שיר אהבה בדואי צליל מכוון", entity=EntityType.TRACK)


if __name__ == "__main__":
    main()
