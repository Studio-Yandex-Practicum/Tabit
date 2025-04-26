import sys
import time

from fastapi import Request
from loguru import logger

from src.core.constants import Logging

from .app import settings

# Logger initialization
logger.remove(0)  # Remove old config
logger.add(sys.stderr, level=settings.log_level)  # Settings for console
logger.add(
    Logging.LOG_FILE,
    rotation=Logging.LOG_ROTATION,
    retention=Logging.LOG_RETENTION,
    level=settings.log_level,
)  # Settings for log file

fake_db_logger = logger.bind(name='fake_db_data')
fake_db_logger.remove()
fake_db_logger.add(
    Logging.FAKE_DB_DATA_LOG_FILE, rotation='3 days', retention=Logging.LOG_RETENTION, level='INFO'
)


class LoggingMiddleware:
    """Class for logging all requests as middleware"""

    async def __call__(self, request: Request, call_next, *args, **kwargs):
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        logger.info(
            f'Request: {request.method} {request.url} - {duration:.3f} sec; '
            f'Response: {response.status_code}'
        )
        return response
