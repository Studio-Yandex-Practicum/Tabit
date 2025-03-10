"""Модуль CRUD для компании."""

from datetime import datetime
from typing import Any, List

from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.companies.models import Company
from src.crud import CRUDBase
from src.tabit_management.models import LicenseType


class CRUDCompany(CRUDBase):
    """CRUD операции для модели компании."""

    async def get_import(
        self,
        objects_in: List,
        file_name: str,
    ) -> Any:
        """
        Импортирует записи в файл .txt.
        Параметры метода:
            objects_in: список объектов для импорта
            file_name: имя импортируемого файла без расширения.
        """
        with open(f'{file_name}.txt', 'w') as file:
            count = 0
            table_titles = []
            for entity in objects_in:
                entity_string = []
                for key, value in entity.__dict__.items():
                    if key not in (
                        '_sa_instance_state',
                        'updated_at',
                        'created_at',
                        'hashed_password',
                    ):
                        entity_string.append(str(value))
                        table_titles.append(key)
                if count == 0:
                    file.write(f'{"  ".join(table_titles)}\n')
                file.write(f'{"  ".join(entity_string)}\n')
                count += 1
        return FileResponse(path=f'{file_name}.txt', filename=f'{file_name}.txt')

    # TODO Этот метод был создан, чтобы исключить изменения в базовом crud, в методе get_by_slug
    # Было принято решение покf не менять метод get_by_slug, а создать этот метод
    # В методе get_by_slug допущена ошибка в условии проверке. Там проверяют not result
    # хотя на самом деле нам нужно проверять, был ли найден объект в базе данных.
    # result — это объект, полученный от запроса к базе данных, и даже если он пустой,
    # у него все равно будет значение (например, объект запроса), поэтому not result
    # не обязательно будет истинным, когда данные не найдены.
    # Вместо этого нам нужно проверять obj_model, который содержит реальный результат запроса.
    async def get_by_company_slug(self, session: AsyncSession, company_slug: str):
        """Получает компанию по slug.

        Параметры:
            session: Асинхронная сессия SQLAlchemy.
            obj_slug: Строка, представляющая slug компании.
        Возвращаемое значение:
            Найденный объект компании или None.
        """
        company = await session.execute(select(Company).where(Company.slug == company_slug))
        return company.scalar_one_or_none()

    async def is_company_slug_exists(self, session: AsyncSession, slug: str) -> None:
        """
        Проверяет, существует ли компания с указанным slug.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            slug (str): Уникальный slug компании.

        Returns:
            bool: True, если компания с таким slug уже существует, иначе False.
        """
        result = await session.execute(select(Company).where(Company.slug == slug))
        return result.scalar_one_or_none() is not None

    async def save_end_license_time(
        self, session: AsyncSession, company_start_license_time: datetime, license_id: int
    ) -> datetime:
        """
        Вычисляет дату окончания лицензии.

        Args:
            session (AsyncSession): Асинхронная сессия SQLAlchemy.
            company_start_license_time (datetime): Дата начала лицензии.
            license_id (int): ID лицензии.

        Returns:
            datetime: Дата окончания лицензии.
        """
        license_term = await session.scalar(
            select(LicenseType.license_term).where(LicenseType.id == license_id)
        )

        return company_start_license_time + license_term


company_crud = CRUDCompany(Company)
