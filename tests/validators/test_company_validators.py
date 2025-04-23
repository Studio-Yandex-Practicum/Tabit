from src.features_v1.constants import TextError
import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.features_v1.validators.company_validators import (
    check_department_name_duplicate,
    check_slug_duplicate,
    check_user_company,
    check_company_and_department,
    check_company_exists,
    validate_company_slug,
)
from src.models import Company

@pytest.mark.asyncio
class TestCompanyValidators:
    """Тесты для валидаторов, связанных с компаниями и отделами."""

    async def test_check_department_name_duplicate_raises(self, async_session: AsyncSession, company_for_test):
        """
        Тест проверяет, что при дублировании имени отдела выбрасывается HTTPException с кодом 400.

        Параметры:
            - async_session (AsyncSession): Асинхронная сессия SQLAlchemy.
            - company_for_test (callable): Фикстура для создания компании с отделом.

        Ассерты:
            - Проверка, что выбрасывается HTTPException с кодом 400.
        """
        company, department = await company_for_test(with_department=True)
        with pytest.raises(HTTPException) as exc:
            await check_department_name_duplicate(company.id, department.name, async_session)
        assert exc.value.status_code == 400

    async def test_check_department_name_duplicate_passes(self, async_session: AsyncSession, company_for_test):
        """
        Тест проверяет, что при уникальном имени отдела валидация проходит без исключений.

        Параметры:
            - async_session (AsyncSession): Асинхронная сессия SQLAlchemy.
            - company_for_test (callable): Фикстура для создания компании с отделом.

        Ассерты:
            - Проверка, что валидация проходит без исключений.
        """
        company, department = await company_for_test(with_department=True)
        await check_department_name_duplicate(company.id, "unique-name", async_session)

    async def test_check_slug_duplicate_unique(self, async_session: AsyncSession):
        """
        Тест проверяет, что для уникального имени компании генерируется корректный slug.

        Параметры:
            - async_session (AsyncSession): Асинхронная сессия SQLAlchemy.

        Ассерты:
            - Проверка, что slug начинается с ожидаемой строки.
        """
        company = Company(name="Unique Company Name")
        slug = await check_slug_duplicate(company, async_session)
        assert slug.startswith("unique-company-name")

    async def test_check_user_company_valid(self, async_session: AsyncSession, company_for_test):
        """
        Тест проверяет валидность соответствия company_id и slug компании.

        Параметры:
            - async_session (AsyncSession): Асинхронная сессия SQLAlchemy.
            - company_for_test (callable): Фикстура для создания компании.

        Ассерты:
            - Проверка, что валидация проходит без исключений.
        """
        company = await company_for_test({'name': 'Компания тест'})
        await check_user_company(company.id, company.slug, async_session)

    async def test_check_user_company_invalid(self, async_session: AsyncSession, company_for_test):
        """
        Тест проверяет, что при несоответствии slug компании выбрасывается HTTPException с кодом 403.

        Параметры:
            - async_session (AsyncSession): Асинхронная сессия SQLAlchemy.
            - company_for_test (callable): Фикстура для создания компании.

        Ассерты:
            - Проверка, что выбрасывается HTTPException с кодом 403.
        """
        company = await company_for_test({'name': 'Компания тест'})
        with pytest.raises(HTTPException) as exc:
            await check_user_company(company.id, "wrong-slug", async_session)
        assert exc.value.status_code == 403

    async def test_check_company_and_department_valid(self, async_session: AsyncSession, company_for_test):
        """
        Тест проверяет валидность комбинации company_id и department_id.

        Параметры:
            - async_session (AsyncSession): Асинхронная сессия SQLAlchemy.
            - company_for_test (callable): Фикстура для создания компании с отделом.

        Ассерты:
            - Проверка, что валидация проходит без исключений.
        """
        company, department = await company_for_test(with_department=True)
        await check_company_and_department(company.id, department.id, async_session)

    async def test_check_company_and_department_invalid_department(self, async_session: AsyncSession, company_for_test):
        """
        Тест проверяет, что при несуществующем department_id выбрасывается HTTPException с кодом 422 и соответствующим сообщением.

        Параметры:
            - async_session (AsyncSession): Асинхронная сессия SQLAlchemy.
            - company_for_test (callable): Фикстура для создания компании.

        Ассерты:
            - Проверка, что выбрасывается HTTPException с кодом 422.
            - Проверка, что detail ошибки соответствует TextError.DEPARTMENT_NOT_FOUND.
        """
        company = await company_for_test({'name': 'Компания тест'})
        with pytest.raises(HTTPException) as exc:
            await check_company_and_department(company.id, 999999, async_session)
        assert exc.value.status_code == 422
        assert exc.value.detail == TextError.DEPARTMENT_NOT_FOUND

    async def test_check_company_exists_found(self, async_session: AsyncSession, company_for_test):
        """
        Тест проверяет успешное нахождение компании по slug.

        Параметры:
            - async_session (AsyncSession): Асинхронная сессия SQLAlchemy.
            - company_for_test (callable): Фикстура для создания компании.

        Ассерты:
            - Проверка, что валидация проходит без исключений.
        """
        company = await company_for_test({'name': 'Компания тест'})
        await check_company_exists(company.slug, async_session)

    async def test_check_company_exists_not_found(self, async_session: AsyncSession):
        """
        Тест проверяет, что при отсутствии компании по slug выбрасывается HTTPException с кодом 404.

        Параметры:
            - async_session (AsyncSession): Асинхронная сессия SQLAlchemy.

        Ассерты:
            - Проверка, что выбрасывается HTTPException с кодом 404.
        """
        with pytest.raises(HTTPException) as exc:
            await check_company_exists("non-existent", async_session)
        assert exc.value.status_code == 404

    async def test_validate_company_slug_duplicate(self, async_session: AsyncSession, company_for_test):
        """
        Тест проверяет, что при дублирующемся slug компании выбрасывается HTTPException с кодом 400.

        Параметры:
            - async_session (AsyncSession): Асинхронная сессия SQLAlchemy.
            - company_for_test (callable): Фикстура для создания компании.

        Ассерты:
            - Проверка, что выбрасывается HTTPException с кодом 400.
        """
        company = await company_for_test({'name': 'Компания тест'})
        with pytest.raises(HTTPException) as exc:
            await validate_company_slug(async_session, company.slug)
        assert exc.value.status_code == 400

    async def test_validate_company_slug_unique(self, async_session: AsyncSession):
        """
        Тест проверяет, что при уникальном slug компании валидация проходит без исключений.

        Параметры:
            - async_session (AsyncSession): Асинхронная сессия SQLAlchemy.

        Ассерты:
            - Проверка, что валидация проходит без исключений.
        """
        await validate_company_slug(async_session, "totally-unique-slug")