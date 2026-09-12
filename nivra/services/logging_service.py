# ---------------------------------------------------------------------------
# Nivra Logging Service
# ---------------------------------------------------------------------------
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


class LoggingService:
    def __init__(self, log_path: str) -> None:
        self.log_path = Path(log_path)
        self.log_path.parent.mkdir(parents=True, exist_ok=True)
        self._logger = logging.getLogger("nivra")
        self._logger.propagate = False
        self._logger.setLevel(logging.DEBUG)

        if not self._logger.handlers:
            handler = RotatingFileHandler(
                self.log_path,
                mode="a",
                maxBytes=2_000_000,
                backupCount=3,
                encoding="utf-8",
            )
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            handler.setFormatter(formatter)
            self._logger.addHandler(handler)


    def info(self, message: str) -> None:
        self._logger.info(message)

    def warning(self, message: str) -> None:
        self._logger.warning(message)

    def error(self, message: str) -> None:
        self._logger.error(message)

    def debug(self, message: str) -> None:
        self._logger.debug(message)