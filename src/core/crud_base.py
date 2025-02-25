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

from http import HTTPStatus
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from uuid import UUID

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi_users import BaseUserManager, exceptions, models, schemas
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from starlette.requests import Request

from src.core.config.logging import logger
from src.core.constants.common import (
    DEFAULT_AUTO_COMMIT,
    DEFAULT_LIMIT,
    DEFAULT_SKIP,
    TEXT_ERROR_EXISTS_EMAIL,
    TEXT_ERROR_INVALID_PASSWORD,
    TEXT_ERROR_NOT_FOUND,
    TEXT_ERROR_SERVER_CREATE,
    TEXT_ERROR_SERVER_CREATE_LOG,
    TEXT_ERROR_SERVER_DELETE,
    TEXT_ERROR_SERVER_DELETE_LOG,
    TEXT_ERROR_SERVER_UPDATE,
    TEXT_ERROR_SERVER_UPDATE_LOG,
    TEXT_ERROR_UNIQUE,
    TEXT_ERROR_UNIQUE_CREATE_LOG,
    TEXT_ERROR_UNIQUE_UPDATE_LOG,
)

ModelType = TypeVar('ModelType')
CreateSchemaType = TypeVar('CreateSchemaType')
UpdateSchemaType = TypeVar('UpdateSchemaType')


