import logging
from pathlib import Path


def get_logger(name: str = "crop_pipeline", level: int = logging.INFO) -> logging.Logger:
	logger = logging.getLogger(name)
	if not logger.handlers:
		handler = logging.StreamHandler()
		handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
		logger.addHandler(handler)
	logger.setLevel(level)
	return logger


def configure_logging(level: str = "INFO", log_file: str | Path | None = None) -> logging.Logger:
	logger = get_logger(level=getattr(logging, level.upper(), logging.INFO))
	if log_file and not any(isinstance(handler, logging.FileHandler) for handler in logger.handlers):
		path = Path(log_file)
		path.parent.mkdir(parents=True, exist_ok=True)
		handler = logging.FileHandler(path, encoding="utf-8")
		handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s %(message)s"))
		logger.addHandler(handler)
	return logger
