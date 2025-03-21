import pytest
from fastapi import status
from fastapi.encoders import jsonable_encoder
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.users.models import UserTabit
from tests.constants import (
    ADMIN_CREATE_MOD_BAD,
    ADMIN_CREATE_MOD_NEW,
    ADMIN_GET_MOD_INFO,
    ADMIN_PATCH_MOD,
    ADMIN_PATCH_MOD_BAD,
    ADMIN_PUT_MOD,
    MOD_TEST_EMAIL_BAD,
    TEST_UUID,
    URL,
)
from tests.utils import get_count, update_object


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

    @pytest.mark.skip(reason='Нет возможности протестировать')
    async def test_get_paginated_companies_info(
        self, client: AsyncClient, administrator_tabit, company_for_test, get_token
    ):
        """Тест для проверки получения списка компаний с пагинацией."""
        # TODO: после добавления пагинации написать тест для её проверки
        pass

    async def test_get_multiple_staff(
        self,
        client: AsyncClient,
        administrator_tabit,
        get_token,
        department_for_test,
        moderator_of_company,
    ):
        """Тест для проверки получения списка модераторов."""
        admin = await administrator_tabit()
        token = await get_token(client, admin, URL.ADMIN_LOGIN)
        department = await department_for_test()
        ten_mods = [
            await moderator_of_company(
                {'company_id': department.company_id, 'current_department_id': department.id}
            )
            for _ in range(10)
        ]
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

    @pytest.mark.skip(reason='Нет возможности протестировать')
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
        department_for_test,
        moderator_of_company,
        url,
        status_code,
    ):
        """Тест для проверки получения информации о модераторе по переданному UUID."""
        admin = await administrator_tabit()
        token = await get_token(client, admin, URL.ADMIN_LOGIN)
        department = await department_for_test()
        moderator = await moderator_of_company(
            {'company_id': department.company_id, 'current_department_id': department.id}
        )
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
        self, client: AsyncClient, administrator_tabit, get_token, department_for_test
    ):
        """Тест для проверки создания модератора"""
        admin = await administrator_tabit()
        token = await get_token(client, admin, URL.ADMIN_LOGIN)
        department = await department_for_test()
        response = await client.post(
            URL.ADMIN_MODS_URL,
            headers=token,
            json=ADMIN_CREATE_MOD_NEW.update(
                {'company_id': department.company_id, 'current_department_id': department.id}
            ),
        )
        assert response.status_code == status.HTTP_200_OK, (
            f'В ответе ожидается status_code {status.HTTP_200_OK}, получен {response.status_code}'
        )
        result = response.json()
        for key in ADMIN_CREATE_MOD_NEW:
            if key != 'password':
                assert result[key] == ADMIN_CREATE_MOD_NEW[key]
        assert result['company_id'] == department.company_id
        assert result['current_department_id'] == department.id
        assert result['last_department_id'] is None

    @pytest.mark.parametrize('payload', ADMIN_CREATE_MOD_BAD)
    async def test_unsuccessful_create_moderator(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        administrator_tabit,
        get_token,
        company_for_test,
        department_for_test,
        moderator_of_company,
        payload,
    ):
        """Тест для проверки неуспешного создания модератора"""
        admin = await administrator_tabit()
        token = await get_token(client, admin, URL.ADMIN_LOGIN)
        department = await department_for_test()
        await moderator_of_company(
            ADMIN_CREATE_MOD_NEW.update(
                {'company_id': department.company_id, 'current_department_id': department.id}
            )
        )
        await company_for_test()  # создаётся другая компания
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

    @pytest.mark.parametrize('payload, check_department_change', ADMIN_PATCH_MOD)
    async def test_successful_patch_moderator(
        self,
        client: AsyncClient,
        administrator_tabit,
        get_token,
        department_for_test,
        moderator_of_company,
        payload,
        check_department_change,
    ):
        """Тест для проверки обновления модератора PATCH-запросом"""
        admin = await administrator_tabit()
        token = await get_token(client, admin, URL.ADMIN_LOGIN)
        department = await department_for_test()
        await department_for_test({'company_id': department.company_id})
        moderator = await moderator_of_company(
            {'company_id': department.company_id, 'current_department_id': department.id}
        )
        response = await client.patch(
            URL.ADMIN_MOD_DATA_URL.format(user_id=moderator.id),
            headers=token,
            json=payload,
        )
        assert response.status_code == status.HTTP_200_OK, (
            f'В ответе ожидается status_code {status.HTTP_200_OK}, получен {response.status_code}'
        )
        result = response.json()
        for key in payload:
            assert result[key] == payload[key]
        if check_department_change:
            assert result['last_department_id'] == department.id

    @pytest.mark.parametrize('payload', ADMIN_PATCH_MOD_BAD)
    async def test_unsuccessful_patch_moderator(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        administrator_tabit,
        get_token,
        department_for_test,
        moderator_of_company,
        payload,
    ):
        """Тест для проверки неуспешного обновления модератора PATCH-запросом"""
        admin = await administrator_tabit()
        token = await get_token(client, admin, URL.ADMIN_LOGIN)
        department = await department_for_test()
        moderator = await moderator_of_company(
            ADMIN_CREATE_MOD_NEW.update(
                {'company_id': department.company_id, 'current_department_id': department.id}
            )
        )
        await moderator_of_company(
            {
                'email': MOD_TEST_EMAIL_BAD,
                'company_id': department.company_id,
                'current_department_id': department.id,
            }
        )
        await department_for_test()  # создаётся другой отдел для другой компании
        old_moderator_data = jsonable_encoder(moderator)
        response = await client.patch(
            URL.ADMIN_MOD_DATA_URL.format(user_id=moderator.id),
            headers=token,
            json=payload,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, (
            f'В ответе ожидается status_code {status.HTTP_422_UNPROCESSABLE_ENTITY}, '
            f'получен {response.status_code}'
        )
        new_moderator_data = update_object(async_session, moderator)
        assert new_moderator_data == old_moderator_data, (
            'При неуспешном PATCH-запросе объект пользователя не должен меняться'
        )

    @pytest.mark.parametrize('payload, check_department_change', ADMIN_PUT_MOD)
    async def test_successful_put_moderator(
        self,
        client: AsyncClient,
        administrator_tabit,
        get_token,
        department_for_test,
        moderator_of_company,
        payload,
        check_department_change,
    ):
        admin = await administrator_tabit()
        token = await get_token(client, admin, URL.ADMIN_LOGIN)
        department = await department_for_test()
        await department_for_test({'company_id': department.company_id})
        moderator = await moderator_of_company(
            {'company_id': department.company_id, 'current_department_id': department.id}
        )
        response = await client.put(
            URL.ADMIN_MOD_DATA_URL.format(user_id=moderator.id),
            headers=token,
            json=payload,
        )
        assert response.status_code == status.HTTP_200_OK, (
            f'В ответе ожидается status_code {status.HTTP_200_OK}, получен {response.status_code}'
        )
        result = response.json()
        for key in payload:
            assert result[key] == payload[key]
        if check_department_change:
            assert result['last_department_id'] == department.id

    @pytest.mark.parametrize('payload', ADMIN_PATCH_MOD_BAD)
    async def test_unsuccessful_put_moderator(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        administrator_tabit,
        get_token,
        department_for_test,
        moderator_of_company,
        payload,
    ):
        admin = await administrator_tabit()
        token = await get_token(client, admin, URL.ADMIN_LOGIN)
        department = await department_for_test()
        moderator = await moderator_of_company(
            ADMIN_CREATE_MOD_NEW.update(
                {'company_id': department.company_id, 'current_department_id': department.id}
            )
        )
        await moderator_of_company(
            {
                'email': MOD_TEST_EMAIL_BAD,
                'company_id': department.company_id,
                'current_department_id': department.id,
            }
        )
        await department_for_test()  # создаётся другой отдел для другой компании
        old_moderator_data = jsonable_encoder(moderator)
        response = await client.put(
            URL.ADMIN_MOD_DATA_URL.format(user_id=moderator.id),
            headers=token,
            json=payload,
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, (
            f'В ответе ожидается status_code {status.HTTP_422_UNPROCESSABLE_ENTITY}, '
            f'получен {response.status_code}'
        )
        new_moderator_data = update_object(async_session, moderator)
        assert new_moderator_data == old_moderator_data, (
            'При неуспешном PUT-запросе объект пользователя не должен меняться'
        )

    async def test_update_404(
        self,
        client: AsyncClient,
        administrator_tabit,
        get_token,
    ):
        admin = await administrator_tabit()
        token = await get_token(client, admin, URL.ADMIN_LOGIN)
        response = await client.patch(
            URL.ADMIN_MOD_DATA_URL.format(user_id=TEST_UUID), headers=token, json=ADMIN_PATCH_MOD
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            f'В ответе ожидается status_code {status.HTTP_404_NOT_FOUND}, '
            f'получен {response.status_code}'
        )
        response = await client.put(
            URL.ADMIN_MOD_DATA_URL.format(user_id=TEST_UUID), headers=token, json=ADMIN_PUT_MOD
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            f'В ответе ожидается status_code {status.HTTP_404_NOT_FOUND}, '
            f'получен {response.status_code}'
        )


@pytest.mark.asyncio
class TestDeleteTabitManagement:
    """Класс для тестов POST-эндпоинтов tabit_management.py"""

    async def test_delete_moderator(
        self,
        client: AsyncClient,
        administrator_tabit,
        get_token,
        department_for_test,
        moderator_of_company,
    ):
        admin = await administrator_tabit()
        token = await get_token(client, admin, URL.ADMIN_LOGIN)
        department = await department_for_test()
        moderator = await moderator_of_company(
            {'company_id': department.company_id, 'current_department_id': department.id}
        )
        response = await client.delete(
            URL.ADMIN_MOD_DATA_URL.format(user_id=moderator.id), headers=token
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT, (
            f'В ответе ожидается status_code {status.HTTP_204_NO_CONTENT}, '
            f'получен {response.status_code}'
        )

    async def test_delete_moderator_404(self, client: AsyncClient, administrator_tabit, get_token):
        admin = await administrator_tabit()
        token = await get_token(client, admin, URL.ADMIN_LOGIN)
        response = await client.delete(
            URL.ADMIN_MOD_DATA_URL.format(user_id=TEST_UUID), headers=token
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            f'В ответе ожидается status_code {status.HTTP_404_NOT_FOUND}, '
            f'получен {response.status_code}'
        )
