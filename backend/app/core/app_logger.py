from loguru import logger
import sys
import os
from app.config import settings
import tempfile
LOG_PATH = os.getenv("LOG_PATH", os.path.join(tempfile.gettempdir(), "app.log"))
LOG_LEVEL = settings.LOG_LEVEL

logger.remove()
logger.add(sys.stderr, level=LOG_LEVEL)

logger.add(
    LOG_PATH,
    rotation="10 MB",
    retention="7 days",
    compression="zip",
    level=LOG_LEVEL,
    backtrace=True,
    diagnose=True,
)