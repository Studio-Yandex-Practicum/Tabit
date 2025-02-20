from src.api.v1.auth.managers import UserManager, get_user_db
from src.users.models.models import UserTabit

PATRONYMICS = [
    'Александрович',
    'Алексеевич',
    'Дмитриевич',
    'Евгеньевич',
    'Иванович',
    'Петрович',
    'Сергеевич',
    'Николаевич',
]


async def get_user_manager_instance(session) -> UserManager:
    """Создаёт UserManager внутри активной сессии."""
    async for user_db in get_user_db(session):  # anext() не пропускает ruff
        return UserManager(user_db)
    raise ValueError('get_user_db(session) не вернул объект')


print(f'Все поля: {[column.name for column in UserTabit.__table__.columns]}')

unique_fields = [column.name for column in UserTabit.__table__.columns if column.unique]
print(f'Уникальные поля: {unique_fields}')
