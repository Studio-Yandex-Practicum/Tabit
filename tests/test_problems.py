import pytest
from fastapi import status
from httpx import AsyncClient

from tests.constants import URL


def get_test_problem_data(all_fields=True):
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
    if all_fields:
        # Подставляется в тесте после создания юзера.
        test_data['members'] = None
        return test_data
    return test_data


class TestCreateProblem:
    """Тесты POST-запросов."""

    @pytest.mark.asyncio
    async def test_create_problem_with_all_fields(self, client: AsyncClient, employee_of_company):
        """
        Тест запроса на создание проблемы со всеми полями.

        Проверяем, что API возвращает 201 статус.
        Проверяем, что ответ содержит корректные значения переданных полей.
        В текущей реализации поле members не возвращается в ответе, поэтому его пропускаем.

        """
        test_owner = await employee_of_company()
        test_member, test_company = await employee_of_company(return_company=True)
        test_data = get_test_problem_data()
        test_data['owner_id'] = f'{test_owner.id}'
        test_data['company_slug'] = test_company.slug
        test_data['members'] = [f'{test_member.id}']
        url = URL.PROBLEMS_ENDPOINT.format(company_slug=test_company.slug)
        response = await client.post(url, json=test_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        for field, expected_value in test_data.items():
            if field == 'members':
                continue
            assert data[field] == expected_value, (
                f"Ожидалось значение поля '{field}': '{expected_value}', получено: '{data[field]}'"
            )

    @pytest.mark.asyncio
    async def test_create_problem_with_only_required_fields(
        self, client: AsyncClient, employee_of_company
    ):
        """
        Тест запроса на создание проблемы только с обязательными полями.

        Проверяем, что API возвращает 201 статус.
        Проверяем, что ответ содержит корректные значения переданных полей.

        """
        test_owner, test_company = await employee_of_company(return_company=True)
        test_data = get_test_problem_data(all_fields=False)
        test_data['owner_id'] = f'{test_owner.id}'
        test_data['company_slug'] = test_company.slug
        url = URL.PROBLEMS_ENDPOINT.format(company_slug=test_company.slug)
        response = await client.post(url, json=test_data)
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        for field, expected_value in test_data.items():
            assert data[field] == expected_value, (
                f"Ожидалось значение поля '{field}': '{expected_value}', получено: '{data[field]}'"
            )

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
        test_data = get_test_problem_data(all_fields=False)
        for field_name in test_data:
            response = await client.post(
                url, json=get_test_problem_data(all_fields=False).pop(field_name)
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
        test_data = get_test_problem_data(all_fields=False)
        test_data['company_slug'] = 'company_that_doesnt_exist'
        test_data['owner_id'] = f'{test_owner.id}'
        url = URL.PROBLEMS_ENDPOINT.format(company_slug='company_that_doesnt_exist')
        response = await client.post(url, json=test_data)
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestGetProblem:
    """Тесты GET-запросов."""

    @pytest.mark.asyncio
    async def test_get_problems_list(
        self, client: AsyncClient, company_for_test, employee_of_company, problem_for_test
    ):
        """
        Тест на получение списка проблем компании.
        Перед запросом создаём в базе 3 проблемы, две из которых принадлежат одной компании.

        Проверяем, что API возвращает 200 статус.
        Проверяем, что возвращаются только проблемы, связанные с компанией.
        Проверяем, что количество объектов в ответе корректно.

        """
        test_owner, test_company = await employee_of_company(return_company=True)
        test_problems_for_one_company = [
            await problem_for_test(
                {'company_slug': test_company.slug, 'owner_id': f'{test_owner.id}'}
            )
            for _ in range(2)
        ]
        _ = await problem_for_test()
        response = await client.get(URL.PROBLEMS_ENDPOINT.format(company_slug=test_company.slug))
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        assert len(response_data) == len(test_problems_for_one_company)
        for problem in response_data:
            assert problem['company_slug'] == test_company.slug

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
            URL.PROBLEM_ENDPOINT.format(
                company_slug=test_problem.company_slug, problem_id=test_problem.id
            )
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
            URL.PROBLEM_ENDPOINT.format(company_slug=test_problem.company_slug, problem_id=0)
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestPatchProblem:
    """Тесты PATCH-запросов."""

    @pytest.mark.asyncio
    async def test_patch_problem_full_update(self, client: AsyncClient, problem_for_test):
        """
        Тест на полное обновление проблемы.
        Перед тестом создаём проблему и создаём словарь данных для обновления.

        Проверяем, что API возвращает статус 200.
        Проверяем, что данные ответа соответствуют данным для обновления.

        """
        test_problem = await problem_for_test()
        data_for_updating = {
            'name': 'обновлённая проблема',
            'description': 'описание обновлённой проблемы',
            'color': 2,
            'status': 'В работе',
            'company_slug': test_problem.company_slug,
        }
        response = await client.patch(
            URL.PROBLEM_ENDPOINT.format(
                company_slug=test_problem.company_slug, problem_id=test_problem.id
            ),
            json=data_for_updating,
        )
        assert response.status_code == status.HTTP_200_OK
        updated_data = response.json()
        for key, value in data_for_updating.items():
            assert updated_data[key] == value

    @pytest.mark.asyncio
    async def test_patch_problem_partial_update(self, client: AsyncClient, problem_for_test):
        """
        Тест на частичное обновление проблемы.
        Перед тестом создаём проблему и создаём словарь данных для обновления.

        Проверяем, что API возвращает статус 200.
        Проверяем, что данные ответа соответствуют данным для обновления."

        """
        test_problem = await problem_for_test()
        data_for_updating = {
            'name': 'обновлённая проблема',
            'description': 'описание обновлённой проблемы',
            'color': 2,
            'status': 'В работе',
        }
        url = URL.PROBLEM_ENDPOINT.format(
            company_slug=test_problem.company_slug, problem_id=test_problem.id
        )
        for key, value in data_for_updating.items():
            response = await client.patch(
                url, json={key: value, 'company_slug': test_problem.company_slug}
            )
            assert response.status_code == status.HTTP_200_OK
            updated_data = response.json()
            assert updated_data[key] == value

    @pytest.mark.asyncio
    async def test_patch_problem_company_doesnt_exist(self, client: AsyncClient, problem_for_test):
        """
        Тест изменения проблемы, если компания не существует.

        Проверяем, что API возвращает 404 статус.

        """
        test_problem = await problem_for_test()
        data_for_updating = {
            'name': 'обновленная проблема',
            'company_slug': test_problem.company_slug,
        }
        response = await client.patch(
            URL.PROBLEM_ENDPOINT.format(
                company_slug='company_that_doesnt_exist', problem_id=test_problem.id
            ),
            json=data_for_updating,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_patch_problem_doesnt_exist(self, client: AsyncClient, problem_for_test):
        """
        Тест изменения проблемы, если проблема не существует.

        Проверяем, что API возвращает 404 статус.

        """
        test_problem = await problem_for_test()
        data_for_updating = {
            'name': 'обновленная проблема',
            'company_slug': test_problem.company_slug,
        }
        response = await client.patch(
            URL.PROBLEM_ENDPOINT.format(company_slug=test_problem.company_slug, problem_id=0),
            json=data_for_updating,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestDeleteProblem:
    """Тесты DELETE-запросов."""

    @pytest.mark.asyncio
    async def test_delete_problem(self, client: AsyncClient, problem_for_test):
        """
        Тест успешного удаления проблемы.

        Проверяем, что API возвращает статус 204.

        """
        test_problem = await problem_for_test()
        response = await client.delete(
            URL.PROBLEM_ENDPOINT.format(
                company_slug=test_problem.company_slug, problem_id=test_problem.id
            )
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.asyncio
    async def test_delete_problem_company_doesnt_exist(
        self, client: AsyncClient, problem_for_test
    ):
        """
        Тест удаления проблемы, если компания не существует.

        Проверяем, что API возвращает статус 404.

        """
        test_problem = await problem_for_test()
        response = await client.delete(
            URL.PROBLEM_ENDPOINT.format(
                company_slug='company_that_doesnt_exist', problem_id=test_problem.id
            )
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_delete_problem_doesnt_exist(self, client: AsyncClient, problem_for_test):
        """
        Тест удаления проблемы, если проблемы не существует.

        Проверяем, что API возвращает статус 404.

        """
        test_problem = await problem_for_test()
        response = await client.delete(
            URL.PROBLEM_ENDPOINT.format(company_slug=test_problem.company_slug, problem_id=0)
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
