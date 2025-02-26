import sys
import time

from fastapi import Request
from loguru import logger

from .config import settings

LOG_FILE = 'logs/tabit.log'
FAKE_DB_DATA_LOG_FILE = 'logs/fake_db_data.log'
LOG_ROTATION = '1 day'
LOG_RETENTION = '7 days'

# Logger initialization
logger.remove(0)  # Remove old config
logger.add(sys.stderr, level=settings.log_level)  # Settings for console
logger.add(
    LOG_FILE, rotation=LOG_ROTATION, retention=LOG_RETENTION, level=settings.log_level
)  # Settings for log file

fake_db_logger = logger.bind(name='fake_db_data')
fake_db_logger.remove()
fake_db_logger.add(FAKE_DB_DATA_LOG_FILE, rotation='3 days', retention=LOG_RETENTION, level='INFO')


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
