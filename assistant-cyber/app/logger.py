import logging
import sys

from app.config import get_settings

config = get_settings()

logging.basicConfig(
    level=logging.INFO,
    format=config.LOG_FORMAT,
    datefmt=config.DATE_FORMAT,
    handlers=[logging.StreamHandler(sys.stdout)]
)

def get_logger(name: str) -> logging.Logger:
    return logging.getLogger(name)

