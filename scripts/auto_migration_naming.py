"""
Функция name_migration скрипта интегрирована в функцию alembic/env.py: do_run_migrations

Скрипт при выполнении стандартной команды создания миграции выполняет следующие шаги:
    1. ID: Собирает названия файлов миграции внутри папки alembic/revisons/ , извлекает число
    обозначающее id миграции, доавбляя к нему единицу. Если же папка пуста, за ID берется 01.
    2. commit: Введеная команда на создание миграции парсится, из неё достается строка
    после флага -m, содержащая коммит к миграции.
    3. Для создаваемой миграции создается имя в формате <ID>_<commit>.py

    Пример:
        если в папке с миграциями есть уже 2 миграции с id 01 и 02 -
        команда alembic revision --autogenerate -m 'Тестовая миграция' создаст миграцию
        03_тестовая_миграция.py.
"""

import os
import sys
from pathlib import Path
from re import match

from alembic.script import ScriptDirectory

MIGRATIONS_DIR = Path(__file__).parent.parent / 'alembic' / 'versions'
if not MIGRATIONS_DIR.exists():
    MIGRATIONS_DIR.mkdir(parents=True, exist_ok=True)

MIGRATION_RE_ID = r'^(\d+)_'


def next_migration_id() -> str:
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


def get_and_normolize_migration_commit() -> str:
    """
    Функция вытаскивает из аргументов команды коммит к миграции приводя к стандартному виду.

    Проверка ошибок:
        Если флаг -m не был прописан, возникает ошибка ValueError.
        Если флаг -m присутствует, но коммит неб ыл заполнен, возникает ошибка IndexError.
        В обоих случаях функция возвращает для создаваемого коммита строку 'default_migration'.
    """
    try:
        commit_index = sys.argv.index('-m') + 1
        return sys.argv[commit_index].replace(' ', '_').lower()
    except (ValueError, IndexError):
        return 'default_migration'  # Или выбрасывать ошибку с просьбой заполнить коммит?


def name_migration(context, revision, directives):
    """
    Автоматически задаёт имя файлу миграции перед созданием.
        1. Определяет следующий id миграции.
        2. Получает описание миграции из аргумента `-m` и форматирует его.
        3. Формирует имя файла в формате `<id>_<коммит>.py`.
        4. Подменяет `rev_id` миграции, чтобы rev_id миграции совпадал с id в названии файла.
        5. Обновляет путь файла миграции, чтобы Alembic создал его сразу с нужным именем.

    Аргументы:
        context (MigrationContext): Контекст выполнения Alembic.
        revision (Optional[str]): Уникальный идентификатор ревизии.
        derictives: список с объектом MigrationScript, представляющий новую миграцию, содержит:
            Путь к файлу миграции.
            id ревизии (rev_id).
    """
    if not directives or not directives[0]:
        return

    migration_script = directives[0]
    migration_id = next_migration_id()
    commit_text = get_and_normolize_migration_commit()
    new_filename = f'{migration_id}_{commit_text}.py'
    migration_script.rev_id = migration_id
    migration_script.path = os.path.join(
        ScriptDirectory.from_config(context.config).versions, new_filename
    )