class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    """
    Универсальный базовый класс для CRUD операций.
    """

    def __init__(self, model: Type[ModelType]):
        """
        Инициализирует CRUD-класс с указанной моделью.

        Параметры:
            model: SQLAlchemy-модель (класс), связанный с таблицей в БД.
        """
        self.model = model

    async def get(self, session: AsyncSession, obj_id: int | str | UUID) -> Optional[ModelType]:
        """
        Получает объект по ID (int, str или UUID).

        Возвращает объект модели или None, если он не найден.
        """
        result = await session.execute(select(self.model).where(self.model.id == obj_id))
        return result.scalars().first()

    async def get_or_404(
        self, session: AsyncSession, obj_id: int | UUID, message: str = TEXT_ERROR_NOT_FOUND
    ) -> ModelType:
        """
        Получает объект по ID или выбрасывает 404-ошибку.

        Возвращает объект или HTTPException(404), если не найден.
        """
        obj = await self.get(session, obj_id)
        if not obj:
            # TODO: Здесь и далее по коду избавиться от литералов, упаковать всё в константы.
            # Константы хранить в отдельном файле.
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
        return obj

    async def get_by_slug(
        self,
        session: AsyncSession,
        obj_slug: str,
        raise_404: bool = False,
        message: str = TEXT_ERROR_NOT_FOUND,
    ) -> Optional[ModelType]:
        """
        Получает объект по полю slug.

        Возвращает объект модели или None, если он не найден.
        Если параметр raise_404 = True, тогда выбрасывает 404-ошибку, если не найден.
        """
        result = await session.execute(select(self.model).where(self.model.slug == obj_slug))
        obj_model = result.scalars().first()
        if not result and raise_404:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
        return obj_model

    async def get_multi(
        self,
        session: AsyncSession,
        skip: int = DEFAULT_SKIP,
        limit: int = DEFAULT_LIMIT,
        filters: Optional[Dict[str, Any]] = None,
        order_by: list[str] | None = None,
    ) -> List[ModelType]:
        """
        Получает список объектов с пагинацией, фильтрацией и сортировкой.

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
            valid_filters = {key: value for key, value in filters.items() if value is not None}

            if valid_filters:
                query = self._apply_filters(query, valid_filters)

        if order_by:
            query = self._apply_order_by(query, order_by)

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
        Создаёт новый объект в БД.

        При нарушении уникальности выбрасывает 400-ошибку.
        """
        # TODO: Добавить возможность автозаполнение поля owner у модели.
        obj_data = obj_in.model_dump()
        db_obj = self.model(**obj_data)
        try:
            session.add(db_obj)
            if auto_commit:
                await session.commit()
                await session.refresh(db_obj)
        except IntegrityError as e:
            # TODO: Сюда попадают не только ошибки уникальности, но и не правильно оформленные
            # поля, надо переделать на более универсальный ответ.
            await session.rollback()
            logger.error(f'{TEXT_ERROR_UNIQUE_CREATE_LOG} {self.model.__name__}: {e}')
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=TEXT_ERROR_UNIQUE,
            )
        except Exception as e:
            await session.rollback()
            logger.error(f'{TEXT_ERROR_SERVER_CREATE_LOG} {self.model.__name__}: {e}')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=TEXT_ERROR_SERVER_CREATE,
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
        update_data = obj_in.model_dump(exclude_unset=True)

        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])

        try:
            session.add(db_obj)
            if auto_commit:
                await session.commit()
                await session.refresh(db_obj)
        except IntegrityError as e:
            await session.rollback()
            logger.error(f'{TEXT_ERROR_UNIQUE_UPDATE_LOG} {self.model.__name__}: {e}')
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=TEXT_ERROR_UNIQUE,
            )
        except Exception as e:
            await session.rollback()
            logger.error(f'{TEXT_ERROR_SERVER_UPDATE_LOG} {self.model.__name__}: {e}')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=TEXT_ERROR_SERVER_UPDATE,
            )
        return db_obj

    async def remove(
        self, session: AsyncSession, db_object: ModelType, auto_commit: bool = DEFAULT_AUTO_COMMIT
    ) -> Any:
        """
        Удаляет переданный объект.
        """
        try:
            await session.delete(db_object)
            if auto_commit:
                await session.commit()
        except Exception as e:
            await session.rollback()
            logger.error(f'{TEXT_ERROR_SERVER_DELETE_LOG} {self.model.__name__}: {e}')
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=TEXT_ERROR_SERVER_DELETE,
            )

    def _apply_filters(self, query: Select, filters: dict[str, Any]) -> Select:
        """
        Добавляет простые условия равенства (WHERE) к запросу на основе словаря.

        Назначение:
            Фильтрует результат по полям self.model. Если поля нет в модели,
            он игнорируется.
        Параметры:
            query: Исходный SQLAlchemy Select.
            filters: Словарь вида {имя_поля: значение}.
        Возвращаемое значение:
            Обновлённый запрос c наложенными условиями.
        Пример:
            filters = {'status': 'active', 'user_id': 10}
            query = select(self.model)
            query = self._apply_filters(query, filters)
            # WHERE model.status='active' AND model.user_id=10
        """
        # TODO: Добавить поддержку операций >, <, LIKE, IN, BETWEEN и т.д.
        for field_name, field_value in filters.items():
            column = getattr(self.model, field_name, None)
            if column is not None:
                query = query.where(column == field_value)
        return query

    def _apply_order_by(self, query: Select, order_by: list[str]) -> Select:
        """
        Добавляет сортировку (ORDER BY) к запросу, поддерживая '-' для убывания.

        Назначение:
            Упорядочивает результат по указанным полям модели. Если поле
            начинается с '-', применяется сортировка по убыванию. Если
            поля нет в модели, он игнорируется.
        Параметры:
            query: Исходный SQLAlchemy Select.
            order_by: Список имён полей; '-' в начале означает DESC.
        Возвращаемое значение:
            Обновлённый запрос с сортировкой.
        Пример:
            order = ['-created_at', 'id']
            query = select(self.model)
            query = self._apply_order_by(query, order)
            # ORDER BY model.created_at DESC, model.id ASC
        """
        for field_name in order_by:
            desc = field_name.startswith('-')
            actual_field_name = field_name[1:] if desc else field_name
            column = getattr(self.model, actual_field_name, None)
            if column is not None:
                query = query.order_by(column.desc() if desc else column.asc())
        return query


class UserCreateMixin:
    """
    Миксин для CRUD. Добавляет метод для создания пользователя.
    """

    async def create_user(
        self,
        request: Request,
        user_create: schemas.UC,
        user_manager: BaseUserManager[models.UP, models.ID],
    ):
        """
        Создаст нового пользователя.
        Электронная почта считается `username` в передаваемой форме.
        Проводится проверка на уникальность электронной почты.
        Проводится проверка пароля.
        В БД данных пароль не сохраняется, сохраняется его хэш.
        """
        try:
            created_user = await user_manager.create(user_create, safe=False, request=request)
        except exceptions.UserAlreadyExists:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail=TEXT_ERROR_EXISTS_EMAIL,
            )
        except exceptions.InvalidPasswordException as e:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail={
                    'code': TEXT_ERROR_INVALID_PASSWORD,
                    'reason': e.reason,
                },
            )
        return created_user
