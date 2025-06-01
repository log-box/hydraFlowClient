import logging
import os
from logging.handlers import RotatingFileHandler

from app.config import settings

# Создание каталога, если его нет
os.makedirs(os.path.dirname(settings.LOG_PATH), exist_ok=True)

# Инициализация логгера
logger = logging.getLogger("hydraApp")
logger.setLevel(getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO))
logger.propagate = False

if not logger.handlers:
    # Консоль
    stream_handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
    )
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    # Файл
    file_handler = RotatingFileHandler(
        settings.LOG_PATH,
        maxBytes=5 * 1024 * 1024,
        backupCount=3
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
