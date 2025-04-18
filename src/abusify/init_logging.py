from logging.config import dictConfig
from pathlib import Path


def configure_logging(
        *,
        logs_dir: Path = Path("logs"),
        level: str = "INFO",
        log_filename: str = "app.log",
) -> None:
    """
    Prepare log directory, and configure root logger with console
    and file handlers via dictConfig.
    """
    # ensure directory exists
    logs_dir.mkdir(parents=True, exist_ok=True)

    dictConfig({
        "version": 1,
        "disable_existing_loggers": True,
        "formatters": {
            "standard": {
                "format": "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
            }
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": level,
                "formatter": "standard",
                "stream": "ext://sys.stderr",
            },
            "file": {
                "class": "logging.FileHandler",
                "level": level,
                "formatter": "standard",
                "filename": str(logs_dir / log_filename),
                "encoding": "utf-8",
            },
        },
        "root": {
            "level": level,
            "handlers": ["console", "file"],
        },
    })
