"""
Модуль с универсальным базовым классом для CRUD операций.

Содержит:
- Определения типов: ModelType, CreateSchemaType, UpdateSchemaType.
- Константу Default.AUTO_COMMIT для управления автокоммитом.
- Функции для фильтрации и сортировки запросов:
  apply_filters, apply_order_by.
- Класс CRUDBase с асинхронными методами get, get_or_404, get_multi,
  create, update и delete.
"""

from http import HTTPStatus
from typing import Any, Dict, Generic, Type, TypeVar
from uuid import UUID

from fastapi import HTTPException, status
from fastapi.encoders import jsonable_encoder
from fastapi_users import BaseUserManager, exceptions, models, schemas
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import Select
from starlette.requests import Request

from src.core.config.logging import logger
from src.crud.constants import Default, TextError

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

    async def get(self, session: AsyncSession, obj_id: int | str | UUID) -> ModelType | None:
        """
        Получает объект по ID (int, str или UUID).

        Возвращает объект модели или None, если он не найден.
        """
        result = await session.execute(select(self.model).where(self.model.id == obj_id))
        return result.scalars().first()

    async def get_or_404(
        self, session: AsyncSession, obj_id: int | UUID, message: str | None = None
    ) -> ModelType:
        """
        Получает объект из БД по id или выбрасывает 404-ошибку.

        Параметры:
            session: Асинхронная сессия SQLAlchemy.
            obj_id: идентификатор объекта.
            message: сообщение, которое вернется с ошибкой 404.
        Возвращает:
            Экземпляр модели.

        Возможные ошибки:
            HTTPException со статусом 404, если не найдет объект по id в БД.
        """
        obj = await self.get(session, obj_id)
        if not obj:
            if message is None:
                message = TextError.NOT_FOUND.format(obj=self.model.__name__, id=obj_id)
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
        return obj

    async def get_by_slug(
        self,
        session: AsyncSession,
        obj_slug: str,
        raise_404: bool = False,
        message: str | None = None,
    ) -> ModelType | None:
        """
        Получает объект по полю slug.

        Возвращает объект модели или None, если он не найден.
        Если параметр raise_404 = True, тогда выбрасывает 404-ошибку, если не найден.
        """
        result = await session.execute(select(self.model).where(self.model.slug == obj_slug))
        obj_model = result.scalars().first()
        if not obj_model and raise_404:
            if message is None:
                message = TextError.NOT_FOUND_BY_SLUG.format(
                    obj=self.model.__name__, slug=obj_slug
                )
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=message)
        return obj_model

    async def get_multi(
        self,
        session: AsyncSession,
        skip: int = Default.SKIP,
        limit: int = Default.LIMIT,
        filters: Dict[str, Any] | None = None,
        order_by: list[str] | None = None,
        unique_filter_rows: bool = False,
    ) -> list[ModelType]:
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
            unique_filter_rows: При значении True изменит результирующий ответЖ:
                добавит метод unique(), чтобы каждая строка возвращалась уникальным образом.
                Необходим для некоторых запросов.
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
        if unique_filter_rows:
            return result.unique().scalars().all()  # type: ignore
        return result.scalars().all()  # type: ignore

    async def create(
        self,
        session: AsyncSession,
        obj_in: CreateSchemaType,
        auto_commit: bool = Default.AUTO_COMMIT,
    ) -> ModelType:
        """
        Создаёт новый объект в БД.
        """
        # TODO: Добавить возможность автозаполнение поля owner у модели.
        obj_data = obj_in.model_dump()  # type: ignore
        db_obj = self.model(**obj_data)
        try:
            session.add(db_obj)
            if auto_commit:
                await session.commit()
                await session.refresh(db_obj)
        except Exception as error:
            await session.rollback()
            logger.error(f'{TextError.CREATE_SERVER_LOG} {self.model.__name__}: {error}')
            raise error
        return db_obj

    async def update(
        self,
        session: AsyncSession,
        db_obj: ModelType,
        obj_in: UpdateSchemaType,
        auto_commit: bool = Default.AUTO_COMMIT,
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
        except Exception as error:
            await session.rollback()
            logger.error(f'{TextError.UPDATE_SERVER_LOG} {self.model.__name__}: {error}')
            raise error
        return db_obj

    async def remove(
        self, session: AsyncSession, db_object: ModelType, auto_commit: bool = Default.AUTO_COMMIT
    ) -> Any:
        """
        Удаляет переданный объект.
        """
        try:
            await session.delete(db_object)
            if auto_commit:
                await session.commit()
        except Exception as error:
            await session.rollback()
            logger.error(f'{TextError.DELETE_SERVER_LOG} {self.model.__name__}: {error}')
            raise error

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
                detail=TextError.EXISTS_EMAIL,
            )
        except exceptions.InvalidPasswordException as e:
            raise HTTPException(
                status_code=HTTPStatus.BAD_REQUEST,
                detail={
                    'code': TextError.INVALID_PASSWORD,
                    'reason': e.reason,
                },
            )
        return created_user


class CRUDBaseWithAssociations(CRUDBase):
    """Расширенный CRUD для изменения таблицы БД и связной модели."""

    def __init__(self, model, associations_model):
        """
        Параметры:
            associations_model: связная таблица.
        """
        super().__init__(model)
        self.associations_model = associations_model

    def get_data_associations_for_updata(
        self,
        data_from_db: list[dict[str, Any]],
        data_to_update: set[Any],
        left_id: bool = True,
    ) -> tuple[list[str], list[str]]:
        """
        Подготовит информацию о добавлении и удалении записей в связную таблицу,
        на основе изменений в основной таблице.

        Параметры:
            data_from_db: список словарей с записями связной таблицы из БД
                (получив объект, мы можем получить все записи в связной таблице);
            data_to_update: набор данных полученных из обновления
                (при изменении записи основной таблице передаётся информация об изменениях
                в связной, например, набор UUID);
            left_id: если True, то в записях из БД будет сверять данные атрибут left_id,
                в противном случае right_id.
        Возвращает:
            Кортеж из двух списков со строками. В первом списке перечень добавляемых значений,
            во втором удаляемых. (Если в наборе с изменениями есть те параметры, которые уже
            записаны в связную таблицу - они игнорируются и не будут добавлены не в один
            из списков).
        """
        side = 'left_id' if left_id else 'right_id'
        add_rows = [
            str(update)
            for update in data_to_update
            if str(update) not in [from_db[side] for from_db in data_from_db]
        ]
        delete_rows = [
            from_db[side]
            for from_db in data_from_db
            if (from_db[side] not in [str(update) for update in data_to_update])
        ]
        return add_rows, delete_rows
