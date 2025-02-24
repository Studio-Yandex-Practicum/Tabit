"""
Функция name_migration скрипта интегрирована в функцию alembic/env.py: do_run_migrations

Скрипт при выполнении стандартной команды создания миграции выполняет следующие шаги:
    1. ID: Собирает названия файлов миграции внутри папки alembic/revisons/ , извлекает число
    обозначающее id миграции, доавбляя к нему единицу. Если же папка пуста, за ID берется 01.
    3. Для создаваемой миграции создается имя в формате <ID>_<commit>.py, если commit был передан,
    или <ID>_no_discription_please_rename.py если commit передан не был.

    Пример:
        если в папке с миграциями есть уже 2 миграции с id 01 и 02 -
        команда alembic revision --autogenerate -m 'Тестовая миграция' создаст миграцию
        03_тестовая_миграция.py.
"""

from pathlib import Path
from re import match

MIGRATIONS_DIR = Path(__file__).parent.parent / 'alembic' / 'versions'
if not MIGRATIONS_DIR.exists():
    MIGRATIONS_DIR.mkdir(parents=True, exist_ok=True)

MIGRATION_RE_ID = r'^(\d+)_'


def get_next_migration_id() -> str:
    """
    Функция возвращает идентификатор для создаваемой миграции в 2 шага:
       1. Собирает имена файлов существующих миграций и создает список из их идентификаторов
       с помощью регулярного выражения.
       2. Вычисляет максимальный из идентификаторов, увличивает на единицу и дополняет нулями
       слева до двух символов, если необходимо.
    """
    migrations_id = [
        int(matched.group(1))
        for file_object in MIGRATIONS_DIR.iterdir()
        if file_object.is_file() and (matched := match(MIGRATION_RE_ID, file_object.name))
    ]
    next_migration_id = max(migrations_id, default=0) + 1
    return str(next_migration_id).zfill(2)


def generate_migration_name(context, revision, directives):
    """
    Автоматически задаёт имя файлу миграции перед созданием.

    1. Определяет следующий id миграции.
    2. Получает commit миграции из аргумента '-m'.
    3. Формирует имя файла в формате <id>_<commit>.py.
       - 'id' берётся из атрибута 'rev_id' миграции.
       - 'commit' — из атрибута 'message'.
    4. Подменяет 'rev_id' миграции, который Alembic подставляет в название файла.
    5. Если 'message' не был передан или пустой, подставляет дефолтное значение.

    Аргументы:
        context: Контекст выполнения Alembic.
        revision: Уникальный идентификатор ревизии.
        directives: список с объектом MigrationScript, представляющий новую миграцию.

    Атрибуты 'directives', используемые в функции:
        rev_id (str): ID миграции.
        message (str): commit миграции переданный при вводе команды.
    """
    if not directives or not directives[0]:
        return

    migration_script = directives[0]
    migration_id = get_next_migration_id()
    migration_script.rev_id = migration_id
    if not migration_script.message:
        migration_script.message = 'no_discription_please_rename'
