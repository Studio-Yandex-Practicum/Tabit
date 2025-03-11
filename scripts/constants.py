from dataclasses import dataclass
from pathlib import Path
from re import compile

# Константы для migration_auto_naming.py
MIGRATIONS_DIR = Path(__file__).parent.parent / 'alembic' / 'versions'
MIGRATION_RE_ID = compile(r'^(\d+)_')


# Константы для pre_start.py
@dataclass
class TextScripts:
    """Текстовые переменные файла scripts.py."""

    DESCRIPTION: str = """
        Запустит проект с помощью uvicorn.

        флаги --reload, --host, --port опциональные и могут указываться одновременно.\n
        фдаг --create-superuser - создаст первого суперпользователя согласно данным в .env без
        последующего запуска проекта.
        """
    LOGGER: str = 'Starting uvicorn server...'
    RELOAD: str = 'Запустит uvicorn с флагом --reload'
    HOST: str = 'Указать хост при запуске.'
    PORT: str = 'Указать порт при запуске.'
    CREATE: str = 'Создать суперпользователя'
