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
    }


class TestCreateProblem:
    """Тесты POST-запросов."""

    @pytest.mark.asyncio
    async def test_create_problem_with_members(
        self, client: AsyncClient, employee_of_company, get_token_for_user
    ):
        """
        Тест запроса на создание проблемы с передачей members.

        Проверяем, что API возвращает 201 статус.
        Проверяем, что ответ содержит корректные значения переданных полей.
        Проверяем, что ответ содержит корректные значения автозаполняемых полей.
        Проверяем, что чисто пользотелей в поле members корректно.

        """
        test_owner, test_company = await employee_of_company(return_company=True)
        test_member = await employee_of_company({'company_id': test_company.id})
        test_data = get_test_problem_data()
        test_data['members'] = [f'{test_member.id}']
        url = URL.PROBLEMS_ENDPOINT.format(company_slug=test_company.slug)
        response = await client.post(
            url, json=test_data, headers=await get_token_for_user(test_owner)
        )
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data['name'] == test_data['name']
        assert response_data['description'] == test_data['description']
        assert response_data['color'] == test_data['color']
        assert response_data['type'] == test_data['type']
        assert response_data['status'] == 'Новая'
        assert response_data['owner_id'] == str(test_owner.id)
        assert response_data['company_id'] == test_company.id
        assert len(response_data['members']) == 2

    @pytest.mark.asyncio
    async def test_create_problem_without_members(
        self, client: AsyncClient, employee_of_company, get_token_for_user
    ):
        """
        Тест запроса на создание проблемы без передачи members.

        Проверяем, что API возвращает 201 статус.
        Проверяем, что ответ содержит корректные значения переданных полей.
        Проверяем, что ответ содержит корректные значения автозаполняемых полей.
        Проверяем, что число пользователей в поле members равно одному.
        Проверяем, что id пользователя в поле members равно test_owner.id.

        """
        test_owner, test_company = await employee_of_company(return_company=True)
        test_data = get_test_problem_data()
        url = URL.PROBLEMS_ENDPOINT.format(company_slug=test_company.slug)
        response = await client.post(
            url, json=test_data, headers=await get_token_for_user(test_owner)
        )
        assert response.status_code == status.HTTP_201_CREATED
        response_data = response.json()
        assert response_data['name'] == test_data['name']
        assert response_data['description'] == test_data['description']
        assert response_data['color'] == test_data['color']
        assert response_data['type'] == test_data['type']
        assert response_data['status'] == 'Новая'
        assert response_data['owner_id'] == str(test_owner.id)
        assert response_data['company_id'] == test_company.id
        assert len(response_data['members']) == 1
        assert response_data['members'][0]['member_id'] == str(test_owner.id)

    @pytest.mark.asyncio
    async def test_create_problem_without_required_field(
        self, client: AsyncClient, employee_of_company, get_token_for_user
    ):
        """
        Тест запроса на создание проблемы без передачи обязательного поля.

        Проверяем, что API возвращает 422 статус.

        """
        test_owner, test_company = await employee_of_company(return_company=True)
        url = URL.PROBLEMS_ENDPOINT.format(company_slug=test_company.slug)
        test_data = get_test_problem_data()
        for field_name in test_data:
            response = await client.post(
                url,
                json=get_test_problem_data().pop(field_name),
                headers=await get_token_for_user(test_owner),
            )
            assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    @pytest.mark.asyncio
    async def test_create_problem_if_company_doesnt_exist(
        self, client: AsyncClient, employee_of_company, get_token_for_user
    ):
        """
        Тест запроса на создание проблемы, если компания не существует.

        Проверяем, что API возвращает 404 статус.

        """
        test_owner = await employee_of_company()
        test_data = get_test_problem_data()
        url = URL.PROBLEMS_ENDPOINT.format(company_slug='company_that_doesnt_exist')
        response = await client.post(
            url, json=test_data, headers=await get_token_for_user(test_owner)
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_create_problem_if_user_unauthorized(
        self,
        client: AsyncClient,
        company_for_test,
    ):
        """
        Тест запроса на создание проблемы неавторизованным пользователем.

        Проверяем, что API возвращает 401 статус.

        """
        test_company = await company_for_test()
        test_data = get_test_problem_data()
        url = URL.PROBLEMS_ENDPOINT.format(company_slug=test_company.slug)
        response = await client.post(url, json=test_data)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_create_problem_if_user_not_from_company(
        self, client: AsyncClient, company_for_test, employee_of_company, get_token_for_user
    ):
        """
        Тест создания проблемы, если пользователь не является сотрудником компании.

        Проверяем, что API возвращает 403 статус.
        """
        test_company = await company_for_test()
        test_user = await employee_of_company()
        test_data = get_test_problem_data()
        url = URL.PROBLEMS_ENDPOINT.format(company_slug=test_company.slug)
        response = await client.post(
            url, json=test_data, headers=await get_token_for_user(test_user)
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    # TODO: пока закомменчено, так как данная валидация не работает.
    # @pytest.mark.asyncio
    # async def test_create_problem_if_member_not_from_company(
    #     self,
    #     client: AsyncClient,
    #     employee_of_company,
    #     get_token_for_user
    # ):
    #     """
    #     Тест создания проблемы с передачей в members пользотвалея,
    #     не являющегося сотрудником компании.

    #     Проверяем, что API возвращает 400 статус.
    #     """
    #     test_owner, test_company = await employee_of_company(return_company=True)
    #     user_not_from_company = await employee_of_company()
    #     test_data = get_test_problem_data()
    #     test_data['members'] = [f'{user_not_from_company.id}']
    #     url = URL.PROBLEMS_ENDPOINT.format(company_slug=test_company.slug)
    #     response = await client.post(
    #         url,
    #         json=test_data,
    #         headers=await get_token_for_user(test_owner)
    #         )
    #     assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestGetProblem:
    """Тесты GET-запросов."""

    @pytest.mark.asyncio
    async def test_get_problems_list(
        self, client: AsyncClient, employee_of_company, problem_for_test, get_token_for_user
    ):
        """
        Тест на получение списка проблем компании.
        Перед запросом создаём в базе 3 проблемы, две из которых принадлежат одной компании.

        Проверяем, что API возвращает 200 статус.
        Проверяем, что возвращаются только проблемы, связанные с компанией.
        Проверяем, что количество проблем в ответе корректно.

        """
        test_owner, test_company = await employee_of_company(return_company=True)
        test_problems_for_one_company = [
            await problem_for_test({'company_id': test_company.id, 'owner_id': f'{test_owner.id}'})
            for _ in range(2)
        ]
        await problem_for_test()
        response = await client.get(
            URL.PROBLEMS_ENDPOINT.format(company_slug=test_company.slug),
            headers=await get_token_for_user(test_owner),
        )
        assert response.status_code == status.HTTP_200_OK
        expected_fields = {
            'id',
            'name',
            'description',
            'color',
            'type',
            'status',
            'owner_id',
            'company_id',
            'members',
            'created_at',
            'updated_at',
        }
        response_data = response.json()
        assert len(response_data) == len(test_problems_for_one_company)
        for problem in response_data:
            assert problem['company_id'] == test_company.id
            for field in problem:
                assert field in expected_fields

    @pytest.mark.asyncio
    async def test_get_problems_company_doesnt_exists(
        self, client: AsyncClient, employee_of_company, get_token_for_user
    ):
        """
        Тест на получение списка проблем несуществующей компании.

        Проверяем, что API возвращает 404 статус.

        """
        test_user = await employee_of_company()
        response = await client.get(
            URL.PROBLEMS_ENDPOINT.format(company_slug='company_that_doesnt_exist'),
            headers=await get_token_for_user(test_user),
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_get_problems_list_user_unauthorized(
        self, client: AsyncClient, problem_for_test
    ):
        """
        Тест запроса на получение списка проблем неавторизованным пользователем.

        Проверям, что API возвращает 401 статус.

        """
        _, _, test_company = await problem_for_test(return_all_objects=True)
        response = await client.get(URL.PROBLEMS_ENDPOINT.format(company_slug=test_company.slug))
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_get_problems_list_user_not_from_company(
        self, client: AsyncClient, problem_for_test, employee_of_company, get_token_for_user
    ):
        """
        Тест запроса на списка проблем, если пользователь не сотрудник компании,
        которой принадлежит проблема.

        Проверяем, что API возвращает статус 403.
        """
        _, _, test_company = await problem_for_test(return_all_objects=True)
        test_user = await employee_of_company()
        response = await client.get(
            URL.PROBLEMS_ENDPOINT.format(company_slug=test_company.slug),
            headers=await get_token_for_user(test_user),
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_get_single_problem(
        self, client: AsyncClient, problem_for_test, get_token_for_user
    ):
        """
        Тест на получение отдельной проблемы.

        Проверяем, что API возвращает статус 200.
        Проверяем, что ответ содержит ожидаемые поля.

        """
        test_problem, test_employee, test_company = await problem_for_test(return_all_objects=True)
        expected_fields = {
            'id',
            'name',
            'description',
            'color',
            'type',
            'status',
            'owner_id',
            'company_id',
            'members',
            'created_at',
            'updated_at',
        }
        response = await client.get(
            URL.PROBLEM_ENDPOINT.format(
                company_slug=test_company.slug, problem_id=test_problem.id
            ),
            headers=await get_token_for_user(test_employee),
        )
        assert response.status_code == status.HTTP_200_OK
        response_data = response.json()
        for field in response_data:
            assert field in expected_fields

    @pytest.mark.asyncio
    async def test_get_non_existing_problem(
        self, client: AsyncClient, problem_for_test, get_token_for_user
    ):
        """
        Тест получения отдельной проблемы по несуществующему id.

        Проверяем, что API возвращает статус 404.

        """
        _, test_user, test_company = await problem_for_test(return_all_objects=True)
        response = await client.get(
            URL.PROBLEM_ENDPOINT.format(company_slug=test_company.slug, problem_id=0),
            headers=await get_token_for_user(test_user),
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_get_problem_company_doesnt_exist(
        self, client: AsyncClient, problem_for_test, get_token_for_user
    ):
        """
        Тест получения отдельной проблемы, если компания не существует.

        Проверяем, что API возвращает статус 404.

        """
        test_problem, test_user, _ = await problem_for_test(return_all_objects=True)
        response = await client.get(
            URL.PROBLEM_ENDPOINT.format(
                company_slug='company_doesnt_exist', problem_id=test_problem.id
            ),
            headers=await get_token_for_user(test_user),
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_get_problem_user_unauthorized(self, client: AsyncClient, problem_for_test):
        """
        Тест запроса на получение отдельной проблемы неавторизованным пользователем.

        Проверям, что API возвращает 401 статус.

        """
        test_problem, _, test_company = await problem_for_test(return_all_objects=True)
        response = await client.get(
            URL.PROBLEM_ENDPOINT.format(company_slug=test_company.slug, problem_id=test_problem.id)
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_get_single_problem_user_not_from_company(
        self, client: AsyncClient, problem_for_test, employee_of_company, get_token_for_user
    ):
        """
        Тест запроса на получение проблемы, если пользователь не сотрудник компании,
        которой принадлежит проблема.

        Проверяем, что API возвращает статус 403.
        """
        test_problem, _, test_company = await problem_for_test(return_all_objects=True)
        test_user = await employee_of_company()
        response = await client.get(
            URL.PROBLEMS_ENDPOINT.format(
                company_slug=test_company.slug, problem_id=test_problem.id
            ),
            headers=await get_token_for_user(test_user),
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN


class TestPatchProblem:
    """Тесты PATCH-запросов."""

    @pytest.mark.asyncio
    async def test_patch_problem_full_update(
        self, client: AsyncClient, problem_for_test, employee_of_company, get_token_for_user
    ):
        """
        Тест на полное обновление проблемы.
        Перед тестом создаём проблему и создаём словарь данных для обновления.

        Проверяем, что API возвращает статус 200.
        Проверяем, что данные ответа соответствуют данным для обновления.

        # TODO: Добавить проверку обновления поля members, если передаём несколько человек.
                В текущей реализации не работает.

        """
        test_problem, test_owner, test_company = await problem_for_test(return_all_objects=True)
        member_for_updating = await employee_of_company({'company_id': test_company.id})
        data_for_updating = {
            'name': 'обновлённая проблема',
            'description': 'описание обновлённой проблемы',
            'color': 2,
            'status': 'В работе',
            'type': 'Взаимодействие в коллективе',
            'members': [str(member_for_updating.id)],
        }
        response = await client.patch(
            URL.PROBLEM_ENDPOINT.format(
                company_slug=test_company.slug, problem_id=test_problem.id
            ),
            json=data_for_updating,
            headers=await get_token_for_user(test_owner),
        )
        assert response.status_code == status.HTTP_200_OK
        updated_data = response.json()
        for key, value in data_for_updating.items():
            if key == 'members':
                assert len(updated_data[key]) == 2
                continue
            assert updated_data[key] == value

    @pytest.mark.asyncio
    async def test_patch_problem_partial_update(
        self, client: AsyncClient, problem_for_test, employee_of_company, get_token_for_user
    ):
        """
        Тест на частичное обновление проблемы.
        Перед тестом создаём проблему и словарь данных для обновления.

        Проверяем, что API возвращает статус 200.
        Проверяем, что данные ответа соответствуют данным для обновления."

        # TODO: Добавить проверку обновления поля members, если передаём несколько человек.
                В текущей реализации не работает.

        """
        test_problem, test_owner, test_company = await problem_for_test(return_all_objects=True)
        member_for_updating = await employee_of_company({'company_id': test_company.id})
        data_for_updating = {
            'name': 'обновлённая проблема',
            'description': 'описание обновлённой проблемы',
            'color': 2,
            'status': 'В работе',
            'type': 'Взаимодействие в коллективе',
            'members': [str(member_for_updating.id)],
        }
        url = URL.PROBLEM_ENDPOINT.format(
            company_slug=test_company.slug,
            problem_id=test_problem.id,
        )
        for key, value in data_for_updating.items():
            response = await client.patch(
                url, json={key: value}, headers=await get_token_for_user(test_owner)
            )
            assert response.status_code == status.HTTP_200_OK
            updated_data = response.json()
            if key == 'members':
                assert len(updated_data[key]) == 2
                continue
            assert updated_data[key] == value

    @pytest.mark.asyncio
    async def test_patch_problem_company_doesnt_exist(
        self, client: AsyncClient, problem_for_test, get_token_for_user
    ):
        """
        Тест изменения проблемы, если компания не существует.

        Проверяем, что API возвращает 404 статус.

        """
        test_problem, test_owner, _ = await problem_for_test(return_all_objects=True)
        data_for_updating = {'name': 'обновленная проблема'}
        response = await client.patch(
            URL.PROBLEM_ENDPOINT.format(
                company_slug='company_that_doesnt_exist', problem_id=test_problem.id
            ),
            json=data_for_updating,
            headers=await get_token_for_user(test_owner),
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_patch_problem_doesnt_exist(
        self, client: AsyncClient, problem_for_test, get_token_for_user
    ):
        """
        Тест изменения проблемы, если проблема не существует.

        Проверяем, что API возвращает 404 статус.

        """
        _, test_owner, test_company = await problem_for_test(return_all_objects=True)
        data_for_updating = {'name': 'обновленная проблема'}
        response = await client.patch(
            URL.PROBLEM_ENDPOINT.format(company_slug=test_company.slug, problem_id=0),
            json=data_for_updating,
            headers=await get_token_for_user(test_owner),
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_update_problem_if_user_not_from_company(
        self, client: AsyncClient, problem_for_test, employee_of_company, get_token_for_user
    ):
        """
        Тест обновления проблемы, если пользователь не является сотрудником компании.

        Проверяем, что API возвращает 403 статус.
        """
        test_problem, _, test_company = await problem_for_test(return_all_objects=True)
        test_user = await employee_of_company()
        data_for_updating = {'name': 'обновлённая проблема'}
        url = URL.PROBLEM_ENDPOINT.format(
            company_slug=test_company.slug, problem_id=test_problem.id
        )
        response = await client.patch(
            url, json=data_for_updating, headers=await get_token_for_user(test_user)
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_update_problem_if_user_not_author(
        self, client: AsyncClient, problem_for_test, employee_of_company, get_token_for_user
    ):
        """
        Тест обновления проблемы, если пользователь не является автором проблемы.

        Проверяем, что API возвращает 403 статус.
        """
        test_problem, _, test_company = await problem_for_test(return_all_objects=True)
        test_user = await employee_of_company({'company_id': test_company.id})
        data_for_updating = {'name': 'обновлённая проблема'}
        url = URL.PROBLEM_ENDPOINT.format(
            company_slug=test_company.slug, problem_id=test_problem.id
        )
        response = await client.patch(
            url, json=data_for_updating, headers=await get_token_for_user(test_user)
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_update_problem_if_problem_completed(
        self, client: AsyncClient, problem_for_test, employee_of_company, get_token_for_user
    ):
        """
        Тест запроса на обновление проблемы, если проблема уже завершена.

        Проверяем, что API возвращает 422 статус.
        """
        test_owner, test_company = await employee_of_company(return_company=True)
        test_problem = await problem_for_test(
            {'status': 'Завершена', 'owner_id': test_owner.id, 'company_id': test_company.id}
        )
        data_for_updating = {'name': 'обновлённая проблема'}
        url = url = URL.PROBLEM_ENDPOINT.format(
            company_slug=test_company.slug, problem_id=test_problem.id
        )
        response = await client.patch(
            url, json=data_for_updating, headers=await get_token_for_user(test_owner)
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestDeleteProblem:
    """Тесты DELETE-запросов."""

    @pytest.mark.asyncio
    async def test_delete_problem(self, client: AsyncClient, problem_for_test, get_token_for_user):
        """
        Тест успешного удаления проблемы.

        Проверяем, что API возвращает статус 204.

        """
        test_problem, test_owner, test_company = await problem_for_test(return_all_objects=True)
        response = await client.delete(
            URL.PROBLEM_ENDPOINT.format(
                company_slug=test_company.slug, problem_id=test_problem.id
            ),
            headers=await get_token_for_user(test_owner),
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT

    @pytest.mark.asyncio
    async def test_delete_problem_company_doesnt_exist(
        self, client: AsyncClient, problem_for_test, get_token_for_user
    ):
        """
        Тест удаления проблемы, если компания не существует.

        Проверяем, что API возвращает статус 404.

        """
        test_problem, test_owner, _ = await problem_for_test(return_all_objects=True)
        response = await client.delete(
            URL.PROBLEM_ENDPOINT.format(
                company_slug='company_that_doesnt_exist', problem_id=test_problem.id
            ),
            headers=await get_token_for_user(test_owner),
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_delete_problem_doesnt_exist(
        self, client: AsyncClient, problem_for_test, get_token_for_user
    ):
        """
        Тест удаления проблемы, если проблемы не существует.

        Проверяем, что API возвращает статус 404.

        """
        _, test_owner, test_company = await problem_for_test(return_all_objects=True)
        response = await client.delete(
            URL.PROBLEM_ENDPOINT.format(company_slug=test_company.slug, problem_id=0),
            headers=await get_token_for_user(test_owner),
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_delete_problem_by_unauthorized_user(
        self, client: AsyncClient, problem_for_test
    ):
        """
        Тест запроса на удаление проблемы неавторизованным пользователем.

        Проверяем, что API возвращает 401 статус
        """
        test_problem, _, test_company = await problem_for_test(return_all_objects=True)
        response = await client.delete(
            URL.PROBLEM_ENDPOINT.format(company_slug=test_company.slug, problem_id=test_problem.id)
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    @pytest.mark.asyncio
    async def test_delete_problem_user_not_from_company(
        self, client: AsyncClient, problem_for_test, employee_of_company, get_token_for_user
    ):
        """
        Тест запроса на удаление проблемы, если пользователь не является сотрудником компании.

        Проверяем, что API возвращает 403 статус.
        """
        test_problem, _, test_company = await problem_for_test(return_all_objects=True)
        user_not_from_company = await employee_of_company()
        response = await client.delete(
            URL.PROBLEM_ENDPOINT.format(
                company_slug=test_company.slug, problem_id=test_problem.id
            ),
            headers=await get_token_for_user(user_not_from_company),
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_delete_problem_if_user_not_author(
        self, client: AsyncClient, problem_for_test, employee_of_company, get_token_for_user
    ):
        """
        Запрос на удаление проблемы от пользователя, не являющегося её создателем.

        Проверяем, что API возвращает 403 статус.
        """
        test_problem, _, test_company = await problem_for_test(return_all_objects=True)
        not_author_user = await employee_of_company()
        response = await client.delete(
            URL.PROBLEM_ENDPOINT.format(
                company_slug=test_company.slug, problem_id=test_problem.id
            ),
            headers=await get_token_for_user(not_author_user),
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    @pytest.mark.asyncio
    async def test_delete_problem_if_problem_completed(
        self, client: AsyncClient, problem_for_test, employee_of_company, get_token_for_user
    ):
        """
        Тест запроса на удаление проблемы, если она уже завершена.

        Проверяем, что API возвращает 422 статус.
        """
        test_owner, test_company = await employee_of_company(return_company=True)
        test_problem = await problem_for_test(
            {'status': 'Завершена', 'owner_id': test_owner.id, 'company_id': test_company.id}
        )
        response = await client.delete(
            URL.PROBLEM_ENDPOINT.format(
                company_slug=test_company.slug, problem_id=test_problem.id
            ),
            headers=await get_token_for_user(test_owner),
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
