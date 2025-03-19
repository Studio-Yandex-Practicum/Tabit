import pytest
from fastapi import status
from httpx import AsyncClient

from tests.constants import URL


def get_test_problem_data(with_members=True):
    """Возвращает шаблон данных для запроса на создание проблемы."""
    test_data = {
        'name': 'Тестовая проблема',
        'description': 'В чём смысл бытия?',
        'color': 1,
        'type': 'Взаимодействие в коллективе',
        'status': 'Новая',
        'owner_id': None,  # Подставляется в тесте после создания юзера.
        'company_slug': None,  # Подставляется в тесте после создания company.
    }
    if with_members:
        # Подставляется в тесте после создания юзера.
        test_data['members'] = None
        return test_data
    return test_data


class TestCreateProblem:
    """Тесты POST-запросов."""

    @pytest.mark.asyncio
    async def test_create_problem_with_members(
        self, client: AsyncClient, company_for_test, employee_of_company
    ):
        """
        Тест запроса на создание проблемы с передачей members.

        Проверяем, что API возвращает 201 статус.
        Проверяем, что ответ содержит корректные значения переданных полей.

        """
        test_company = await company_for_test()
        test_owner = await employee_of_company()
        test_member = await employee_of_company()
        test_data = get_test_problem_data()
        test_data['owner_id'] = f'{test_owner.id}'
        test_data['company_slug'] = test_company.slug
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
        assert response_data['company_slug'] == test_data['company_slug']

    @pytest.mark.asyncio
    async def test_create_problem_without_members(
        self, client: AsyncClient, company_for_test, employee_of_company
    ):
        """
        Тест запроса на создание проблемы без передачи members.

        Проверяем, что API возвращает 201 статус.
        Проверяем, что ответ содержит корректные значения переданных полей.

        """
        test_company = await company_for_test()
        test_owner = await employee_of_company()
        test_data = get_test_problem_data(with_members=False)
        test_data['owner_id'] = f'{test_owner.id}'
        test_data['company_slug'] = test_company.slug
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
        assert response_data['company_slug'] == test_data['company_slug']

    @pytest.mark.asyncio
    async def test_create_problem_without_required_field(
        self, client: AsyncClient, company_for_test
    ):
        """
        Тест запроса на создание проблемы без передачи обязательного поля.

        Проверяем, что API возвращает 422 статус.

        """
        test_company = await company_for_test()
        url = URL.PROBLEMS_ENDPOINT.format(company_slug=test_company.slug)
        test_data = get_test_problem_data(with_members=False)
        for field_name in test_data:
            response = await client.post(
                url, json=get_test_problem_data(with_members=False).pop(field_name)
            )
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
        test_data = get_test_problem_data(with_members=False)
        test_data['company_slug'] = 'company_that_doesnt_exist'
        test_data['owner_id'] = f'{test_owner.id}'
        url = URL.PROBLEMS_ENDPOINT.format(company_slug='company_that_doesnt_exist')
        response = await client.post(url, json=test_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGetProblem:
    """Тесты GET-запросов."""

    @pytest.mark.asyncio
    async def test_get_problems_list(self, client: AsyncClient, problem_for_test):
        """
        Тест на получение списка проблем компании.
        Перед запросом создаём в базе 3 проблемы, 2 из которых связаны с одной компанией.

        Проверяем, что API возвращает 200 статус.
        Проверяем, что возвращаются только проблемы, связанные с компанией.
        Проверяем, что количество объектов в ответе корректно.

        """
        test_problem = await problem_for_test()
        _ = await problem_for_test(custom_company_slug=test_problem.company_slug)
        _ = await problem_for_test()
        response = await client.get(
            URL.PROBLEMS_ENDPOINT.format(company_slug=test_problem.company_slug)
        )
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data) == 2
        for problem in response_data:
            assert problem['company_slug'] == test_problem.company_slug

    @pytest.mark.asyncio
    async def test_get_problems_company_doesnt_exists(self, client: AsyncClient):
        """
        Тест на получение списка проблем несуществующей компании.

        Проверяем, что API возвращает 404 статус.
        """
        response = await client.get(
            URL.PROBLEMS_ENDPOINT.format(company_slug='company_that_doesnt_exist')
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_get_single_problem(self, client: AsyncClient, problem_for_test):
        """
        Тест на получение отдельной проблемы.

        Проверяем, что API возвращает статус 200.
        Проверяем, что ответ содержит ожидаемые поля.
        """
        test_problem = await problem_for_test()
        expected_fields = {
            'id',
            'name',
            'description',
            'color',
            'type',
            'status',
            'owner_id',
            'company_slug',
            'created_at',
            'updated_at',
        }
        response = await client.get(
            URL.PROBLEMS_ENDPOINT.format(company_slug=test_problem.company_slug)
            + f'/{test_problem.id}'
        )
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        for field in response_data:
            assert field in expected_fields

    @pytest.mark.asyncio
    async def test_get_non_existing_problem(self, client: AsyncClient, problem_for_test):
        """
        Тест получения отдельной проблемы по несуществующему id.

        Проверяем, что API возвращает статус 404.
        """
        test_problem = await problem_for_test()
        response = await client.get(
            URL.PROBLEMS_ENDPOINT.format(company_slug=test_problem.company_slug) + '/2'
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
