"""Модуль CRUD для отдела."""

import random

from slugify import slugify
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config.logging import logger
from src.core.constants import DEFAULT_AUTO_COMMIT, LENGTH_SLUG, TextError
from src.crud.crud_base import CRUDBase
from src.models import Department
from src.schemas.company import CompanyDepartmentCreateSchema, CompanyDepartmentUpdateSchema


class CRUDDepartment(CRUDBase):
    """
    CRUD операций для модели отделов компании.

    Класс предоставляет базовые методы для создания, чтения, обновления
    и удаления объектов в базе данных.

    Атрибуты:
        model (Type[BaseModel]): Модель SQLAlchemy для работы с базой данных.
    """

    async def create_for_company(
        self,
        session: AsyncSession,
        department_in: CompanyDepartmentCreateSchema,
        company_id: int,
        auto_commit: bool = DEFAULT_AUTO_COMMIT,
    ) -> Department:
        """
        Создание отдела для конкретной компании.

        Аргументы:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            department_in (Type[BaseModel]): Модель Pydantic для тела запроса для создания записи.
            company_id (int): идентификационный номер компании, в которой планируется создать
                отдел.
            auto_commit (bool): флаг, если True, то функция сохранит в БД изменения сама.
        Возвращает:
            Department: экземпляр модели Отдела.

        Исключения:
            ValueError: Возникает при некорректных значениях параметров.
            DatabaseError: Возникает при ошибках работы с базой данных.
        """
        db_department: Department = self.model(**department_in.model_dump())
        db_department.slug = await self._generate_slug(session, department_in.name)
        db_department.company_id = company_id
        try:
            session.add(db_department)
            if auto_commit:
                await session.commit()
                await session.refresh(db_department)
        except Exception as error:
            await session.rollback()
            logger.error(f'{TextError.SERVER_UPDATE_LOG} {self.model.__name__}: {error}')
            raise error
        return db_department

    async def update(
        self,
        session: AsyncSession,
        db_department: Department,
        department_in: CompanyDepartmentUpdateSchema,
        auto_commit: bool = DEFAULT_AUTO_COMMIT,
    ) -> Department:
        """
        Изменение данных отдела.

        Аргументы:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            db_department (Department): Экземпляр модели Отдела, которую меняем.
            department_in (Type[BaseModel]): Модель Pydantic для тела запроса для изменения записи.
            auto_commit (bool): флаг, если True, то функция сохранит в БД изменения сама.
        Возвращает:
            Department: экземпляр модели Отдела.

        Исключения:
            ValueError: Возникает при некорректных значениях параметров.
            DatabaseError: Возникает при ошибках работы с базой данных.
        """
        if department_in.name and department_in.name != db_department.name:
            db_department.slug = await self._generate_slug(session, department_in.name)
        return await super().update(session, db_department, department_in, auto_commit)

    async def get_by_name_in_company(
        self,
        session: AsyncSession,
        name: str,
        company_id: int,
    ) -> Department | None:
        result = await session.execute(
            select(self.model).where(
                (self.model.name == name) & (self.model.company_id == company_id)
            )
        )
        return result.scalars().first()

    async def _generate_slug(self, session: AsyncSession, name: str) -> str:
        """
        Генерирует уникальный slug. Если сгенерированный slug уже существует в БД,
        добавляет случайное число в конец и повторяет проверку.

        Аргументы:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            name (str): Название, из которого создается slug.

        Возвращает:
            str: Уникальный slug.

        Исключения:
            ValueError: Возникает при некорректных значениях параметров.
            DatabaseError: Возникает при ошибках работы с базой данных.
        """
        new_slug = slugify(name)
        while await department_crud.get_by_slug(session, new_slug):
            new_slug = f'{new_slug}-{random.randint(1000, 9999)}'[:LENGTH_SLUG]
        return new_slug


department_crud = CRUDDepartment(Department)
