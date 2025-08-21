import pytest
from fastapi import status
from httpx import AsyncClient

from tests.constants import ExpectedFieldsConstants, LengthConstants, UrlConstants, type_token
from tests.utils import random_string


def generate_department_data(length=5):
    """Генерирует реалистичные данные для создания компании."""
    return {'name': f'Отдел {random_string(length)}'}


@pytest.mark.asyncio(loop_scope='session')
class TestCreateDepartment:
    """Набор тестов для создания отделов компании администраторами сервиса."""

    async def test_create_department(
        self,
        client: AsyncClient,
        superuser_token: type_token,
        company_for_test,
    ):
        """
        Тест успешного создания отдела для компании.

        Проверяет, что API корректно создаёт отдел.
        Убедимся, что ответ содержит правильные значения и API возвращает 201
        """
        payload = generate_department_data()
        company = await company_for_test()

        response = await client.post(
            UrlConstants.MANAGEMENT_DEPARTMENT.format(company_slug=company.slug),
            json=payload,
            headers=superuser_token,
        )
        assert response.status_code == status.HTTP_201_CREATED, response.text
        data = response.json()
        for field in ExpectedFieldsConstants.DEPARTMENT_FIELDS_FOR_ADMIN:
            assert field in data
        assert data['name'] == payload['name']

    async def test_create_department_access(
        self,
        client: AsyncClient,
        admin_token: type_token,
        company_for_test,
    ):
        """
        Тест успешного создания отдела для компании.

        Проверяет, что API корректно создаёт отдел,
        если запрос отправлял администратор сервиса, но не супер-пользователь.
        Убедимся, что ответ API возвращает 201.
        """
        payload = generate_department_data()
        company = await company_for_test()

        response = await client.post(
            UrlConstants.MANAGEMENT_DEPARTMENT.format(company_slug=company.slug),
            json=payload,
            headers=admin_token,
        )
        assert response.status_code == status.HTTP_201_CREATED

    async def test_create_department_not_access(
        self,
        client: AsyncClient,
        moderator_token: type_token,
        employee_token: type_token,
        company_for_test,
    ):
        """
        Тест создания отдела для компании.

        Проверяет, что API не создаст отдел,
        если запрос отправлял не администратор сервиса или не супер-пользователь.
        Убедимся, что ответ API возвращает 401.
        """
        company = await company_for_test()
        tokens_bad = (
            moderator_token,
            employee_token,
            {'Authorization': 'foo.bar.baz'},
            None,
        )
        for token in tokens_bad:
            payload = generate_department_data(200)
            response = await client.post(
                UrlConstants.MANAGEMENT_DEPARTMENT.format(company_slug=company.slug),
                json=payload,
                headers=token,
            )
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_create_department_whitespace(
        self,
        client: AsyncClient,
        superuser_token: type_token,
        company_for_test,
    ):
        """
        Тест успешного создания отдела для компании,
        если в строковых полях присутствуют пробелы по краям.

        Проверяет, что API корректно создаёт отдел.
        Убедимся, что API возвращает 201
        """
        name = 'Отдел'
        bad_payload = {'name': f' {name} '}
        company = await company_for_test()

        response = await client.post(
            UrlConstants.MANAGEMENT_DEPARTMENT.format(company_slug=company.slug),
            json=bad_payload,
            headers=superuser_token,
        )
        assert response.status_code == status.HTTP_201_CREATED, response.text
        assert response.json()['name'] == name

    @pytest.mark.parametrize(
        'length_name, status_',
        (
            (LengthConstants.MAX_NAME_DEPARTMENT, status.HTTP_201_CREATED),
            (LengthConstants.MAX_NAME_DEPARTMENT + 1, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ),
    )
    async def test_create_department_length_name(
        self,
        client: AsyncClient,
        superuser_token: type_token,
        company_for_test,
        length_name,
        status_,
    ):
        """
        Тест создания отдела для компании, при придельном количестве символов в поле `name`.

        Если количество максимально - отдел будет создан.
        Если привешает максимальное - должна быть ошибка 422.
        """
        payload = {'name': 'x' * length_name}
        company = await company_for_test()

        response = await client.post(
            UrlConstants.MANAGEMENT_DEPARTMENT.format(company_slug=company.slug),
            json=payload,
            headers=superuser_token,
        )
        assert response.status_code == status_, response.text

    async def test_create_department_not_company(
        self,
        client: AsyncClient,
        superuser_token: type_token,
        company_for_test,
    ):
        """
        Тест создания отдела для компании.

        При указании в пути несуществующего slug компании, ответ должен вернуться со статусом 404.
        """
        payload = generate_department_data()
        company = await company_for_test()
        bad_company_slug = company.slug + 'x'

        response = await client.post(
            UrlConstants.MANAGEMENT_DEPARTMENT.format(company_slug=bad_company_slug),
            json=payload,
            headers=superuser_token,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
        assert (response_json := response.json()['detail']) == (
            f'Не найден объект Company по данному slug: {bad_company_slug}'
        ), response_json

    async def test_create_department_duplicate_in_company(
        self,
        client: AsyncClient,
        superuser_token: type_token,
        company_for_test,
    ):
        """
        Тест создания отдела для компании.

        В одной компании не может быть двух отделов с одинаковым названием.
        При попытке создать второй отдел с тем же названием должна быть ошибка 400.
        """
        payload = generate_department_data()
        company = await company_for_test()

        for _ in range(2):
            response = await client.post(
                UrlConstants.MANAGEMENT_DEPARTMENT.format(company_slug=company.slug),
                json=payload,
                headers=superuser_token,
            )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text
        assert 'detail' in response.json()

    async def test_create_department_duplicate_in_another_company(
        self,
        client: AsyncClient,
        superuser_token: type_token,
        company_for_test,
    ):
        """
        Тест создания отдела для компании.

        В двух разных компаниях может быть созданы отделы с одинаковым названием.
        При попытке создать в другой компании с тем же названием, должен создастся,
        ответ должен быть 201, а slug у них должен быть разный.
        """
        payload = generate_department_data()
        company_1 = await company_for_test()
        company_2 = await company_for_test()

        response_1 = await client.post(
            UrlConstants.MANAGEMENT_DEPARTMENT.format(company_slug=company_1.slug),
            json=payload,
            headers=superuser_token,
        )
        response_2 = await client.post(
            UrlConstants.MANAGEMENT_DEPARTMENT.format(company_slug=company_2.slug),
            json=payload,
            headers=superuser_token,
        )

        assert response_2.status_code == status.HTTP_201_CREATED
        assert response_1.json()['slug'] != response_2.json()['slug']


@pytest.mark.asyncio(loop_scope='session')
class TestGetDepartment:
    """Набор тестов для получения информации отделов компании администраторами сервиса."""

    async def test_get_multi_departments(
        self,
        client: AsyncClient,
        superuser_token: type_token,
        company_for_test,
        department_for_test,
    ):
        """
        Тест получения списка отделов конкретной компаний.

        При корректных данных должен вернутся ответ в виде списка со статусом 200.
        """
        company_1 = await company_for_test()
        company_2 = await company_for_test()

        for _ in range(2):
            await department_for_test({'company_id': company_1.id})
        await department_for_test({'company_id': company_2.id})

        response = await client.get(
            UrlConstants.MANAGEMENT_DEPARTMENT.format(company_slug=company_1.slug),
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_200_OK

        departments = response.json()
        assert isinstance(departments, list), 'Ответ API должен быть списком компаний'
        assert len(departments) == 2, 'В ответе должно быть два отдела'

        for department in departments:
            assert ExpectedFieldsConstants.DEPARTMENT_FIELDS_FOR_ADMIN.issubset(
                department.keys()
            ), (
                'Ответ должен содержать поля: '
                f'{ExpectedFieldsConstants.DEPARTMENT_FIELDS_FOR_ADMIN}'
            )

    async def test_get_multi_departments_access(
        self,
        client: AsyncClient,
        admin_token: type_token,
        department_for_test,
    ):
        """
        Тест получения списка отделов конкретной компаний.

        Проверяет, что API корректно вернет список,
        если запрос отправлял администратор сервиса, но не супер-пользователь.
        Убедимся, что ответ API возвращает 200.
        """
        _, company = await department_for_test(return_company=True)
        response = await client.get(
            UrlConstants.MANAGEMENT_DEPARTMENT.format(company_slug=company.slug),
            headers=admin_token,
        )

        assert response.status_code == status.HTTP_200_OK

    async def test_get_multi_departments_not_access(
        self,
        client: AsyncClient,
        moderator_token: type_token,
        employee_token: type_token,
        department_for_test,
    ):
        """
        Тест получения списка отделов конкретной компаний.

        Проверяет, что API не вернет список,
        если запрос не администратор сервиса или не супер-пользователь.
        Убедимся, что ответ API возвращает 401.
        """
        _, company = await department_for_test(return_company=True)
        tokens_bad = (
            moderator_token,
            employee_token,
            {'Authorization': 'foo.bar.baz'},
            None,
        )
        for token in tokens_bad:
            response = await client.get(
                UrlConstants.MANAGEMENT_DEPARTMENT.format(company_slug=company.slug),
                headers=token,
            )
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_multi_departments_not_company(
        self,
        client: AsyncClient,
        superuser_token: type_token,
        department_for_test,
    ):
        """
        Тест получения списка отделов конкретной компаний.

        При указании в пути несуществующего slug компании, ответ должен вернуться со статусом 404.
        """
        _, company = await department_for_test(return_company=True)
        bad_company_slug = company.slug + 'x'

        response = await client.get(
            UrlConstants.MANAGEMENT_DEPARTMENT.format(company_slug=bad_company_slug),
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert (response_json := response.json()['detail']) == (
            f'Не найден объект Company по данному slug: {bad_company_slug}'
        ), response_json

    async def test_get_department(
        self,
        client: AsyncClient,
        superuser_token: type_token,
        department_for_test,
    ):
        """
        Тест получения данных конкретного отдела конкретной компаний.

        При корректных данных должен вернутся ответ в виде списка со статусом 200.
        """
        department, company = await department_for_test(return_company=True)

        response = await client.get(
            UrlConstants.MANAGEMENT_DEPARTMENT_WITH_SLUG.format(
                company_slug=company.slug,
                department_slug=department.slug,
            ),
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert ExpectedFieldsConstants.DEPARTMENT_FIELDS_FOR_ADMIN.issubset(data), (
            f'Компания должна содержать поля: '
            f'{ExpectedFieldsConstants.DEPARTMENT_FIELDS_FOR_ADMIN}'
        )

    async def test_get_department_access(
        self,
        client: AsyncClient,
        admin_token: type_token,
        department_for_test,
    ):
        """
        Тест получения данных конкретного отдела конкретной компаний.

        Проверяет, что API корректно вернет данные,
        если запрос отправлял администратор сервиса, но не супер-пользователь.
        Убедимся, что ответ API возвращает 200.
        """
        department, company = await department_for_test(return_company=True)

        response = await client.get(
            UrlConstants.MANAGEMENT_DEPARTMENT_WITH_SLUG.format(
                company_slug=company.slug,
                department_slug=department.slug,
            ),
            headers=admin_token,
        )

        assert response.status_code == status.HTTP_200_OK

    async def test_get_department_not_access(
        self,
        client: AsyncClient,
        moderator_token: type_token,
        employee_token: type_token,
        department_for_test,
    ):
        """
        Тест получения данных конкретного отдела конкретной компаний.

        Проверяет, что API не вернет данные,
        если запрос не администратор сервиса или не супер-пользователь.
        Убедимся, что ответ API возвращает 401.
        """
        department, company = await department_for_test(return_company=True)
        tokens_bad = (
            moderator_token,
            employee_token,
            {'Authorization': 'foo.bar.baz'},
            None,
        )
        for token in tokens_bad:
            response = await client.get(
                UrlConstants.MANAGEMENT_DEPARTMENT_WITH_SLUG.format(
                    company_slug=company.slug,
                    department_slug=department.slug,
                ),
                headers=token,
            )
            assert response.status_code == status.HTTP_401_UNAUTHORIZED

    async def test_get_department_not_company(
        self,
        client: AsyncClient,
        superuser_token: type_token,
        department_for_test,
    ):
        """
        Тест получения данных конкретного отдела конкретной компаний.

        При указании в пути несуществующего slug компании, ответ должен вернуться со статусом 404.
        """
        department, company = await department_for_test(return_company=True)
        bad_company_slug = company.slug + 'x'

        response = await client.get(
            UrlConstants.MANAGEMENT_DEPARTMENT_WITH_SLUG.format(
                company_slug=bad_company_slug,
                department_slug=department.slug,
            ),
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert (response_json := response.json()['detail']) == (
            f'Не найден объект Company по данному slug: {bad_company_slug}'
        ), response_json

    async def test_get_department_not_department(
        self,
        client: AsyncClient,
        superuser_token: type_token,
        department_for_test,
    ):
        """
        Тест получения данных конкретного отдела конкретной компаний.

        При указании в пути несуществующего slug отдела, ответ должен вернуться со статусом 404.
        """
        department, company = await department_for_test(return_company=True)
        bad_department_slug = department.slug + 'x'

        response = await client.get(
            UrlConstants.MANAGEMENT_DEPARTMENT_WITH_SLUG.format(
                company_slug=company.slug,
                department_slug=bad_department_slug,
            ),
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert (response_json := response.json()['detail']) == (
            f'Не найден объект Department по данному slug: {bad_department_slug}'
        ), response_json

    async def test_get_department_department_not_in_company(
        self,
        client: AsyncClient,
        superuser_token: type_token,
        department_for_test,
    ):
        """
        Тест получения данных конкретного отдела конкретной компаний.

        При указании в пути slug отдела, который не относится к компании,
        slug которой указан в пути, ответ должен вернуться со статусом 422.
        """
        department_1, _ = await department_for_test(return_company=True)
        _, company_2 = await department_for_test(return_company=True)

        response = await client.get(
            UrlConstants.MANAGEMENT_DEPARTMENT_WITH_SLUG.format(
                company_slug=company_2.slug,
                department_slug=department_1.slug,
            ),
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert 'detail' in response.json()


@pytest.mark.asyncio(loop_scope='session')
class TestPatchDepartment:
    """Набор тестов для изменения информации отделов компании администраторами сервиса."""

    async def test_patch_departments(
        self,
        client: AsyncClient,
        superuser_token: type_token,
        department_for_test,
    ):
        """
        Тест успешного изменения данных отдела компании.

        Проверяет, что API корректно изменит данные.
        Убедимся, что ответ содержит правильные значения и API возвращает 200
        """
        payload = generate_department_data()
        department, company = await department_for_test(return_company=True)

        response = await client.patch(
            UrlConstants.MANAGEMENT_DEPARTMENT_WITH_SLUG.format(
                company_slug=company.slug,
                department_slug=department.slug,
            ),
            json=payload,
            headers=superuser_token,
        )
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        for field in ExpectedFieldsConstants.DEPARTMENT_FIELDS_FOR_ADMIN:
            assert field in data
        assert data['name'] == payload['name']

    async def test_patch_departments_access(
        self,
        client: AsyncClient,
        admin_token: type_token,
        department_for_test,
    ):
        """
        Тест успешного изменения данных отдела компании.

        Проверяет, что API корректно изменит данные,
        если запрос отправлял администратор сервиса, но не супер-пользователь.
        Убедимся, что ответ API возвращает 200.
        """
        payload = generate_department_data()
        department, company = await department_for_test(return_company=True)

        response = await client.patch(
            UrlConstants.MANAGEMENT_DEPARTMENT_WITH_SLUG.format(
                company_slug=company.slug,
                department_slug=department.slug,
            ),
            json=payload,
            headers=admin_token,
        )
        assert response.status_code == status.HTTP_200_OK, response.text

    async def test_patch_departments_not_access(
        self,
        client: AsyncClient,
        moderator_token: type_token,
        employee_token: type_token,
        department_for_test,
    ):
        """
        Тест изменения данных отдела компании.

        Проверяет, что API не изменит данные,
        если запрос отправлял не администратор сервиса или не супер-пользователь.
        Убедимся, что ответ API возвращает 401.
        """
        payload = generate_department_data()
        department, company = await department_for_test(return_company=True)
        tokens_bad = (
            moderator_token,
            employee_token,
            {'Authorization': 'foo.bar.baz'},
            None,
        )
        for token in tokens_bad:
            response = await client.patch(
                UrlConstants.MANAGEMENT_DEPARTMENT_WITH_SLUG.format(
                    company_slug=company.slug,
                    department_slug=department.slug,
                ),
                json=payload,
                headers=token,
            )
            assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text

    async def test_patch_departments_whitespace(
        self,
        client: AsyncClient,
        superuser_token: type_token,
        department_for_test,
    ):
        """
        Тест успешного изменения данных отдела компании,
        если в строковых полях присутствуют пробелы по краям.

        Проверяет, что API корректно изменяется отдел.
        Убедимся, что API возвращает 200
        """
        name = 'Отдел'
        bad_payload = {'name': f' {name} '}
        department, company = await department_for_test(return_company=True)

        response = await client.patch(
            UrlConstants.MANAGEMENT_DEPARTMENT_WITH_SLUG.format(
                company_slug=company.slug,
                department_slug=department.slug,
            ),
            json=bad_payload,
            headers=superuser_token,
        )
        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        for field in ExpectedFieldsConstants.DEPARTMENT_FIELDS_FOR_ADMIN:
            assert field in data
        assert data['name'] == name

    @pytest.mark.parametrize(
        'length_name, status_',
        (
            (LengthConstants.MAX_NAME_DEPARTMENT, status.HTTP_200_OK),
            (LengthConstants.MAX_NAME_DEPARTMENT + 1, status.HTTP_422_UNPROCESSABLE_ENTITY),
        ),
    )
    async def test_patch_departments_length_name(
        self,
        client: AsyncClient,
        superuser_token: type_token,
        department_for_test,
        length_name,
        status_,
    ):
        """
        Тест изменения данных отдела компании, при придельном количестве символов в поле `name`.

        Если количество максимально - отдел будет создан.
        Если привешает максимальное - должна быть ошибка 422.
        """
        payload = {'name': 'x' * length_name}
        department, company = await department_for_test(return_company=True)

        response = await client.patch(
            UrlConstants.MANAGEMENT_DEPARTMENT_WITH_SLUG.format(
                company_slug=company.slug,
                department_slug=department.slug,
            ),
            json=payload,
            headers=superuser_token,
        )
        assert response.status_code == status_, response.text

    async def test_patch_departments_not_company(
        self,
        client: AsyncClient,
        superuser_token: type_token,
        department_for_test,
    ):
        """
        Тест изменения данных отдела компании.

        При указании в пути несуществующего slug компании, ответ должен вернуться со статусом 404.
        """
        payload = generate_department_data()
        department, company = await department_for_test(return_company=True)
        bad_company_slug = company.slug + 'x'

        response = await client.patch(
            UrlConstants.MANAGEMENT_DEPARTMENT_WITH_SLUG.format(
                company_slug=bad_company_slug,
                department_slug=department.slug,
            ),
            json=payload,
            headers=superuser_token,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
        assert (response_json := response.json()['detail']) == (
            f'Не найден объект Company по данному slug: {bad_company_slug}'
        ), response_json

    async def test_patch_departments_not_department(
        self,
        client: AsyncClient,
        superuser_token: type_token,
        department_for_test,
    ):
        """
        Тест изменения данных отдела компании.

        При указании в пути несуществующего slug отдела, ответ должен вернуться со статусом 404.
        """
        payload = generate_department_data()
        department, company = await department_for_test(return_company=True)
        bad_department_slug = department.slug + 'x'

        response = await client.patch(
            UrlConstants.MANAGEMENT_DEPARTMENT_WITH_SLUG.format(
                company_slug=company.slug,
                department_slug=bad_department_slug,
            ),
            json=payload,
            headers=superuser_token,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
        assert (response_json := response.json()['detail']) == (
            f'Не найден объект Department по данному slug: {bad_department_slug}'
        ), response_json

    async def test_patch_department_department_not_in_company(
        self,
        client: AsyncClient,
        superuser_token: type_token,
        department_for_test,
    ):
        """
        Тест изменения данных конкретного отдела конкретной компаний.

        При указании в пути slug отдела, который не относится к компании,
        slug которой указан в пути, ответ должен вернуться со статусом 422.
        """
        payload = generate_department_data()
        department_1, _ = await department_for_test(return_company=True)
        _, company_2 = await department_for_test(return_company=True)

        response = await client.patch(
            UrlConstants.MANAGEMENT_DEPARTMENT_WITH_SLUG.format(
                company_slug=company_2.slug,
                department_slug=department_1.slug,
            ),
            json=payload,
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert 'detail' in response.json()

    async def test_patch_department_duplicate_in_company(
        self,
        client: AsyncClient,
        superuser_token: type_token,
        department_for_test,
    ):
        """
        Тест изменения данных отдела компании.

        В одной компании не может быть двух отделов с одинаковым названием.
        При попытке изменить второй отдел на название первого должна быть ошибка 400.
        """
        department_1, company = await department_for_test(return_company=True)
        department_2 = await department_for_test({'company_id': company.id})
        payload = {'name': department_1.name}

        response = await client.patch(
            UrlConstants.MANAGEMENT_DEPARTMENT_WITH_SLUG.format(
                company_slug=company.slug,
                department_slug=department_2.slug,
            ),
            json=payload,
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text
        assert 'detail' in response.json()

    async def test_patch_department_duplicate_in_another_company(
        self,
        client: AsyncClient,
        superuser_token: type_token,
        department_for_test,
    ):
        """
        Тест изменения данных отдела компании.

        В двух разных компаниях может быть созданы отделы с одинаковым названием.
        При попытке изменить название отдел в одной компании на название отдела другой
        должен быть ответ 200, а slug у них должен быть разный.
        """
        department_1, _ = await department_for_test(return_company=True)
        department_2, company_2 = await department_for_test(return_company=True)
        payload = {'name': department_1.name}

        response = await client.patch(
            UrlConstants.MANAGEMENT_DEPARTMENT_WITH_SLUG.format(
                company_slug=company_2.slug,
                department_slug=department_2.slug,
            ),
            json=payload,
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        assert data['name'] == department_1.name
        assert data['slug'] != department_1.slug


@pytest.mark.asyncio(loop_scope='session')
class TestDeleteDepartment:
    """Набор тестов удаления отдела компании администраторами сервиса."""

    async def test_delete_departments(
        self,
        client: AsyncClient,
        superuser_token: type_token,
        department_for_test,
    ):
        """
        Тест успешного удаления данных отдела компании.

        Проверяет, что API корректно удалит данные.
        Убедимся, что API возвращает 204
        """
        department, company = await department_for_test(return_company=True)

        response = await client.delete(
            UrlConstants.MANAGEMENT_DEPARTMENT_WITH_SLUG.format(
                company_slug=company.slug,
                department_slug=department.slug,
            ),
            headers=superuser_token,
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT, response.text

    async def test_delete_departments_access(
        self,
        client: AsyncClient,
        admin_token: type_token,
        department_for_test,
    ):
        """
        Тест успешного удаления данных отдела компании.

        Проверяет, что API корректно удалит данные,
        если запрос отправлял администратор сервиса, но не супер-пользователь.
        Убедимся, что ответ API возвращает 204.
        """
        department, company = await department_for_test(return_company=True)

        response = await client.delete(
            UrlConstants.MANAGEMENT_DEPARTMENT_WITH_SLUG.format(
                company_slug=company.slug,
                department_slug=department.slug,
            ),
            headers=admin_token,
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT, response.text

    async def test_delete_departments_not_access(
        self,
        client: AsyncClient,
        moderator_token: type_token,
        employee_token: type_token,
        department_for_test,
    ):
        """
        Тест удаления данных отдела компании.

        Проверяет, что API удалит данные,
        если запрос отправлял не администратор сервиса или не супер-пользователь.
        Убедимся, что ответ API возвращает 401.
        """
        department, company = await department_for_test(return_company=True)
        tokens_bad = (
            moderator_token,
            employee_token,
            {'Authorization': 'foo.bar.baz'},
            None,
        )
        for token in tokens_bad:
            response = await client.delete(
                UrlConstants.MANAGEMENT_DEPARTMENT_WITH_SLUG.format(
                    company_slug=company.slug,
                    department_slug=department.slug,
                ),
                headers=token,
            )
            assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text

    async def test_delete_departments_not_company(
        self,
        client: AsyncClient,
        superuser_token: type_token,
        department_for_test,
    ):
        """
        Тест Удаление отдела компании.

        При указании в пути несуществующего slug компании, ответ должен вернуться со статусом 404.
        """
        department, company = await department_for_test(return_company=True)
        bad_company_slug = company.slug + 'x'

        response = await client.delete(
            UrlConstants.MANAGEMENT_DEPARTMENT_WITH_SLUG.format(
                company_slug=bad_company_slug,
                department_slug=department.slug,
            ),
            headers=superuser_token,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
        assert (response_json := response.json()['detail']) == (
            f'Не найден объект Company по данному slug: {bad_company_slug}'
        ), response_json

    async def test_delete_departments_not_department(
        self,
        client: AsyncClient,
        superuser_token: type_token,
        department_for_test,
    ):
        """
        Тест удаление отдела компании.

        При указании в пути несуществующего slug отдела, ответ должен вернуться со статусом 404.
        """
        payload = generate_department_data()
        department, company = await department_for_test(return_company=True)
        bad_department_slug = department.slug + 'x'

        response = await client.patch(
            UrlConstants.MANAGEMENT_DEPARTMENT_WITH_SLUG.format(
                company_slug=company.slug,
                department_slug=bad_department_slug,
            ),
            json=payload,
            headers=superuser_token,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
        assert (response_json := response.json()['detail']) == (
            f'Не найден объект Department по данному slug: {bad_department_slug}'
        ), response_json

    async def test_delete_department_department_not_in_company(
        self,
        client: AsyncClient,
        superuser_token: type_token,
        department_for_test,
    ):
        """
        Тест удаление конкретного отдела конкретной компаний.

        При указании в пути slug отдела, который не относится к компании,
        slug которой указан в пути, ответ должен вернуться со статусом 422.
        """
        department_1, _ = await department_for_test(return_company=True)
        _, company_2 = await department_for_test(return_company=True)

        response = await client.delete(
            UrlConstants.MANAGEMENT_DEPARTMENT_WITH_SLUG.format(
                company_slug=company_2.slug,
                department_slug=department_1.slug,
            ),
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert 'detail' in response.json()
