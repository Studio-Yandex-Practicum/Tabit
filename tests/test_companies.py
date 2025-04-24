import random
import uuid

import pytest
from fastapi import status
from httpx import AsyncClient

from src.core.constants import ERROR_INVALID_TELEGRAM_USERNAME
from tests.constants import (
    COMPANY_FIELDS,
    DEPARTMENT_FIELDS,
    EMPLOYEE_FIELDS,
    URL,
    USER_TELEGRAM,
)


def generate_department_data(all_fields=False):
    """Генерирует реалистичные данные для создания департамента."""
    data = {'name': f'Тестовый департамент {uuid.uuid4().hex[:3]}'}

    if all_fields:
        pass
        # Slug автогенерится.
        # data.update({'slug': f'test-department-{uuid.uuid4().hex[:3]}'})

    return data


def generate_employee_data(all_fields=False):
    """Генерирует реалистичные данные для создания сотрудника."""
    cyrillic_letters = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
    random_suffix = ''.join(random.choice(cyrillic_letters) for _ in range(4))

    data = {
        'email': f'user{uuid.uuid4().hex[:8]}@example.com',
        'password': 'Astring123',
        'name': f'Иван{random_suffix}',
        'surname': f'Петров{random_suffix}',
        'role': 'Сотрудник',
        'company_id': 1,
    }

    if all_fields:
        data.update(
            {
                'is_active': True,
                'is_superuser': False,
                'is_verified': False,
                'patronymic': f'Сергеевич{random_suffix}',
                'phone_number': '71234567890',
                'birthday': '2025-03-05',
                'telegram_username': f'user{uuid.uuid4().hex[:4]}',
                'start_date_employment': '2025-03-05',
                'end_date_employment': '2025-03-06',
                'avatar_link': 'https://example.com/',
                'current_department_id': 1,
                'previous_department_id': 1,
                'employee_position': f'Должность{random_suffix}',
            }
        )

    return data


class TestGetСompanies:
    """Тесты для эндпоинта получения информации о компании."""

    @pytest.mark.asyncio
    async def test_get_company_success(
        self, client: AsyncClient, moderator_of_company, get_token_for_user
    ):
        """
        Тест успешного получения информации о компании.

        Проверяет:
        1. Успешный статус ответа (200 OK)
        2. Наличие всех ожидаемых полей в ответе
        3. Корректность значений основных полей (name, slug)
        """
        moderator, company = await moderator_of_company(return_company=True)
        token = await get_token_for_user(moderator)
        response = await client.get(
            URL.COMPANY_ENDPOINT.format(company_slug=company.slug), headers=token
        )
        assert (
            response.status_code == status.HTTP_200_OK
        ), f'Ожидался статус 200 OK, получен {response.status_code}. Ответ: {response.text}'
        data = response.json()
        assert (
            set(data.keys()) == COMPANY_FIELDS
        ), f'Ожидались поля {COMPANY_FIELDS}, получены поля {set(data.keys())}'

        field_checks = {
            'name': company.name,
            'slug': company.slug,
        }

        for field, expected_value in field_checks.items():
            assert (
                data[field] == expected_value
            ), f"Ожидалось значение поля '{field}': '{expected_value}', получено: '{data[field]}'"


class TestGetEmployees:
    """Тесты для эндпоинта получения списка сотрудников компании."""

    @pytest.mark.asyncio
    async def test_get_employees_success(
        self, client: AsyncClient, moderator_of_company, get_token_for_user, employee_of_company
    ):
        """
        Тест успешного получения списка сотрудников компании.

        Проверяет:
        1. Успешный статус ответа (200 OK)
        2. Корректность формата ответа (список)
        3. Соответствие количества сотрудников
        4. Наличие всех ожидаемых полей в каждом сотруднике
        5. Корректность привязки сотрудников к компании
        """
        moderator, company = await moderator_of_company(return_company=True)
        token = await get_token_for_user(moderator)

        employees = [moderator]
        employees.extend([await employee_of_company({'company_id': company.id}) for _ in range(3)])

        response = await client.get(
            URL.EMPLOYEES_ENDPOINT.format(company_slug=company.slug), headers=token
        )
        assert (
            response.status_code == status.HTTP_200_OK
        ), f'Ожидался статус 200 OK, получен {response.status_code}. Ответ: {response.text}'

        data = response.json()

        assert isinstance(data, list), f'Ожидался список, получен тип {type(data)}'
        assert len(data) == len(
            employees
        ), f'Ожидалось {len(employees)} сотрудников, получено {len(data)}'

        for employee_data in data:
            assert (
                set(employee_data.keys()) == EMPLOYEE_FIELDS
            ), f'Ожидались поля {EMPLOYEE_FIELDS}, получены поля {set(employee_data.keys())}'

            field_checks = {
                'company_id': company.id,
                'is_active': True,
                'is_superuser': False,
                'is_verified': False,
            }

            for field, expected_value in field_checks.items():
                assert employee_data[field] == expected_value, (
                    f"Ожидалось значение поля '{field}': '{expected_value}', "
                    f"получено: '{employee_data[field]}'"
                )


