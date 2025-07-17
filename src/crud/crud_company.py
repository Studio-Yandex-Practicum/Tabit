"""Модуль CRUD для компании."""

from datetime import datetime, timedelta, timezone
from typing import Any, List

from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from src.crud import CRUDBase
from src.crud.constants import DefaultConstants, DirectoryConstants
from src.models import Company, LicenseType
from src.schemas import CompanyCreateSchema, CompanyUpdateSchema
from src.utils.base64_image import base64image


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

    # TODO LOST: используется в валидаторе, который нигде не используется
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

    async def is_company_slug_exists(self, session: AsyncSession, slug: str) -> bool:
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
        if license_term is None:
            raise ValueError(f'У лицензии с ID {license_id} отсутствует срок действия.')
        delta: timedelta = timedelta(
            days=license_term.days,
            seconds=license_term.seconds,
            microseconds=license_term.microseconds,
        )
        return company_start_license_time + delta

    async def create(
        self,
        session: AsyncSession,
        company_in: CompanyCreateSchema,
        auto_commit: bool = DefaultConstants.AUTO_COMMIT,
    ) -> Company:
        """
        Создаёт запись в таблице "Компания".

        Если был передан логотип, то декодирует его из строки Base64 в файл
        и в поле logo сохранит путь до него.

        Если указаны license_id и start_license_time — рассчитывает end_license_time и is_active.
        """
        company_data = company_in.model_dump()

        if company_in.logo:
            assert company_in.slug is not None
            company_data['logo'] = await base64image(
                company_in.logo, company_in.slug, DirectoryConstants.LOGO
            )

        if company_in.license_id and company_in.start_license_time:
            end_license_time = await self.save_end_license_time(
                session,
                company_start_license_time=company_in.start_license_time,
                license_id=company_in.license_id,
            )
            company_data['end_license_time'] = end_license_time
        else:
            company_data['end_license_time'] = None

        now = datetime.now(timezone.utc)
        start = company_data.get('start_license_time')
        end = company_data.get('end_license_time')
        if start and end and start <= now <= end:
            company_data['is_active'] = True
        else:
            company_data['is_active'] = False

        company_schema = CompanyCreateSchema(**company_data)
        return await super().create(session, company_schema, auto_commit)

    async def update(
        self,
        session: AsyncSession,
        company_db: Company,
        company_in: CompanyUpdateSchema,
        auto_commit: bool = DefaultConstants.AUTO_COMMIT,
    ) -> Company:
        """
        Обновляет запись компании.

        - Обрабатывает логотип, если передан.
        - Пересчитывает end_license_time и is_active.
        """
        company_data = company_in.model_dump(exclude_unset=True)
        if company_in.logo:
            company_data['logo'] = await base64image(
                company_in.logo, company_db.slug, DirectoryConstants.LOGO
            )

        if company_in.license_id and company_in.start_license_time:
            end_license_time = await self.save_end_license_time(
                session,
                company_start_license_time=company_in.start_license_time,
                license_id=company_in.license_id,
            )
            company_data['end_license_time'] = end_license_time
            now = datetime.now(timezone.utc)
            if company_in.start_license_time <= now <= end_license_time:
                company_data['is_active'] = True
            else:
                company_data['is_active'] = False

        for key, value in company_data.items():
            setattr(company_db, key, value)
        return await super().update(session, company_db, company_in, auto_commit)


company_crud = CRUDCompany(Company)
