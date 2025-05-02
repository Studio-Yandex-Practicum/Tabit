import random
import string
from datetime import datetime, timedelta

import pytest
from fastapi import status
from httpx import AsyncClient

from tests.constants import UrlConstants


def generate_task_data(problem_id=None, owner_id=None, executers=None, all_fields=False):
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
    if executers:
        data.update(
            {
                'executers': executers,
            }
        )
    return data


class TestTasksPost:
    """Тесты POST-запросов к эндпоинту tasks."""

    @pytest.mark.asyncio
    async def test_create_task_without_executers(
        self,
        client: AsyncClient,
        problem_for_test,
        get_token_for_user,
    ):
        """Тест POST-запроса на создание задачи без исполнителей."""
        problem, owner, company = await problem_for_test(return_all_objects=True)
        task_data = generate_task_data(all_fields=True)
        response_task = await client.post(
            UrlConstants.TASKS_ENDPOINT.format(company_slug=company.slug, problem_id=problem.id),
            json=task_data,
            headers=await get_token_for_user(owner),
        )

        assert response_task.status_code == status.HTTP_201_CREATED
        response_data = response_task.json()
        assert response_data['name'] == task_data['name']
        assert response_data['description'] == task_data['description']
        assert response_data['date_completion'] == task_data['date_completion']
        assert response_data['owner_id'] == str(owner.id)

    @pytest.mark.skip('При попытке создания задачи с исполнителями возникает ошибка')  # TODO
    @pytest.mark.asyncio
    async def test_create_task_with_all_fields(
        self,
        client: AsyncClient,
        problem_for_test,
        get_token_for_user,
        employee_of_company,
    ):
        """Тест POST-запроса на создание задачи со всеми полями."""
        problem, owner, company = await problem_for_test(return_all_objects=True)
        executer = await employee_of_company({'company_id': company.id})
        task_data = generate_task_data(executers=[f'{executer.id}'], all_fields=True)
        response_task = await client.post(
            UrlConstants.TASKS_ENDPOINT.format(company_slug=company.slug, problem_id=problem.id),
            json=task_data,
            headers=await get_token_for_user(owner),
        )

        assert response_task.status_code == status.HTTP_201_CREATED

        response_data = response_task.json()

        assert response_data['name'] == task_data['name']
        assert response_data['description'] == task_data['description']
        assert response_data['date_completion'] == task_data['date_completion']
        assert str(executer.id) in response_data['executers']
        assert response_data['owner_id'] == str(owner.id)

    @pytest.mark.asyncio
    async def test_create_task_with_requared_fields(
        self,
        client: AsyncClient,
        problem_for_test,
        get_token_for_user,
    ):
        """Тест POST-запроса на создание задачи только с обязательными полями."""
        problem, owner, company = await problem_for_test(return_all_objects=True)
        task_data = generate_task_data()
        response_task = await client.post(
            UrlConstants.TASKS_ENDPOINT.format(company_slug=company.slug, problem_id=problem.id),
            json=task_data,
            headers=await get_token_for_user(owner),
        )

        assert response_task.status_code == status.HTTP_201_CREATED
        response_data = response_task.json()
        assert response_data['name'] == task_data['name']
        assert response_data['date_completion'] == task_data['date_completion']
        assert response_data['owner_id'] == str(owner.id)

    @pytest.mark.asyncio
    async def test_create_task_without_company_or_problem(
        self,
        client: AsyncClient,
        problem_for_test,
        get_token_for_user,
    ):
        """
        Тест POST-запроса на создание задачи c несуществующей компанией или проблемой.
        """
        problem, owner, company = await problem_for_test(return_all_objects=True)

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

            response_task = await client.post(
                UrlConstants.TASKS_ENDPOINT.format(
                    company_slug=company_slug, problem_id=problem_id
                ),
                json=task_data,
                headers=await get_token_for_user(owner),
            )

            assert response_task.status_code == status_code
            assert response_task.json() == detail
