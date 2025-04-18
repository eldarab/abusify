from logging.config import dictConfig
from pathlib import Path


def configure_logging(
        *,
        logs_dir: Path = Path("logs"),
        level: str = "INFO",
        log_filename: str = "abusify.log",
) -> None:
    """
    Prepare log directory, and configure root logger with console
    and file handlers via dictConfig.
    """
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
                "stream": "ext://sys.stdout",
            },
            "file": {
                "class": "logging.FileHandler",
                "level": level,
                "formatter": "standard",
                "filename": str(logs_dir / log_filename),
                "encoding": "utf-8",
            },
        },
        "loggers": {
            "abusify": {
                "handlers": ["console", "file"],
                "level": level,
                "propagate": False
            }
        },
        "root": {
            "level": level,
            "handlers": ["console", "file"],
        },
    })
