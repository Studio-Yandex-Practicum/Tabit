import time
import sys

from loguru import logger
from fastapi import Request
from .config import settings


LOG_FILE = 'logs/loguru.log'
LOG_ROTATION = '1 day'
LOG_RETENTION = '7 days'

logger.remove(0)
logger.add(sys.stderr, level=settings.log_level)
logger.add(
    LOG_FILE, rotation=LOG_ROTATION, retention=LOG_RETENTION, level=settings.log_level
)


class LoggingMiddleware:
    """Class for logging all requests."""

    async def __call__(self, request: Request, call_next, *args, **kwargs):
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time
        logger.info(f'Request: {request.method} {request.url} - {duration:.3f}')
        logger.info(f'Response: {response.status_code}')
        return response
