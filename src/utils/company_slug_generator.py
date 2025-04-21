import random

from slugify import slugify
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import company_crud
from src.utils.constants import GENERATED_SLUG_SUFFIX_RANGE, SHORT_SYMBOLS


# TODO: Это используется в тестах. Тут этому не место.
def generate_unique_slug(base_slug: str) -> str:
    """Метод формирования `slug` объектов Company или Department."""
    return base_slug + ''.join(random.choices(SHORT_SYMBOLS, k=GENERATED_SLUG_SUFFIX_RANGE))


# TODO: Просится в метод CRUD для сущностей с полем slug.
async def generate_company_slug(session: AsyncSession, name: str) -> str:
    """
    Генерирует уникальный slug из имени компании. Если сгенерированный slug уже существует в БД,
    добавляет случайное число в конец и повторяет проверку.

    :param session: Асинхронная сессия SQLAlchemy
    :param name: Название компании, из которого создается slug
    :return: Уникальный slug
    """
    new_slug = slugify(name)
    while await company_crud.is_company_slug_exists(session, new_slug):
        new_slug = f'{new_slug}-{random.randint(1000, 9999)}'

    return new_slug
