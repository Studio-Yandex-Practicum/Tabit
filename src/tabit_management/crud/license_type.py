import sqlalchemy as sa
from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import CRUDBase
from src.tabit_management.models import LicenseType
from src.tabit_management.schemas.license_type import (
    LicenseTypeFilterSchema,
    LicenseTypeResponseSchema,
)


class CRUDLicenseType(CRUDBase):
    """CRUD операций для моделей лицензий компаний."""

    async def is_license_name_exists(self, session: AsyncSession, name: str) -> bool:
        """Проверяет, существует ли лицензия с данным именем."""
        result = await session.execute(sa.select(LicenseType).where(LicenseType.name == name))
        return result.scalar_one_or_none() is not None

    async def get_filtered(self, session: AsyncSession, filters: LicenseTypeFilterSchema):
        """Возвращает список лицензий с фильтрацией, сортировкой и пагинацией."""
        query = select(LicenseType)

        if filters.name:
            query = query.where(LicenseType.name.ilike(f'%{filters.name}%'))

        if filters.ordering:
            order_field = filters.ordering.lstrip('-')
            sort_order = desc if filters.ordering.startswith('-') else asc
            query = query.order_by(sort_order(getattr(LicenseType, order_field)))

        total_query = select(sa.func.count()).select_from(query.subquery())
        total_result = await session.execute(total_query)
        total_records = total_result.scalar()

        query = query.limit(filters.page_size).offset((filters.page - 1) * filters.page_size)

        result = await session.execute(query)
        license_objects = result.scalars().all()

        return {
            'total': total_records,
            'page': filters.page,
            'page_size': filters.page_size,
            'items': [
                LicenseTypeResponseSchema.model_validate(license) for license in license_objects
            ],
        }


license_type_crud = CRUDLicenseType(LicenseType)
