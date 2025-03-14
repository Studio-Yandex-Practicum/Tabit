import pytest
from fastapi import status
from httpx import AsyncClient

from tests.constants import URL


def get_test_problem_data():
    """Возвращает шаблон данных для запроса на создание проблемы."""
    return {
        'name': 'Тестовая проблема',
        'description': 'В чём смысл бытия?',
        'color': 1,
        'type': 'Взаимодействие в коллективе',
        'status': 'Новая',
        'owner_id': None,  # Подставляется в тесте после создания owner.
        'company_id': None,  # Подставляется в тесте после создания company.
        'members': None,  # Подставляется в тесте после создания member.
    }


class TestCreateProblem:
    """Тесты POST-запросов."""

    @pytest.mark.asyncio
    async def test_create_problem(
        self, client: AsyncClient, company_for_test, employee_of_company
    ):
        """
        Тест запроса на создание проблемы.

        Убеждаемся, что API возвращает 201 статус.
        Проверяем, что ответ содержит корректные значения переданных полей.

        В текущей реализации проекта все поля обязательны для заполнения.
        """
        test_company = await company_for_test()
        test_owner = await employee_of_company()
        test_member = await employee_of_company()
        test_data = get_test_problem_data()
        test_data['owner_id'] = f'{test_owner.id}'
        test_data['company_id'] = test_company.id
        test_data['members'] = [f'{test_member.id}']
        url = URL.PROBLEMS_ENDPOINT.format(company_slug=test_company.slug)
        response = await client.post(url, json=test_data)
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data['name'] == test_data['name']
        assert response_data['description'] == test_data['description']
        assert response_data['color'] == test_data['color']
        assert response_data['type'] == test_data['type']
        assert response_data['status'] == test_data['status']
        assert response_data['owner_id'] == test_data['owner_id']
        assert response_data['company_id'] == test_data['company_id']

    @pytest.mark.asyncio
    async def test_create_problem_without_required_field(
        self, client: AsyncClient, company_for_test
    ):
        """
        Тест запроса на создание проблемы без обязательного поля.
        В текущей реализации проекта все поля обязательны.

        Проверяем, что если какое-то поле не передано, API возвращает 422 статус.
        """
        test_company = await company_for_test()
        url = URL.PROBLEMS_ENDPOINT.format(company_slug=test_company.slug)
        test_data = get_test_problem_data()
        for field_name in test_data:
            response = await client.post(url, json=get_test_problem_data().pop(field_name))
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_create_problem_if_company_doesnt_exist(
        self, client: AsyncClient, employee_of_company
    ):
        """
        Тест запроса на создание проблемы, если компания не существует.

        Проверяем, что API возвращает 404 статус.
        """
        test_owner = await employee_of_company()
        test_member = await employee_of_company()
        test_data = get_test_problem_data()
        test_data['company_id'] = 1
        test_data['owner_id'] = f'{test_owner.id}'
        test_data['members'] = [f'{test_member.id}']
        url = URL.PROBLEMS_ENDPOINT.format(company_slug='ooo_company_doesnt_exist')
        response = await client.post(url, json=test_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGetProblem:
    """Тесты GET-запросов."""
