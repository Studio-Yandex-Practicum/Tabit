import random
import string
from datetime import datetime, timedelta

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models import AssociationUserProblem
from tests.conftest import make_entry_in_table
from tests.constants import UrlConstants


def generate_task_data(problem_id=None, owner_id=None, executors=None, all_fields=False):
    """Генерирует реалистичные данные для создания задач."""

    def random_string(length):
        """Генерирует случайную строку указанной длины."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    data = {
        'name': f'Задача {random_string(7)}',
        'date_completion': (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d'),
    }
    if all_fields:
        data.update(
            {
                'description': f'Описание задачи: {random_string(15)}',
            }
        )
    if executors:
        data.update({'executors': executors})
    return data


class TestTasksPost:
    """Тесты POST-запросов."""

    @pytest.mark.asyncio
    async def test_create_task_without_employee_executors(
        self,
        client: AsyncClient,
        problem_for_test,
        get_token_for_user,
    ):
        """Запрос на создание задачи без исполнителей."""
        problem, employee_owner, company = await problem_for_test(return_all_objects=True)
        task_data = generate_task_data(all_fields=True)
        response = await client.post(
            UrlConstants.TASKS_ENDPOINT.format(company_slug=company.slug, problem_id=problem.id),
            json=task_data,
            headers=await get_token_for_user(employee_owner),
        )

        response_data = response.json()
        assert response.status_code == status.HTTP_201_CREATED, response_data
        for key, value in task_data.items():
            assert response_data[key] == value, response_data

    @pytest.mark.asyncio
    async def test_create_task_with_all_fields(
        self,
        client: AsyncClient,
        problem_for_test,
        get_token_for_user,
        employee_of_company,
        async_session: AsyncSession,
    ):
        """Запрос на создание задачи со всеми полями."""
        problem, employee_owner, company = await problem_for_test(return_all_objects=True)
        # Создание исполнителя для задачи и занесение его в участики проблемы.
        employee_executor = await employee_of_company({'company_id': company.id})
        executor_problem_data = {'left_id': str(employee_executor.id), 'right_id': problem.id}
        await make_entry_in_table(async_session, executor_problem_data, AssociationUserProblem)
        task_data = generate_task_data(executors=[f'{employee_executor.id}'], all_fields=True)
        response = await client.post(
            UrlConstants.TASKS_ENDPOINT.format(company_slug=company.slug, problem_id=problem.id),
            json=task_data,
            headers=await get_token_for_user(employee_owner),
        )

        response_data = response.json()
        assert response.status_code == status.HTTP_201_CREATED, response_data
        for key, value in task_data.items():
            if key == 'executors':
                for executor in value:
                    assert executor in response_data[key][0].values(), response_data
            else:
                assert response_data[key] == value, response_data

    @pytest.mark.asyncio
    async def test_create_task_with_requared_fields(
        self,
        client: AsyncClient,
        problem_for_test,
        get_token_for_user,
    ):
        """Запрос на создание задачи только с обязательными полями."""
        problem, employee_owner, company = await problem_for_test(return_all_objects=True)
        task_data = generate_task_data()
        response = await client.post(
            UrlConstants.TASKS_ENDPOINT.format(company_slug=company.slug, problem_id=problem.id),
            json=task_data,
            headers=await get_token_for_user(employee_owner),
        )

        response_data = response.json()
        assert response.status_code == status.HTTP_201_CREATED, response_data
        for key, value in task_data.items():
            assert response_data[key] == value, response_data

    @pytest.mark.asyncio
    async def test_create_task_without_company_or_problem(
        self,
        client: AsyncClient,
        problem_for_test,
        get_token_for_user,
    ):
        """Запрос на создание задачи c несуществующей компанией или проблемой."""
        problem, employee_owner, company = await problem_for_test(return_all_objects=True)
        variants = (
            (
                problem.id,
                invalid_slug := 'No-way-company',
                status.HTTP_404_NOT_FOUND,
                {'detail': f'Не найден объект Company по данному slug: {invalid_slug}'},
            ),
            (
                problem.id + 1,
                company.slug,
                status.HTTP_404_NOT_FOUND,
                {'detail': f'Не найден объект Problem по данному id: {problem.id + 1}'},
            ),
        )
        for problem_id, company_slug, status_code, detail in variants:
            task_data = generate_task_data()
            response = await client.post(
                UrlConstants.TASKS_ENDPOINT.format(
                    company_slug=company_slug, problem_id=problem_id
                ),
                json=task_data,
                headers=await get_token_for_user(employee_owner),
            )
            assert response.status_code == status_code, response.json()
            assert response.json() == detail


class TestTasksGet:
    """Тесты GET-запросов."""

    @pytest.mark.asyncio
    async def test_get_all_tasks_by_problem(
        self,
        client: AsyncClient,
        task_for_test,
        get_token_for_user,
    ):
        """Запрос на получение списка задач по проблеме."""
        task, problem, employee_owner, company = await task_for_test(return_all_objects=True)
        task_data = [task]
        task_data.extend(
            [
                await task_for_test({'problem_id': problem.id, 'owner_id': employee_owner.id})
                for _ in range(3)
            ]
        )
        response = await client.get(
            UrlConstants.TASKS_ENDPOINT.format(company_slug=company.slug, problem_id=problem.id),
            headers=await get_token_for_user(employee_owner),
        )

        response_data = response.json()
        assert response.status_code == status.HTTP_200_OK, response_data
        assert isinstance(response_data, list), response_data
        assert len(response_data) == len(task_data), response_data

    @pytest.mark.asyncio
    async def test_get_single_task_info(
        self,
        client: AsyncClient,
        task_for_test,
        get_token_for_user,
    ):
        """Запрос на получение информации о конкретной задаче."""
        task, problem, employee_owner, company = await task_for_test(return_all_objects=True)
        response = await client.get(
            UrlConstants.TASK_ENDPOINT.format(
                company_slug=company.slug,
                problem_id=problem.id,
                task_id=task.id,
            ),
            headers=await get_token_for_user(employee_owner),
        )

        response_data = response.json()
        assert response.status_code == status.HTTP_200_OK, response_data
        assert response_data['id'] == task.id, response_data
        assert response_data['name'] == task.name, response_data
        assert response_data['date_completion'] == task.date_completion.isoformat(), response_data
        assert response_data['status'] == task.status, response_data

    @pytest.mark.asyncio
    async def test_get_tasks_without_tasks(
        self,
        client: AsyncClient,
        problem_for_test,
        get_token_for_user,
    ):
        """Запрос на получение задач при их отсутствии."""
        problem, employee, company = await problem_for_test(return_all_objects=True)
        response = await client.get(
            UrlConstants.TASKS_ENDPOINT.format(company_slug=company.slug, problem_id=problem.id),
            headers=await get_token_for_user(employee),
        )

        response_data = response.json()
        assert response.status_code == status.HTTP_200_OK, response_data
        assert isinstance(response_data, list), response_data
        assert not len(response_data), response_data


class TestTasksUpdate:
    """Тесты PATCH-запросов."""

    @pytest.mark.asyncio
    async def test_patch_task_full_update(
        self,
        client: AsyncClient,
        task_for_test,
        get_token_for_user,
        employee_of_company,
        async_session: AsyncSession,
    ):
        """Запрос на полное обновление всех полей задачи."""
        task, problem, employee_owner, company = await task_for_test(return_all_objects=True)
        # Создание исполнителя для задачи и занесение его в участики проблемы.
        employee_executor = await employee_of_company({'company_id': company.id})
        executor_problem_data = {'left_id': str(employee_executor.id), 'right_id': problem.id}
        await make_entry_in_table(async_session, executor_problem_data, AssociationUserProblem)
        updated_data = {
            'name': 'Updated name',
            'date_completion': (datetime.now() + timedelta(days=10)).date().isoformat(),
            'description': 'Updated description',
            'status': 'В работе',
            'executors': [str(employee_executor.id)],
        }
        response = await client.patch(
            UrlConstants.TASK_ENDPOINT.format(
                company_slug=company.slug, problem_id=problem.id, task_id=task.id
            ),
            json=updated_data,
            headers=await get_token_for_user(employee_owner),
        )

        response_data = response.json()
        assert response.status_code == status.HTTP_200_OK, response_data
        assert response_data['transfer_counter'] == 1, response_data
        for key, value in updated_data.items():
            if key == 'executors':
                for executor in value:
                    assert executor in response_data[key][0].values(), response_data
            else:
                assert response_data[key] == value, response_data

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'field, value',
        [
            ('name', 'Updated name'),
            ('description', 'Updated description'),
            ('date_completion', (datetime.now() + timedelta(days=10)).date().isoformat()),
            ('status', 'В работе'),
            ('executors', ['employee_executor_id']),
        ],
    )
    async def test_patch_task_partial_update(
        self,
        client: AsyncClient,
        task_for_test,
        field,
        value,
        get_token_for_user,
        employee_of_company,
        async_session: AsyncSession,
    ):
        """Запрос обновление каждого из полей задачи отдельно."""
        task, problem, employee_owner, company = await task_for_test(return_all_objects=True)
        # Создание исполнителя для задачи и занесение его в участики проблемы.
        employee_executor = await employee_of_company({'company_id': company.id})
        executor_problem_data = {'left_id': str(employee_executor.id), 'right_id': problem.id}
        await make_entry_in_table(async_session, executor_problem_data, AssociationUserProblem)
        if not isinstance(value, list):
            json = {field: value}
        else:
            json = {field: [str(employee_executor.id)]}
        response = await client.patch(
            UrlConstants.TASK_ENDPOINT.format(
                company_slug=company.slug, problem_id=problem.id, task_id=task.id
            ),
            json=json,
            headers=await get_token_for_user(employee_owner),
        )

        response_data = response.json()
        assert response.status_code == status.HTTP_200_OK, response_data
        if field == 'executors':
            for executor in json[field]:
                assert executor in response_data[field][0].values(), response_data
        else:
            assert response_data[field] == value, response_data
            if field == 'date_completion':
                assert response_data['transfer_counter'] == 1, response_data

    @pytest.mark.asyncio
    async def test_update_task_not_found_problem(
        self,
        client: AsyncClient,
        problem_for_test,
        get_token_for_user,
    ):
        """Запрос на обновление несуществующей задачи."""
        problem, employee_owner, company = await problem_for_test(return_all_objects=True)
        problem_id = problem.id
        task_id = random.randint(1, 100)
        response = await client.patch(
            UrlConstants.TASK_ENDPOINT.format(
                company_slug=company.slug, problem_id=problem_id, task_id=task_id
            ),
            json={'name': 'Updated name'},
            headers=await get_token_for_user(employee_owner),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()


class TestTasksDelete:
    """Тесты DELETE-запросов."""

    @pytest.mark.asyncio
    async def test_delete_task(
        self,
        client: AsyncClient,
        task_for_test,
        get_token_for_user,
    ):
        """Тест успешного удаления задачи."""
        task, problem, employee_owner, company = await task_for_test(return_all_objects=True)
        response = await client.delete(
            UrlConstants.TASK_ENDPOINT.format(
                company_slug=company.slug, problem_id=problem.id, task_id=task.id
            ),
            headers=await get_token_for_user(employee_owner),
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT, response.json()

    @pytest.mark.asyncio
    async def test_delete_not_found_task(
        self,
        client: AsyncClient,
        problem_for_test,
        get_token_for_user,
    ):
        """Запрос на удаление несуществующей задачи."""
        problem, employee, company = await problem_for_test(return_all_objects=True)
        task_id = random.randint(1, 100)
        response = await client.delete(
            UrlConstants.TASK_ENDPOINT.format(
                company_slug=company.slug, problem_id=problem.id, task_id=task_id
            ),
            headers=await get_token_for_user(employee),
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND, response.json()
