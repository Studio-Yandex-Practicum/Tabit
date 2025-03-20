import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import UserTabit
from tests.constants import (
    ADMIN_CREATE_MOD_BAD,
    ADMIN_CREATE_MOD_NEW,
    ADMIN_GET_MOD_INFO,
    ADMIN_UPDATE_MOD,
    TEST_UUID,
    URL,
)
from tests.utils import get_count


@pytest.mark.asyncio
class TestGetTabitManagement:
    """Класс для тестов GET-эндпоинтов tabit_management.py"""

    async def test_get_companies_info(
        self, client: AsyncClient, administrator_tabit, company_for_test, get_token
    ):
        """Тест для проверки получения списка компаний."""
        ten_companies = [await company_for_test() for _ in range(10)]
        admin = await administrator_tabit()
        token = await get_token(client, admin, URL.ADMIN_LOGIN)
        response = await client.get(URL.ADMIN_GET_COMPANIES, headers=token)
        assert response.status_code == status.HTTP_200_OK, (
            f'В ответе ожидается status_code {status.HTTP_200_OK}, получен {response.status_code}'
        )
        result = response.json()
        assert isinstance(result, list), (
            f'В качестве ответа должен быть получен list, пришёл {type(result)}'
        )
        assert len(result) == len(ten_companies), (
            f'Длина полученного списка должна быть равна {len(ten_companies)}'
        )

    async def test_get_paginated_companies_info(
        self, client: AsyncClient, administrator_tabit, company_for_test, get_token
    ):
        """Тест для проверки получения списка компаний с пагинацией."""
        # TODO: после добавления пагинации написать тест для её проверки
        pass

    async def test_get_multiple_staff(
        self, client: AsyncClient, administrator_tabit, get_token, moderator_of_company
    ):
        """Тест для проверки получения списка модераторов."""
        ten_mods = [await moderator_of_company() for _ in range(10)]
        admin = await administrator_tabit()
        token = await get_token(client, admin, URL.ADMIN_LOGIN)
        response = await client.get(URL.ADMIN_MODS_URL, headers=token)
        assert response.status_code == status.HTTP_200_OK, (
            f'В ответе ожидается status_code {status.HTTP_200_OK}, получен {response.status_code}'
        )
        result = response.json()
        assert isinstance(result, list), (
            f'В качестве ответа должен быть получен list, пришёл {type(result)}'
        )
        assert len(result) == len(ten_mods), (
            f'Длина полученного списка должна быть равна {len(ten_mods)}'
        )

    async def test_get_paginated_multiple_staff(
        self, client: AsyncClient, administrator_tabit, get_token, moderator_of_company
    ):
        """Тест для проверки получения списка модераторов с пагинацией."""
        # TODO: после добавления пагинации написать тест для её проверки
        pass

    @pytest.mark.parametrize('url, status_code', ADMIN_GET_MOD_INFO)
    async def test_get_moderator_info(
        self,
        client: AsyncClient,
        administrator_tabit,
        get_token,
        moderator_of_company,
        url,
        status_code,
    ):
        """Тест для проверки получения информации о модераторе по переданному UUID."""
        admin = await administrator_tabit()
        token = await get_token(client, admin, URL.ADMIN_LOGIN)
        moderator = await moderator_of_company()
        if status_code == status.HTTP_200_OK:
            response = await client.get(url.format(user_id=moderator.id), headers=token)
        else:
            response = await client.get(url.format(user_id=TEST_UUID), headers=token)
        assert response.status_code == status_code, (
            f'В ответе ожидается status_code {status_code}, получен {response.status_code}'
        )


@pytest.mark.asyncio
class TestPostTabitManagement:
    """Класс для тестов POST-эндпоинтов tabit_management.py"""

    async def test_successful_create_moderator(
        self, client: AsyncClient, administrator_tabit, get_token, company_for_test
    ):
        """Тест для проверки создания модератора"""
        # TODO: добавить проверку отделов после https://github.com/Studio-Yandex-Practicum/Tabit/issues/252
        admin = await administrator_tabit()
        token = await get_token(client, admin, URL.ADMIN_LOGIN)
        company = await company_for_test()
        response = await client.post(
            URL.ADMIN_MODS_URL,
            headers=token,
            json=ADMIN_CREATE_MOD_NEW.update({'company_id': company.id}),
        )
        assert response.status_code == status.HTTP_200_OK, (
            f'В ответе ожидается status_code {status.HTTP_200_OK}, получен {response.status_code}'
        )
        result = response.json()
        for key in ADMIN_CREATE_MOD_NEW:
            if key != 'password':
                assert result[key] == ADMIN_CREATE_MOD_NEW[key]
        assert result['company_id'] == company.id

    @pytest.mark.parametrize('payload', ADMIN_CREATE_MOD_BAD)
    async def test_unsuccessful_create_moderator(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        administrator_tabit,
        get_token,
        moderator_of_company,
        payload,
    ):
        # TODO: добавить проверку отделов после https://github.com/Studio-Yandex-Practicum/Tabit/issues/252
        admin = await administrator_tabit()
        token = await get_token(client, admin, URL.ADMIN_LOGIN)
        await moderator_of_company(ADMIN_CREATE_MOD_NEW)
        old_user_count = await get_count(async_session, UserTabit)
        response = await client.post(URL.ADMIN_MODS_URL, headers=token, json=payload)
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, (
            f'В ответе ожидается status_code {status.HTTP_422_UNPROCESSABLE_ENTITY}, '
            f'получен {response.status_code}'
        )
        new_user_count = await get_count(async_session, UserTabit)
        assert new_user_count == old_user_count, (
            f'Количество объектов UserTabit должно равняться {old_user_count}. '
            f'Текущее количество - {new_user_count}.'
        )


@pytest.mark.asyncio
class TestUpdateTabitManagement:
    """Класс для тестов PUT и PATCH -эндпоинтов tabit_management.py"""

    async def test_successful_patch_moderator(
        self,
        client: AsyncClient,
        administrator_tabit,
        get_token,
        moderator_of_company,
    ):
        # TODO: добавить проверку отделов после https://github.com/Studio-Yandex-Practicum/Tabit/issues/252
        admin = await administrator_tabit()
        token = await get_token(client, admin, URL.ADMIN_LOGIN)
        moderator = await moderator_of_company()
        response = await client.patch(
            URL.ADMIN_MOD_DATA_URL.format(user_id=moderator.id),
            headers=token,
            json=ADMIN_UPDATE_MOD,
        )
        assert response.status_code == status.HTTP_200_OK, (
            f'В ответе ожидается status_code {status.HTTP_200_OK}, получен {response.status_code}'
        )
        result = response.json()
        for key in ADMIN_UPDATE_MOD:
            assert result[key] == ADMIN_UPDATE_MOD[key]

    async def test_unsuccessful_patch_moderator(
        self,
        client: AsyncClient,
        administrator_tabit,
        get_token,
        moderator_of_company,
    ):
        pass
