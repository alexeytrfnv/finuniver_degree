import logging
import sys

from app.config import get_settings

settings = get_settings()

logging.basicConfig(
    level=logging.INFO,
    format=settings.LOG_FORMAT,
    datefmt=settings.DATE_FORMAT,
    handlers=[logging.StreamHandler(sys.stdout)]
)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)
