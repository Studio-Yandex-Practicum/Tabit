from typing import Type
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import Table


async def create_associations(
    session: AsyncSession,
    association_model: Type[Table],
    left_ids: list[UUID],
    right_id: int,
    status: bool | None = None,
) -> None:
    """Создание ассоциаций между сущностями.

    Назначение:
        Создает ассоциации между левыми и правыми сущностями через указанную модель.
        Выполняет массовую вставку для повышения производительности.
        Для ассоциаций с проблемами добавляет поле status.

    Параметры:
        session: Асинхронная сессия SQLAlchemy.
        association_model: Модель ассоциативной таблицы.
        left_ids: Список UUID левых сущностей (например, ID участников).
        right_id: ID правой сущности (например, ID встречи или проблемы).
        status: Статус ассоциации (используется только для проблем).

    Возвращаемое значение:
        None
    """
    # Создаем базовые данные для ассоциаций
    base_data = {'right_id': right_id}

    # Добавляем статус, если он указан
    if status is not None:
        base_data['status'] = status

    # Создаем список ассоциаций для массовой вставки
    associations = [{'left_id': left_id, **base_data} for left_id in left_ids]

    # Выполняем массовую вставку
    await session.execute(association_model.__table__.insert(), associations)
