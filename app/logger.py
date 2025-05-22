import logging
import os

logger = logging.getLogger("hydraApp")
log_level = os.getenv("LOG_LEVEL", "INFO").upper()
logger.setLevel(getattr(logging, log_level, logging.INFO))
logger.propagate = False

if not logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
