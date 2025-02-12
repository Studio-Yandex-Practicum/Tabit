import os
import sys
from pathlib import Path
from re import match

from alembic.script import write_hooks

MIGRATIONS_DIR = Path(__file__).parent.parent / 'alembic' / 'versions'
MIGRATION_RE_ID = r'(^\d+)'


def next_migration_id() -> str:
    migrations_id = [
        matched.group(1)
        for file_name in MIGRATIONS_DIR.iterdir()
        if file_name.is_file() and (matched := match(MIGRATION_RE_ID, file_name.name))
    ]
    next_migration_id = int(max(migrations_id, default=0)) + 1
    return str(next_migration_id).zfill(2)


def get_and_normolize_migration_commit() -> str:
    try:
        commit_index = sys.argv.index('-m') + 1
        return sys.argv[commit_index].replace(' ', '_').lower()
    except (ValueError, IndexError):
        return 'default_migration'  # Или выбрасывать ошибку с просьбой заполнить коммит?


@write_hooks.register('rename_migration')
def rename_migration(filename, options):
    migration_dir = os.path.dirname(filename)
    migration_id = next_migration_id()
    migration_commit = get_and_normolize_migration_commit()
    migration_name = f'{migration_id}_{migration_commit}.py'
    migration_new_filename = os.path.join(migration_dir, migration_name)
    os.rename(filename, migration_new_filename)


print(next_migration_id())
