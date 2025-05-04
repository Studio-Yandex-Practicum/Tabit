import asyncio

import uvicorn
from click import command, option

from scripts.constants import TextScriptsConstants
from src.core.config.logging import logger
from src.core.database.init_db import create_first_superuser


@command(help=TextScriptsConstants.DESCRIPTION)
@option('--reload', '-r', is_flag=True, default=False, help=TextScriptsConstants.RELOAD)
@option('--host', '-h', default='127.0.0.1', show_default=True, help=TextScriptsConstants.HOST)
@option('--port', '-p', default=8000, show_default=True, help=TextScriptsConstants.PORT)
@option('--create-superuser', '-c', is_flag=True, default=False, help=TextScriptsConstants.CREATE)
def application_management(reload, create_superuser, host, port):
    """
    Функция расширит возможности запуска приложения через консольные команды.

    reload (для флага --reload) - запустит uvicorn с флагом --reload
    host (для флага --host) - для указания хоста при запуске.
    port (для флага --port) - для указания порта при запуске.
    create_superuser (для флага --create-superuser) - не запускает проект, вместо этого делает
        первую запись в БД с данными суперпользователя, указанных в .env.
    """
    if create_superuser:
        asyncio.run(create_first_superuser())
    else:
        logger.info(TextScriptsConstants.LOGGER)
        uvicorn.run('main:app_v1', reload=reload, host=host, port=port)
