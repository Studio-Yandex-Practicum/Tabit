import os
import sys
from pathlib import Path
from re import match

from alembic.script import ScriptDirectory

MIGRATIONS_DIR = Path(__file__).parent.parent / 'alembic' / 'versions'
MIGRATION_RE_ID = r'^(\d+)_'


def next_migration_id() -> str:
    migrations_id = [
        int(matched.group(1))
        for file_name in MIGRATIONS_DIR.iterdir()
        if file_name.is_file() and (matched := match(MIGRATION_RE_ID, file_name.name))
    ]
    next_migration_id = max(migrations_id, default=0) + 1
    return str(next_migration_id).zfill(2)


def get_and_normolize_migration_commit() -> str:
    try:
        commit_index = sys.argv.index('-m') + 1
        return sys.argv[commit_index].replace(' ', '_').lower()
    except (ValueError, IndexError):
        return 'default_migration'  # Или выбрасывать ошибку с просьбой заполнить коммит?


def name_migration(context, revision, directives):
    """Генерирует имя миграции до создания файла."""
    if not directives:
        return

    script = directives[0]
    migration_id = next_migration_id()
    commit_text = get_and_normolize_migration_commit()
    new_filename = f'{migration_id}_{commit_text}.py'
    script.rev_id = migration_id
    script.path = os.path.join(ScriptDirectory.from_config(context.config).versions, new_filename)