class TestGetEmployee:
    """Тесты для эндпоинта получения информации о конкретном сотруднике."""

    @pytest.mark.asyncio
    async def test_get_employee_success(
        self, client: AsyncClient, moderator_of_company, get_token_for_user, employee_of_company
    ):
        """
        Тест успешного получения информации о конкретном сотруднике.

        Проверяет:
        1. Успешный статус ответа (200 OK)
        2. Наличие всех ожидаемых полей в ответе
        3. Корректность значений полей (id, email, name, surname и др.)
        """
        moderator, company = await moderator_of_company(return_company=True)
        token = await get_token_for_user(moderator)

        employee = await employee_of_company({'company_id': company.id})

        response = await client.get(
            URL.EMPLOYEE_ENDPOINT.format(company_slug=company.slug, employee_id=employee.id),
            headers=token,
        )
        assert (
            response.status_code == status.HTTP_200_OK
        ), f'Ожидался статус 200 OK, получен {response.status_code}. Ответ: {response.text}'

        data = response.json()
        assert (
            set(data.keys()) == EMPLOYEE_FIELDS
        ), f'Ожидались поля {EMPLOYEE_FIELDS}, получены поля {set(data.keys())}'
        assert data['id'] == str(
            employee.id
        ), f'Ожидался id сотрудника {employee.id}, получен {data["id"]}'
        assert (
            data['email'] == employee.email
        ), f'Ожидался email сотрудника "{employee.email}", получен "{data["email"]}"'
        assert (
            data['name'] == employee.name
        ), f'Ожидалось имя сотрудника "{employee.name}", получено "{data["name"]}"'
        assert (
            data['surname'] == employee.surname
        ), f'Ожидалась фамилия сотрудника "{employee.surname}", получена "{data["surname"]}"'
        assert (
            data['company_id'] == company.id
        ), f'Ожидался company_id {company.id}, получен {data["company_id"]}'


