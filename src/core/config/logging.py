import sys
import time

from fastapi import Request
from loguru import logger

from src.core.config.app import settings
from src.core.constants.logging import LOG_FILE, LOG_RETENTION, LOG_ROTATION

# Logger initialization
logger.remove(0)  # Remove old config
logger.add(sys.stderr, level=settings.log_level)  # Settings for console
logger.add(
    LOG_FILE, rotation=LOG_ROTATION, retention=LOG_RETENTION, level=settings.log_level
)  # Settings for log file


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
