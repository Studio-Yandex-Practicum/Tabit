import pytest
from fastapi import status
from httpx import AsyncClient

from src.users.models.models import TagUser
from tests.constants import (
    COMPANY_DATA,
    COMPANY_DATA_TWO,
    TAG_BAD_CREATE_DATA,
    TAG_BAD_UPDATE_DATA,
    TAG_UPDATE_DATA,
    URL,
)
from tests.utils import get_count


class TestTagsPermissions:
    """Тесты проверки прав доступа для работы с тегами"""

    @pytest.mark.asyncio
    async def test_create_tag_non_admin_fails(
        self,
        client: AsyncClient,
        company_for_test,
        employee_of_company,
        get_token_for_user,
    ):
        """Тест: обычный сотрудник не может создавать теги"""
        company = await company_for_test(COMPANY_DATA)
        user = await employee_of_company()
        token = await get_token_for_user(user)
        response = await client.post(
            URL.TAGS_ENDPOINT.format(company_id=company.id),
            headers=token,
            json={'name': 'Test Tag', 'user_id': str(user.id)},
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN, (
            f'Обычный пользователь не должен иметь возможность создавать тэги. '
            f'В ответе ожидается status_code {status.HTTP_403_FORBIDDEN}, '
            f'получен {response.status_code}'
        )
        assert response.json() == {'detail': 'Доступно только админам компаний'}

    @pytest.mark.asyncio
    async def test_create_tag_admin_success(
        self,
        async_session,
        client: AsyncClient,
        company_for_test,
        admin_of_company,
        get_token_for_user,
    ):
        """Тест: администратор может создавать теги"""
        company = await company_for_test(COMPANY_DATA)
        admin = await admin_of_company({'company_id': company.id})
        token = await get_token_for_user(admin)
        old_tags_count = await get_count(async_session, TagUser)
        response = await client.post(
            URL.TAGS_ENDPOINT.format(company_id=company.id),
            headers=token,
            json={'name': 'Test Tag', 'user_id': str(admin.id)},
        )
        assert response.status_code == status.HTTP_201_CREATED, (
            f'Создавать теги должны иметь возможность только админы от компании. '
            f'В ответе ожидается status_code {status.HTTP_201_CREATED}, '
            f'получен {response.status_code}'
        )
        new_tags_count = await get_count(async_session, TagUser)
        assert new_tags_count == old_tags_count + 1


class TestTagsBusinessLogic:
    """Тесты бизнес-логики работы с тегами"""

    @pytest.mark.asyncio
    @pytest.mark.parametrize('payload, expected_status', TAG_BAD_CREATE_DATA)
    async def test_create_tag_validation(
        self,
        client: AsyncClient,
        company_for_test,
        admin_of_company,
        get_token_for_user,
        payload,
        expected_status,
    ):
        """Тест валидации при создании тэга"""
        company = await company_for_test(COMPANY_DATA)
        admin = await admin_of_company({'company_id': company.id})
        token = await get_token_for_user(admin)
        response = await client.post(
            URL.TAGS_ENDPOINT.format(company_id=company.id), headers=token, json=payload
        )
        assert response.status_code == expected_status, (
            f'При создании тэга, возникла ошибка. '
            f'В ответе ожидается status_code {expected_status}, '
            f'получен {response.status_code}'
        )

    @pytest.mark.asyncio
    async def test_get_only_company_tags(
        self,
        client: AsyncClient,
        company_for_test,
        admin_of_company,
        get_token_for_user,
        employee_of_company,
        tag_for_test_with_user,
    ):
        """Тест: при запросе получаем только теги своей компании"""
        company1 = await company_for_test(COMPANY_DATA)
        company2 = await company_for_test(COMPANY_DATA_TWO)
        data = {'company_id': company1.id}
        admin = await admin_of_company(data)
        user = await employee_of_company(data)
        token = await get_token_for_user(admin)
        tag1 = await tag_for_test_with_user(company1, user)
        tag2 = await tag_for_test_with_user(company1, user)
        user2 = await employee_of_company({'company_id': company2.id})
        await tag_for_test_with_user(company2, user2)
        response = await client.get(
            URL.TAGS_ENDPOINT.format(company_id=company1.id),
            headers=token,
        )
        tags = response.json()
        assert response.status_code == status.HTTP_200_OK
        assert len(tags) == 2, (
            f'Админ от компании, не должен видеть теги чужой компании. '
            f'В ответе ожидается status_code {status.HTTP_200_OK}, '
            f'получен {response.status_code}'
        )
        assert {str(tag['id']) for tag in tags} == {str(tag1.id), str(tag2.id)}

    @pytest.mark.asyncio
    async def test_no_tag_duplicates(
        self,
        client: AsyncClient,
        company_for_test,
        admin_of_company,
        get_token_for_user,
        tag_for_test_with_user,
        employee_of_company,
    ):
        """Тест: нельзя создать дубликат тэга в компании"""
        company = await company_for_test(COMPANY_DATA)
        admin = await admin_of_company({'company_id': company.id})
        user = await employee_of_company({'company_id': company.id})
        tag = await tag_for_test_with_user(company, user)

        token = await get_token_for_user(admin)
        response = await client.post(
            URL.TAGS_ENDPOINT.format(company_id=company.id),
            headers=token,
            json={'name': tag.name, 'user_id': str(user.id)},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST, (
            f'При создании тегов в компании, дубликатов быть не должно. '
            f'В ответе ожидается status_code {status.HTTP_400_BAD_REQUEST}, '
            f'получен {response.status_code}'
        )
        assert response.json() == {
            'detail': 'Этот тэг уже используется другим пользователем в этой компании.'
        }


class TestTagsCRUD:
    """Тесты CRUD операций с тегами"""

    @pytest.mark.asyncio
    async def test_update_tag(
        self,
        client: AsyncClient,
        company_for_test,
        admin_of_company,
        get_token_for_user,
        tag_for_test_with_user,
        employee_of_company,
    ):
        """Тест обновления тэга"""
        company = await company_for_test(COMPANY_DATA)
        data = {'company_id': company.id}
        admin = await admin_of_company(data)
        user = await employee_of_company(data)
        tag = await tag_for_test_with_user(company, user)

        token = await get_token_for_user(admin)
        response = await client.patch(
            URL.TAG_DETAIL_ENDPOINT.format(company_id=company.id, tag_id=tag.id),
            headers=token,
            json=TAG_UPDATE_DATA,
        )
        assert response.status_code == status.HTTP_200_OK, (
            f'При обновлении тэга, возникла ошибка. '
            f'В ответе ожидается status_code {status.HTTP_200_OK}, '
            f'получен {response.status_code}'
        )
        assert response.json()['name'] == TAG_UPDATE_DATA['name']

    @pytest.mark.asyncio
    @pytest.mark.parametrize('payload, expected_status', TAG_BAD_UPDATE_DATA)
    async def test_update_tag_validation(
        self,
        client: AsyncClient,
        company_for_test,
        admin_of_company,
        get_token_for_user,
        tag_for_test_with_user,
        employee_of_company,
        payload,
        expected_status,
    ):
        """Тест валидации при обновлении тэга"""
        company = await company_for_test(COMPANY_DATA)
        data = {'company_id': company.id}
        admin = await admin_of_company(data)
        user = await employee_of_company(data)
        tag = await tag_for_test_with_user(company, user)
        token = await get_token_for_user(admin)
        response = await client.patch(
            URL.TAG_DETAIL_ENDPOINT.format(company_id=company.id, tag_id=tag.id),
            headers=token,
            json=payload,
        )
        assert response.status_code == expected_status, (
            f'При обновлении тэга, возникла ошибка. '
            f'В ответе ожидается status_code {expected_status}, '
            f'получен {response.status_code}'
        )

    @pytest.mark.asyncio
    async def test_delete_tag(
        self,
        async_session,
        client: AsyncClient,
        company_for_test,
        admin_of_company,
        get_token_for_user,
        tag_for_test_with_user,
        employee_of_company,
    ):
        """Тест удаления тэга"""
        company = await company_for_test(COMPANY_DATA)
        data = {'company_id': company.id}
        admin = await admin_of_company(data)
        user = await employee_of_company(data)
        tag = await tag_for_test_with_user(company, user)
        token = await get_token_for_user(admin)
        old_tags_count = await get_count(async_session, TagUser)
        response = await client.delete(
            URL.TAG_DETAIL_ENDPOINT.format(company_id=company.id, tag_id=tag.id), headers=token
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT, (
            f'В ответе ожидается status_code {status.HTTP_204_NO_CONTENT}, '
            f'получен {response.status_code}'
        )
        new_tags_count = await get_count(async_session, TagUser)
        assert new_tags_count == old_tags_count - 1

    @pytest.mark.asyncio
    async def test_any_admin_can_modify_tags(
        self,
        client: AsyncClient,
        company_for_test,
        admin_of_company,
        get_token_for_user,
        tag_for_test_with_user,
        employee_of_company,
    ):
        """Тест: любой админ компании может изменять теги"""
        company = await company_for_test(COMPANY_DATA)
        data = {'company_id': company.id}
        admin1 = await admin_of_company(data)  # noqa: F841
        admin2 = await admin_of_company(data)
        user = await employee_of_company(data)
        tag = await tag_for_test_with_user(company, user)
        token = await get_token_for_user(admin2)
        response = await client.patch(
            URL.TAG_DETAIL_ENDPOINT.format(company_id=company.id, tag_id=tag.id),
            headers=token,
            json=TAG_UPDATE_DATA,
        )
        assert response.status_code == status.HTTP_200_OK, (
            f'Любой админ от компании должен иметь возможность изменять теги. '
            f'В ответе ожидается status_code {status.HTTP_200_OK}, '
            f'получен {response.status_code}'
        )
