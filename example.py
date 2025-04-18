from pathlib import Path

from dotenv import load_dotenv

from abusify import Abusify, EntityType, configure_logging

configure_logging(
    logs_dir=Path("D:/abusify/logs"),
    level="INFO",
    log_filename="abusify.log"
)

load_dotenv()


def main() -> None:
    ab = Abusify("D:/abusify")
    ab.download("שיר אהבה בדואי צליל מכוון", entity=EntityType.TRACK)


if __name__ == "__main__":
    main()