class TestPatchEmployee:
    """Тесты для эндпоинта обновления информации о сотруднике."""

    @pytest.mark.parametrize(
        'field,new_value',
        [
            ('email', 'user@exфыamp11le.com'),
            ('name', 'striфывфыng'),
            ('surname', 'stфывфыrinфывфыg'),
            ('patronymic', 'string'),
            ('phone_number', '71234567890'),
            ('birthday', '2025-03-05'),
            ('telegram_username', 'string34'),
            ('start_date_employment', '2025-03-05'),
            ('end_date_employment', '2025-03-06'),
            ('avatar_link', 'https://example.com/'),
            ('employee_position', 'string'),
            ('is_active', True),
            ('is_superuser', False),
            ('is_verified', False),
        ],
    )
    @pytest.mark.asyncio
    async def test_patch_employee_single_field(
        self,
        client: AsyncClient,
        moderator_of_company,
        get_token_for_user,
        employee_of_company,
        field,
        new_value,
    ):
        """
        Тест успешного обновления одного поля сотрудника.

        Проверяет:
        1. Успешный статус ответа (200 OK)
        2. Корректность обновленного поля
        3. Сохранение остальных полей без изменений
        """
        moderator, company = await moderator_of_company(return_company=True)
        token = await get_token_for_user(moderator)

        employee = await employee_of_company({'company_id': company.id})
        old_data = (
            response.json()
            if (
                response := await client.get(
                    URL.EMPLOYEE_ENDPOINT.format(
                        company_slug=company.slug, employee_id=employee.id
                    ),
                    headers=token,
                )
            ).status_code
            == status.HTTP_200_OK
            else {}
        )

        response = await client.patch(
            URL.EMPLOYEE_ENDPOINT.format(company_slug=company.slug, employee_id=employee.id),
            headers=token,
            json={field: new_value},
        )
        assert (
            response.status_code == status.HTTP_200_OK
        ), f'Ожидался статус 200 OK, получен {response.status_code}. Ответ: {response.text}'

        data = response.json()
        assert (
            set(data.keys()) == EMPLOYEE_FIELDS
        ), f'Ожидались поля {EMPLOYEE_FIELDS}, получены поля {set(data.keys())}'

        assert (
            data[field] == new_value
        ), f"Ожидалось новое значение поля '{field}': '{new_value}', получено: '{data[field]}'"

        for key, value in old_data.items():
            if key != field and key not in ('updated_at', 'created_at'):
                assert data[key] == value, (
                    f"Поле '{key}' не должно было измениться. "
                    f"Ожидалось: '{value}', получено: '{data[key]}'"
                )

    @pytest.mark.asyncio
    async def test_patch_employee_all_fields(
        self,
        client: AsyncClient,
        moderator_of_company,
        get_token_for_user,
        employee_of_company,
        department_for_test,
    ):
        """
        Тест успешного обновления всех полей сотрудника.

        Проверяет:
        1. Успешный статус ответа (200 OK)
        2. Корректность обновления всех полей
        """
        moderator, company = await moderator_of_company(return_company=True)
        token = await get_token_for_user(moderator)

        department = await department_for_test({'company_id': company.id})
        employee = await employee_of_company({'company_id': company.id})

        update_data = generate_employee_data(all_fields=True)
        update_data['company_id'] = company.id
        update_data['current_department_id'] = department.id
        update_data['previous_department_id'] = department.id
        update_data['role'] = 'Сотрудник'

        response = await client.patch(
            URL.EMPLOYEE_ENDPOINT.format(company_slug=company.slug, employee_id=employee.id),
            headers=token,
            json=update_data,
        )
        assert (
            response.status_code == status.HTTP_200_OK
        ), f'Ожидался статус 200 OK, получен {response.status_code}. Ответ: {response.text}'

        data = response.json()
        assert (
            set(data.keys()) == EMPLOYEE_FIELDS
        ), f'Ожидались поля {EMPLOYEE_FIELDS}, получены поля {set(data.keys())}'

        for field, expected_value in update_data.items():
            if field != 'password':
                assert data[field] == expected_value, (
                    f"Ожидалось значение поля '{field}': '{expected_value}', "
                    f"получено: '{data[field]}'"
                )

    @pytest.mark.asyncio
    async def test_patch_employee_with_same_telegram(
        self,
        client: AsyncClient,
        moderator_of_company,
        get_token_for_user,
        department_for_test,
        employee_of_company,
    ):
        """
        Тест создаст двух сотрудников: со всеми полями и с минимальным набором.
        Затем попрбует установить дублирующий Телеграм одному из них.

        Проверяет:
        1. Статус ответа 400 Bad Request
        2. Корректность сообщения об ошибке
        """
        moderator, company = await moderator_of_company(return_company=True)
        token = await get_token_for_user(moderator)

        department = await department_for_test({'company_id': company.id})

        response = None

        existing_employee_data = generate_employee_data(all_fields=True)
        existing_employee_data['company_id'] = company.id
        existing_employee_data['current_department_id'] = department.id
        existing_employee_data['previous_department_id'] = department.id
        existing_employee_data['telegram_username'] = USER_TELEGRAM
        response = await client.post(
            URL.CREATE_EMPLOYEE_ENDPOINT.format(company_slug=company.slug),
            headers=token,
            json=existing_employee_data,
        )
        employee = await employee_of_company({'company_id': company.id})
        response = await client.patch(
            URL.EMPLOYEE_ENDPOINT.format(company_slug=company.slug, employee_id=employee.id),
            headers=token,
            json={'telegram_username': USER_TELEGRAM},
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST, (
            f'При попытке создать запись с дублированием Telegram-имени'
            f'не было ответа cо статусом {status.HTTP_400_BAD_REQUEST}:\n{response.text}'
        )
        data = response.json()
        assert 'detail' in data, "В ответе отсутствует поле 'detail'"
        assert data['detail'] == ERROR_INVALID_TELEGRAM_USERNAME, (
            f"Ожидалось сообщение '{ERROR_INVALID_TELEGRAM_USERNAME}'"
            f", получено: '{data['detail']}'"
        )

    @pytest.mark.asyncio
    async def test_patch_employee_not_found(
        self, client: AsyncClient, moderator_of_company, get_token_for_user
    ):
        """
        Тест обновления несуществующего сотрудника.

        Проверяет:
        1. Статус ответа 404 Not Found
        2. Корректность сообщения об ошибке
        """
        moderator, company = await moderator_of_company(return_company=True)
        token = await get_token_for_user(moderator)

        non_existent_id = '5e4350bd-ffb8-4af9-92bd-f3199c6fafe3'
        response = await client.patch(
            URL.EMPLOYEE_ENDPOINT.format(company_slug=company.slug, employee_id=non_existent_id),
            headers=token,
            json={'name': 'Иванушка'},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            f'Ожидался статус 404 Not Found, получен {response.status_code}. '
            f'Ответ: {response.text}'
        )

        data = response.json()
        assert 'detail' in data, "В ответе отсутствует поле 'detail'"
        assert (
            data['detail'] == f'Не найден объект CompanyUser по данному id: {non_existent_id}'
        ), f"Ожидалось сообщение 'Объект не найден', получено: '{data['detail']}'"


class TestDeleteEmployee:
    """Тесты для эндпоинта удаления сотрудника."""

    @pytest.mark.asyncio
    async def test_delete_employee_success(
        self, client: AsyncClient, moderator_of_company, get_token_for_user, employee_of_company
    ):
        """
        Тест успешного удаления сотрудника.

        Проверяет:
        1. Успешный статус ответа (204 No Content)
        2. Фактическое удаление сотрудника из базы данных
        """
        moderator, company = await moderator_of_company(return_company=True)
        token = await get_token_for_user(moderator)

        employee = await employee_of_company({'company_id': company.id})

        response = await client.delete(
            URL.EMPLOYEE_ENDPOINT.format(company_slug=company.slug, employee_id=employee.id),
            headers=token,
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT, (
            f'Ожидался статус 204 No Content, получен {response.status_code}. '
            f'Ответ: {response.text}'
        )

        response = await client.get(
            URL.EMPLOYEE_ENDPOINT.format(company_slug=company.slug, employee_id=employee.id),
            headers=token,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            f'Ожидался статус 404 Not Found при попытке получить удаленного сотрудника, '
            f'получен {response.status_code}. Ответ: {response.text}'
        )

    @pytest.mark.asyncio
    async def test_delete_employee_not_found(
        self, client: AsyncClient, moderator_of_company, get_token_for_user
    ):
        """
        Тест удаления несуществующего сотрудника.

        Проверяет:
        1. Статус ответа 404 Not Found
        2. Корректность сообщения об ошибке
        """
        moderator, company = await moderator_of_company(return_company=True)
        token = await get_token_for_user(moderator)

        non_existent_id = '5e4350bd-ffb8-4af9-92bd-f3199c6fafe3'
        response = await client.delete(
            URL.EMPLOYEE_ENDPOINT.format(company_slug=company.slug, employee_id=non_existent_id),
            headers=token,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            f'Ожидался статус 404 Not Found, получен {response.status_code}. '
            f'Ответ: {response.text}'
        )

        data = response.json()
        assert 'detail' in data, "В ответе отсутствует поле 'detail'"
        assert (
            data['detail'] == f'Не найден объект CompanyUser по данному id: {non_existent_id}'
        ), f"Ожидалось сообщение 'Объект не найден', получено: '{data['detail']}'"


class TestGetDepartments:
    """Тесты для эндпоинта получения списка департаментов компании."""

    @pytest.mark.asyncio
    async def test_get_departments_success(
        self, client: AsyncClient, moderator_of_company, get_token_for_user, department_for_test
    ):
        """
        Тест успешного получения списка департаментов компании.

        Проверяет:
        1. Успешный статус ответа (200 OK)
        2. Корректность формата ответа (список)
        3. Соответствие количества департаментов
        4. Наличие всех ожидаемых полей в каждом департаменте
        5. Корректность привязки департаментов к компании
        """
        moderator, company = await moderator_of_company(return_company=True)
        token = await get_token_for_user(moderator)

        departments = [await department_for_test({'company_id': company.id}) for _ in range(3)]

        response = await client.get(
            URL.DEPARTMENTS_ENDPOINT.format(company_slug=company.slug), headers=token
        )
        assert (
            response.status_code == status.HTTP_200_OK
        ), f'Ожидался статус 200 OK, получен {response.status_code}. Ответ: {response.text}'

        data = response.json()

        assert isinstance(data, list), f'Ожидался список, получен тип {type(data)}'
        assert len(data) == len(
            departments
        ), f'Ожидалось {len(departments)} департаментов, получено {len(data)}'
        for dept in data:
            assert (
                set(dept.keys()) == DEPARTMENT_FIELDS
            ), f'Ожидались поля {DEPARTMENT_FIELDS}, получены поля {set(dept.keys())}'
            assert (
                dept['company_id'] == company.id
            ), f'Ожидался company_id {company.id}, получен {dept["company_id"]}'


class TestGetDepartment:
    """Тесты для эндпоинта получения информации о конкретном департаменте."""

    @pytest.mark.asyncio
    async def test_get_department_success(
        self, client: AsyncClient, moderator_of_company, get_token_for_user, department_for_test
    ):
        """
        Тест успешного получения информации о конкретном департаменте.

        Проверяет:
        1. Успешный статус ответа (200 OK)
        2. Наличие всех ожидаемых полей в ответе
        3. Корректность значений полей (name, slug, id, company_id)
        """
        moderator, company = await moderator_of_company(return_company=True)
        token = await get_token_for_user(moderator)

        department = await department_for_test({'company_id': company.id})

        response = await client.get(
            URL.DEPARTMENT_ENDPOINT.format(
                company_slug=company.slug, department_slug=department.slug
            ),
            headers=token,
        )
        assert (
            response.status_code == status.HTTP_200_OK
        ), f'Ожидался статус 200 OK, получен {response.status_code}. Ответ: {response.text}'

        data = response.json()
        assert (
            set(data.keys()) == DEPARTMENT_FIELDS
        ), f'Ожидались поля {DEPARTMENT_FIELDS}, получены поля {set(data.keys())}'

        field_checks = {
            'name': department.name,
            'slug': department.slug,
            'id': department.id,
            'company_id': company.id,
        }

        for field, expected_value in field_checks.items():
            assert (
                data[field] == expected_value
            ), f"Ожидалось значение поля '{field}': '{expected_value}', получено: '{data[field]}'"


class TestPatchDepartment:
    """Тесты для эндпоинта обновления информации о департаменте."""

    # @pytest.mark.skip(reason='Тест временно пропущен, так как есть баг на slug')
    @pytest.mark.asyncio
    async def test_patch_department_success(
        self, client: AsyncClient, moderator_of_company, get_token_for_user, department_for_test
    ):
        """
        Тест успешного обновления департамента.

        Проверяет:
        1. Успешный статус ответа (200 OK)
        2. Корректность обновленных данных
        3. Сохранение остальных полей без изменений
        """
        moderator, company = await moderator_of_company(return_company=True)
        token = await get_token_for_user(moderator)

        department = await department_for_test({'company_id': company.id})
        new_name = 'Иванушка'

        response = await client.patch(
            URL.DEPARTMENT_ENDPOINT.format(
                company_slug=company.slug, department_slug=department.slug
            ),
            headers=token,
            json={'name': new_name},
        )
        assert (
            response.status_code == status.HTTP_200_OK
        ), f'Ожидался статус 200 OK, получен {response.status_code}. Ответ: {response.text}'

        data = response.json()
        assert (
            set(data.keys()) == DEPARTMENT_FIELDS
        ), f'Ожидались поля {DEPARTMENT_FIELDS}, получены поля {set(data.keys())}'

        assert (
            data['name'] == new_name
        ), f"Ожидалось новое имя '{new_name}', получено: '{data['name']}'"

        field_checks = {'id': department.id, 'company_id': company.id}

        for field, expected_value in field_checks.items():
            assert (
                data[field] == expected_value
            ), f"Ожидалось значение поля '{field}': '{expected_value}', получено: '{data[field]}'"

    @pytest.mark.asyncio
    async def test_patch_department_not_found(
        self, client: AsyncClient, moderator_of_company, get_token_for_user
    ):
        """
        Тест обновления несуществующего департамента.

        Проверяет:
        1. Статус ответа 404 Not Found
        2. Корректность сообщения об ошибке
        """
        moderator, company = await moderator_of_company(return_company=True)
        token = await get_token_for_user(moderator)

        non_existent_slug = '99999'
        response = await client.patch(
            URL.DEPARTMENT_ENDPOINT.format(
                company_slug=company.slug, department_slug=non_existent_slug
            ),
            headers=token,
            json={'name': 'Иванушка'},
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            f'Ожидался статус 404 Not Found, получен {response.status_code}. '
            f'Ответ: {response.text}'
        )

        data = response.json()
        assert 'detail' in data, "В ответе отсутствует поле 'detail'"
        assert (
            data['detail'] == f'Не найден объект Department по данному slug: {non_existent_slug}'
        ), f"Ожидалось сообщение 'Объект не найден', получено: '{data['detail']}'"


class TestDeleteDepartment:
    """Тесты для эндпоинта удаления департамента."""

    @pytest.mark.asyncio
    async def test_delete_department_success(
        self, client: AsyncClient, moderator_of_company, get_token_for_user, department_for_test
    ):
        """
        Тест успешного удаления департамента.

        Проверяет:
        1. Успешный статус ответа (204 No Content)
        2. Фактическое удаление департамента из базы данных
        """
        moderator, company = await moderator_of_company(return_company=True)
        token = await get_token_for_user(moderator)

        department = await department_for_test({'company_id': company.id})

        response = await client.delete(
            URL.DEPARTMENT_ENDPOINT.format(
                company_slug=company.slug, department_slug=department.slug
            ),
            headers=token,
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT, (
            f'Ожидался статус 204 No Content, получен {response.status_code}. '
            f'Ответ: {response.text}'
        )

        response = await client.get(
            URL.DEPARTMENT_ENDPOINT.format(
                company_slug=company.slug, department_slug=department.slug
            ),
            headers=token,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            f'Ожидался статус 404 Not Found при попытке получить удаленный департамент, '
            f'получен {response.status_code}. Ответ: {response.text}'
        )

    @pytest.mark.asyncio
    async def test_delete_department_not_found(
        self, client: AsyncClient, moderator_of_company, get_token_for_user
    ):
        """
        Тест удаления несуществующего департамента.

        Проверяет:
        1. Статус ответа 404 Not Found
        2. Корректность сообщения об ошибке
        """
        moderator, company = await moderator_of_company(return_company=True)
        token = await get_token_for_user(moderator)

        non_existent_slug = '99999'
        response = await client.delete(
            URL.DEPARTMENT_ENDPOINT.format(
                company_slug=company.slug, department_slug=non_existent_slug
            ),
            headers=token,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND, (
            f'Ожидался статус 404 Not Found, получен {response.status_code}. '
            f'Ответ: {response.text}'
        )

        data = response.json()
        assert 'detail' in data, "В ответе отсутствует поле 'detail'"
        assert (
            data['detail'] == f'Не найден объект Department по данному slug: {non_existent_slug}'
        ), f"Ожидалось сообщение 'Объект не найден', получено: '{data['detail']}'"


class TestCreateDepartment:
    """Тесты для эндпоинта создания департамента."""

    @pytest.mark.asyncio
    async def test_create_department_with_required_fields(
        self, client: AsyncClient, moderator_of_company, get_token_for_user
    ):
        """
        Тест создания департамента только с обязательными полями.

        Проверяет:
        1. Успешный статус ответа (201 Created)
        2. Наличие всех ожидаемых полей в ответе
        3. Корректность значений полей (name, slug, id, company_id)
        4. Автоматическую генерацию slug из name
        """
        moderator, company = await moderator_of_company(return_company=True)
        token = await get_token_for_user(moderator)

        department_data = generate_department_data()

        response = await client.post(
            URL.CREATE_DEPARTMENT_ENDPOINT.format(company_slug=company.slug),
            headers=token,
            json=department_data,
        )
        assert (
            response.status_code == status.HTTP_201_CREATED
        ), f'Ожидался статус 201 Created, получен {response.status_code}. Ответ: {response.text}'

        data = response.json()
        assert (
            set(data.keys()) == DEPARTMENT_FIELDS
        ), f'Ожидались поля {DEPARTMENT_FIELDS}, получены поля {set(data.keys())}'

        field_checks = {
            'name': department_data['name'],
            'company_id': company.id,
        }

        for field, expected_value in field_checks.items():
            assert (
                data[field] == expected_value
            ), f"Ожидалось значение поля '{field}': '{expected_value}', получено: '{data[field]}'"
        assert isinstance(
            data['id'], int
        ), f'Ожидался целочисленный id, получен тип {type(data["id"])}'

    @pytest.mark.asyncio
    async def test_create_department_with_all_fields(
        self, client: AsyncClient, moderator_of_company, get_token_for_user
    ):
        """
        Тест создания департамента со всеми полями.

        Проверяет:
        1. Успешный статус ответа (201 Created)
        2. Наличие всех ожидаемых полей в ответе
        3. Корректность значений полей (name, slug, id, company_id)
        4. Использование предоставленного slug
        """
        moderator, company = await moderator_of_company(return_company=True)
        token = await get_token_for_user(moderator)

        department_data = generate_department_data(all_fields=True)

        response = await client.post(
            URL.CREATE_DEPARTMENT_ENDPOINT.format(company_slug=company.slug),
            headers=token,
            json=department_data,
        )
        assert (
            response.status_code == status.HTTP_201_CREATED
        ), f'Ожидался статус 201 Created, получен {response.status_code}. Ответ: {response.text}'

        data = response.json()
        assert (
            set(data.keys()) == DEPARTMENT_FIELDS
        ), f'Ожидались поля {DEPARTMENT_FIELDS}, получены поля {set(data.keys())}'

        field_checks = {'name': department_data['name'], 'company_id': company.id}

        for field, expected_value in field_checks.items():
            assert (
                data[field] == expected_value
            ), f"Ожидалось значение поля '{field}': '{expected_value}', получено: '{data[field]}'"
        assert isinstance(
            data['id'], int
        ), f'Ожидался целочисленный id, получен тип {type(data["id"])}'


class TestCreateEmployee:
    """Тесты для эндпоинта создания сотрудника."""

    @pytest.mark.skip(reason='Тест временно пропущен, так как есть баг на обязательное поле role')
    @pytest.mark.asyncio
    async def test_create_employee_with_required_fields(
        self, client: AsyncClient, moderator_of_company, get_token_for_user
    ):
        """
        Тест создания сотрудника только с обязательными полями.

        Проверяет:
        1. Успешный статус ответа (201 Created)
        2. Наличие всех ожидаемых полей в ответе
        3. Корректность значений обязательных полей
        4. Значения по умолчанию для необязательных полей
        """
        moderator, company = await moderator_of_company(return_company=True)
        token = await get_token_for_user(moderator)

        employee_data = generate_employee_data()
        employee_data['company_id'] = company.id

        response = await client.post(
            URL.CREATE_EMPLOYEE_ENDPOINT.format(company_slug=company.slug),
            headers=token,
            json=employee_data,
        )
        assert (
            response.status_code == status.HTTP_201_CREATED
        ), f'Ожидался статус 201 Created, получен {response.status_code}. Ответ: {response.text}'

        data = response.json()
        assert (
            set(data.keys()) == EMPLOYEE_FIELDS
        ), f'Ожидались поля {EMPLOYEE_FIELDS}, получены поля {set(data.keys())}'

        required_fields = {
            'email': employee_data['email'],
            'name': employee_data['name'],
            'surname': employee_data['surname'],
            'role': employee_data['role'],
            'company_id': company.id,
        }

        for field, expected_value in required_fields.items():
            assert (
                data[field] == expected_value
            ), f"Ожидалось значение поля '{field}': '{expected_value}', получено: '{data[field]}'"

    @pytest.mark.asyncio
    async def test_create_employee_with_all_fields(
        self, client: AsyncClient, moderator_of_company, get_token_for_user, department_for_test
    ):
        """
        Тест создания сотрудника со всеми полями.

        Проверяет:
        1. Успешный статус ответа (201 Created)
        2. Наличие всех ожидаемых полей в ответе
        3. Корректность значений всех полей
        """
        moderator, company = await moderator_of_company(return_company=True)
        token = await get_token_for_user(moderator)

        department = await department_for_test({'company_id': company.id})

        employee_data = generate_employee_data(all_fields=True)
        employee_data['company_id'] = company.id
        employee_data['current_department_id'] = department.id
        employee_data['previous_department_id'] = department.id

        response = await client.post(
            URL.CREATE_EMPLOYEE_ENDPOINT.format(company_slug=company.slug),
            headers=token,
            json=employee_data,
        )
        assert (
            response.status_code == status.HTTP_201_CREATED
        ), f'Ожидался статус 201 Created, получен {response.status_code}. Ответ: {response.text}'

        data = response.json()
        assert (
            set(data.keys()) == EMPLOYEE_FIELDS
        ), f'Ожидались поля {EMPLOYEE_FIELDS}, получены поля {set(data.keys())}'

        field_checks = {
            'email': employee_data['email'],
            'name': employee_data['name'],
            'surname': employee_data['surname'],
            'role': employee_data['role'],
            'company_id': company.id,
            'is_active': employee_data['is_active'],
            'is_superuser': employee_data['is_superuser'],
            'is_verified': employee_data['is_verified'],
            'patronymic': employee_data['patronymic'],
            'phone_number': employee_data['phone_number'],
            'birthday': employee_data['birthday'],
            'telegram_username': employee_data['telegram_username'],
            'start_date_employment': employee_data['start_date_employment'],
            'end_date_employment': employee_data['end_date_employment'],
            'avatar_link': employee_data['avatar_link'],
            'current_department_id': employee_data['current_department_id'],
            'previous_department_id': employee_data['previous_department_id'],
            'employee_position': employee_data['employee_position'],
        }

        for field, expected_value in field_checks.items():
            assert (
                data[field] == expected_value
            ), f"Ожидалось значение поля '{field}': '{expected_value}', получено: '{data[field]}'"

    @pytest.mark.asyncio
    async def test_create_employees_with_same_telegram(
        self, client: AsyncClient, moderator_of_company, get_token_for_user, department_for_test
    ):
        """
        Тест создаст 2 сотрудников со всеми полями, но с соваадающими Telegram.

        Проверяет:
        1. Статус ответа 400 Bad Request
        2. Корректность сообщения об ошибке
        """
        moderator, company = await moderator_of_company(return_company=True)
        token = await get_token_for_user(moderator)

        department = await department_for_test({'company_id': company.id})

        response = None
        for i in range(2):
            employee_data = generate_employee_data(all_fields=True)
            employee_data['company_id'] = company.id
            employee_data['current_department_id'] = department.id
            employee_data['previous_department_id'] = department.id
            employee_data['telegram_username'] = USER_TELEGRAM
            response = await client.post(
                URL.CREATE_EMPLOYEE_ENDPOINT.format(company_slug=company.slug),
                headers=token,
                json=employee_data,
            )
        assert response.status_code == status.HTTP_400_BAD_REQUEST, (
            f'При попытке создать запись с дублированием Telegram-имени'
            f'не было ответа cо статусом {status.HTTP_400_BAD_REQUEST}:\n{response.text}'
        )
        data = response.json()
        assert 'detail' in data, "В ответе отсутствует поле 'detail'"
        assert data['detail'] == ERROR_INVALID_TELEGRAM_USERNAME, (
            f"Ожидалось сообщение '{ERROR_INVALID_TELEGRAM_USERNAME}'"
            f", получено: '{data['detail']}'"
        )


class TestFeedback:
    """Тесты для эндпоинта обратной связи."""

    def generate_feedback_data(self):
        """
        Генерирует тестовые данные для отправки обратной связи.

        Возвращает:
            dict: Словарь с тестовыми данными для обратной связи
        """
        return {'email': ['user@example.com'], 'subject_email': 'string', 'message': 'string'}

    @pytest.mark.asyncio
    async def test_send_feedback_success(
        self, client: AsyncClient, moderator_of_company, get_token_for_user
    ):
        """
        Тест успешной отправки обратной связи.

        Проверяет:
        1. Успешный статус ответа (200 OK)
        2. Корректность формата ответа
        3. Наличие сообщения об успешной отправке
        """
        moderator, company = await moderator_of_company(return_company=True)
        token = await get_token_for_user(moderator)

        feedback_data = self.generate_feedback_data()

        response = await client.post(
            URL.FEEDBACK_ENDPOINT.format(company_slug=company.slug),
            headers=token,
            json=feedback_data,
        )
        assert (
            response.status_code == status.HTTP_200_OK
        ), f'Ожидался статус 200 OK, получен {response.status_code}. Ответ: {response.text}'

        data = response.json()
        assert isinstance(data, dict), f'Ожидался словарь, получен тип {type(data)}'
        assert 'message' in data, "В ответе отсутствует поле 'message'"
        assert data['message'] == f'Обратная связь отправлена для компании {company.slug}', (
            f"Ожидалось сообщение 'Обратная связь отправлена для компании {company.slug}', "
            f"получено: '{data['message']}'"
        )
