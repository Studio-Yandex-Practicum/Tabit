"""
Модуль с универсальным базовым классом для CRUD операций.

Содержит:
- Определения типов: ModelType, CreateSchemaType, UpdateSchemaType.
- Константу DEFAULT_AUTO_COMMIT для управления автокоммитом.
- Функции для фильтрации и сортировки запросов:
  apply_filters, apply_order_by.
- Класс CRUDBase с асинхронными методами get, get_or_404, get_multi,
  create, update и delete.
"""

from typing import TypeVar, Generic, Type, Optional, List, Any
from uuid import UUID

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError
from sqlalchemy.sql import Select

from .constants import DEFAULT_AUTO_COMMIT, DEFAULT_SKIP, DEFAULT_LIMIT


ModelType = TypeVar('ModelType')
CreateSchemaType = TypeVar('CreateSchemaType')
UpdateSchemaType = TypeVar('UpdateSchemaType')


def apply_filters(query: Select, model: Type[ModelType], filters: dict[str, Any]) -> Select:
    """
    "Добавляет простые условия равенства (WHERE) к запросу на основе словаря.

    Назначение:
        Фильтрует результат по полям модели. Если поля нет в модели,
        он игнорируется.
    Параметры:
        query: Исходный SQLAlchemy Select.
        model: Класс модели для запроса.
        filters: Словарь вида {имя_поля: значение}.
    Возвращаемое значение:
        Обновлённый запрос c наложенными условиями.
    Пример:
        filters = {'status': 'active', 'user_id': 10}
        query = select(User)
        query = apply_filters(query, User, filters)
        # WHERE user.status='active' AND user.user_id=10
    """
    # TODO: Добавить поддержку операций >, <, LIKE, IN, BETWEEN и т.д.
    for field_name, field_value in filters.items():
        column = getattr(model, field_name, None)
        if column is not None:
            query = query.where(column == field_value)
    return query


def apply_order_by(query: Select, model: Type[ModelType], order_by: list[str]) -> Select:
    """
    "Добавляет сортировку (ORDER BY) к запросу, поддерживая '-' для убывания.

    Назначение:
        Упорядочивает результат по указанным полям. Если поле начинается
        с '-', применяется сортировка по убыванию. Если поля нет в модели,
        он игнорируется.
    Параметры:
        query: Исходный SQLAlchemy Select.
        model: Класс модели для запроса.
        order_by: Список имён полей; '-' в начале означает DESC.
    Возвращаемое значение:
        Обновлённый запрос с сортировкой.
    Пример:
        order = ['-created_at', 'id']
        query = select(User)
        query = apply_order_by(query, User, order)
        # ORDER BY user.created_at DESC, user.id ASC
    """
    for field_name in order_by:
        desc = field_name.startswith('-')
        actual_field_name = field_name[1:] if desc else field_name
        column = getattr(model, actual_field_name, None)
        if column is not None:
            query = query.order_by(column.desc() if desc else column.asc())
    return query


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    "Универсальный базовый класс для CRUD операций.
    """

    def __init__(self, model: Type[ModelType]):
        """
        "Инициализирует CRUD-класс с указанной моделью.

        Параметры:
            model: SQLAlchemy-модель (класс), связанный с таблицей в БД.
        """
        self.model = model

    async def get(self, session: AsyncSession, obj_id: int | UUID) -> Optional[ModelType]:
        """
        "Получает объект по ID (int или UUID).

        Возвращает объект модели или None, если он не найден.
        """
        result = await session.execute(select(self.model).where(self.model.id == obj_id))
        return result.scalars().first()

    async def get_or_404(self, session: AsyncSession, obj_id: int | UUID) -> ModelType:
        """
        "Получает объект по ID или выбрасывает 404-ошибку.

        Возвращает объект или HTTPException(404), если не найден.
        """
        obj = await self.get(session, obj_id)
        if not obj:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Объект не найден')
        return obj

    async def get_multi(
        self,
        session: AsyncSession,
        skip: int = DEFAULT_SKIP,
        limit: int = DEFAULT_LIMIT,
        filters: dict[str, Any] | None = None,
        order_by: list[str] | None = None,
    ) -> List[ModelType]:
        """
        "Получает список объектов с пагинацией, фильтрацией и сортировкой.

        Назначение:
            Извлекает из БД ограниченный набор объектов, пропуская skip.
            При filters накладывается WHERE (apply_filters),
            при order_by — ORDER BY (apply_order_by).
        Параметры:
            session: Асинхронная сессия SQLAlchemy.
            skip: Число записей для пропуска.
            limit: Максимальное число записей.
            filters: Словарь {имя_поля: значение} для фильтрации.
            order_by: Список полей для сортировки; '-' в начале для убывания.
        Возвращаемое значение:
            Список объектов модели.
        Пример:
            filters = {'status': 'active'}
            order = ['-created_at', 'id']
            items = await crud_user.get_multi(
                session=session,
                skip=0,
                limit=10,
                filters=filters,
                order_by=order
            )
        """
        query = select(self.model)

        if filters:
            query = apply_filters(query, self.model, filters)

        if order_by:
            query = apply_order_by(query, self.model, order_by)

        query = query.offset(skip).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()

    async def create(
        self,
        session: AsyncSession,
        obj_in: CreateSchemaType,
        auto_commit: bool = DEFAULT_AUTO_COMMIT,
    ) -> ModelType:
        """
        "Создаёт новый объект в БД.

        При нарушении уникальности выбрасывает 400-ошибку.
        """
        obj_data = obj_in.dict()
        db_obj = self.model(**obj_data)

        session.add(db_obj)
        try:
            if auto_commit:
                await session.commit()
                await session.refresh(db_obj)
        except IntegrityError:
            await session.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail='Ошибка уникальности. Такой объект уже существует.',
            )
        return db_obj

    async def update(
        self,
        session: AsyncSession,
        db_obj: ModelType,
        obj_in: UpdateSchemaType,
        auto_commit: bool = DEFAULT_AUTO_COMMIT,
    ) -> ModelType:
        """
        "Обновляет существующий объект (частичное обновление).

        Принимает объект и данные (Pydantic) для обновления.
        """
        obj_data = jsonable_encoder(db_obj)
        update_data = obj_in.dict(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        session.add(db_obj)
        if auto_commit:
            await session.commit()
            await session.refresh(db_obj)
        return db_obj

    async def delete(
        self, session: AsyncSession, obj_id: int | UUID, auto_commit: bool = DEFAULT_AUTO_COMMIT
    ) -> None:
        """
        "Удаляет объект по ID.

        При отсутствии объекта выбрасывает 404-ошибку.
        """
        obj = await self.get_or_404(session, obj_id)
        await session.delete(obj)
        if auto_commit:
            await session.commit()
