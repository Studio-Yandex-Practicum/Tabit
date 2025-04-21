from datetime import datetime, timedelta, timezone

import pytest
from fastapi import status
from httpx import AsyncClient

from src.core.constants import Directory
from tests.constants import IMAGE_BASE64_JPG, IMAGE_BASE64_PNG, INVALID_IMAGE, ONE, URL, _token
from tests.utils import random_string


def generate_company_data(all_fields=False, license_id=None):
    """Генерирует реалистичные данные для создания компании."""

    data = {'name': f'Компания {random_string(5)}'}

    if all_fields:
        data.update(
            {
                'description': f'Описание компании {random_string(15)}',
                'logo': IMAGE_BASE64_PNG,
                'license_id': license_id,
                'start_license_time': '2025-02-15T07:57:45.058Z',
                'slug': f'company-{random_string(8).lower()}',
            }
        )

    return data


def get_path_logo(slug: str, expansion: str = 'png') -> str:
    """Генерирует путь логотипа по переданному слагу."""
    return f'{Directory.MEDIA}/{Directory.LOGO}/{slug}.{expansion}'


class TestCreateCompany:
    """Набор тестов для создания компании администраторами сервиса."""

    @pytest.mark.asyncio
    async def test_create_company_required_fields(
        self,
        client: AsyncClient,
        superuser_token: _token,
    ):
        """
        Тест успешного создания компании с обязательными полями.

        Проверяет, что API корректно создаёт компанию при передаче только обязательных данных.
        Убедимся, что ответ содержит правильные значения и API возвращает 201
        """
        payload = generate_company_data()

        response = await client.post(
            URL.COMPANIES_ENDPOINT,
            json=payload,
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_201_CREATED, response.text
        data = response.json()
        assert data['name'] == payload['name']
        assert 'slug' in data
        assert 'is_active' in data
        assert 'end_license_time' in data
        assert 'max_admins_count' in data
        assert 'max_employees_count' in data

    @pytest.mark.asyncio
    async def test_create_company_all_fields(
        self, client: AsyncClient, superuser_token: _token, license_for_test
    ):
        """
        Тест успешного создания компании со всеми полями.

        Проверяет, что API корректно создаёт компанию при передаче всех полей.
        Убедимся, что ответ содержит правильные значения и API возвращает 201
        """
        new_license = await license_for_test()
        payload = generate_company_data(all_fields=True, license_id=new_license.id)

        response = await client.post(
            URL.COMPANIES_ENDPOINT,
            json=payload,
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_201_CREATED, response.text
        data = response.json()
        assert data['name'] == payload['name']
        assert data['slug'] == payload['slug']
        assert data['description'] == payload['description']
        assert data['logo'] == get_path_logo(payload['slug'])

    @pytest.mark.asyncio
    async def test_create_company_duplicate_slug(
        self, client: AsyncClient, superuser_token: _token, license_for_test
    ):
        """
        Тест ошибки 400 при создании компании с уже существующим slug.

        Проверяет, что API не позволяет создать компанию с дублирующимся slug.
        Убедимся, что ответ содержит правильное сообщение об ошибке и статус-код 400.
        """
        new_license = await license_for_test()
        payload = generate_company_data(all_fields=True, license_id=new_license.id)

        response = await client.post(
            URL.COMPANIES_ENDPOINT,
            json=payload,
            headers=superuser_token,
        )
        assert response.status_code == status.HTTP_201_CREATED, response.text

        response = await client.post(
            URL.COMPANIES_ENDPOINT,
            json=payload,
            headers=superuser_token,
        )
        assert response.status_code == 400, response.text
        assert (
            response.json()['detail']
            == f"Компания с таким slug '{payload['slug']}' уже существует."
        )

    @pytest.mark.asyncio
    async def test_create_company_missing_name(
        self, client: AsyncClient, superuser_token: _token, license_for_test
    ):
        """
        Тест ошибки 422 при создании компании без обязательного поля 'name'.

        Проверяет, что API не позволяет создать компанию, если отсутствует поле 'name'.
        Убедимся, что ответ содержит правильное сообщение об ошибке и статус-код 422.
        """
        new_license = await license_for_test()
        payload = generate_company_data(all_fields=True, license_id=new_license.id)
        del payload['name']

        response = await client.post(
            URL.COMPANIES_ENDPOINT,
            json=payload,
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text
        error_detail = response.json()['detail']
        assert any(
            error['loc'] == ['body', 'name'] and error['msg'] == 'Field required'
            for error in error_detail
        ), response.text

    @pytest.mark.asyncio
    async def test_create_company_name_too_short(
        self, client: AsyncClient, superuser_token: _token, license_for_test
    ):
        """
        Тест ошибки 422 при создании компании с name менее 2 символов.

        Проверяет, что API не позволяет создать компанию, если поле name содержит менее 2 символов.
        Убедимся, что ответ содержит правильное сообщение об ошибке и статус-код 422.
        """
        new_license = await license_for_test()
        payload = generate_company_data(all_fields=True, license_id=new_license.id)
        payload['name'] = '1'

        response = await client.post(
            URL.COMPANIES_ENDPOINT,
            json=payload,
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text
        error_detail = response.json()['detail']
        assert any(
            error['loc'] == ['body', 'name']
            and error['msg'] == 'String should have at least 2 characters'
            for error in error_detail
        ), response.text

    @pytest.mark.asyncio
    async def test_create_company_name_too_long(
        self, client: AsyncClient, superuser_token: _token, license_for_test
    ):
        """
        Тест ошибки 422 при создании компании с name более 255 символов.

        Проверяет, что API не создает компанию, если поле name содержит более 255 символов.
        Убедимся, что ответ содержит правильное сообщение об ошибке и статус-код 422.
        """
        new_license = await license_for_test()
        payload = generate_company_data(all_fields=True, license_id=new_license.id)
        payload['name'] = 's' * 256

        response = await client.post(
            URL.COMPANIES_ENDPOINT,
            json=payload,
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text
        error_detail = response.json()['detail']
        assert any(
            error['loc'] == ['body', 'name']
            and error['msg'] == 'String should have at most 255 characters'
            for error in error_detail
        ), response.text

    @pytest.mark.asyncio
    async def test_create_company_without_token(self, client: AsyncClient, license_for_test):
        """
        Тест ошибки 401 при создании компании без токена.

        Проверяет, что API не позволяет создать компанию без авторизации.
        Убедимся, что ответ содержит сообщение 'Unauthorized' и статус-код 401.
        """
        new_license = await license_for_test()
        payload = generate_company_data(all_fields=True, license_id=new_license.id)

        response = await client.post(
            URL.COMPANIES_ENDPOINT,
            json=payload,
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text
        assert response.json()['detail'] == 'Unauthorized'

    @pytest.mark.asyncio
    async def test_create_company_invalid_token(self, client: AsyncClient, license_for_test):
        """
        Тест ошибки 401 при создании компании с некорректным токеном.

        Проверяет, что API не позволяет создать компанию с недействительным токеном.
        Убедимся, что ответ содержит сообщение 'Unauthorized' и статус-код 401.
        """
        new_license = await license_for_test()
        payload = generate_company_data(all_fields=True, license_id=new_license.id)

        invalid_token = {'Authorization': 'Bearer invalid_token_123'}

        response = await client.post(
            URL.COMPANIES_ENDPOINT,
            json=payload,
            headers=invalid_token,
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text
        assert response.json()['detail'] == 'Unauthorized'

    @pytest.mark.asyncio
    async def test_create_company_invalid_description_type(
        self, client: AsyncClient, superuser_token: _token, license_for_test
    ):
        """
        Тест ошибки 422 при передаче числа в поле 'description'.

        Проверяет, что API не позволяет создать компанию,
        если поле 'description' передано не в виде строки.
        """
        new_license = await license_for_test()
        payload = generate_company_data(all_fields=True, license_id=new_license.id)
        payload['description'] = 1

        response = await client.post(
            URL.COMPANIES_ENDPOINT,
            json=payload,
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text
        assert any(
            error['loc'] == ['body', 'description']
            and error['msg'] == 'Input should be a valid string'
            for error in response.json()['detail']
        ), response.text

    @pytest.mark.asyncio
    async def test_create_company_invalid_logo_type(
        self, client: AsyncClient, superuser_token: _token, license_for_test
    ):
        """
        Тест ошибки 422 при передаче массива в поле 'logo'.

        Проверяет, что API не позволяет создать компанию, если поле logo передано не в виде строки.
        """
        new_license = await license_for_test()
        payload = generate_company_data(all_fields=True, license_id=new_license.id)
        payload['logo'] = ['invalid_logo_url']

        response = await client.post(
            URL.COMPANIES_ENDPOINT,
            json=payload,
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text
        assert any(
            error['loc'] == ['body', 'logo'] and error['msg'] == 'Input should be a valid string'
            for error in response.json()['detail']
        ), response.text

    @pytest.mark.asyncio
    async def test_create_company_invalid_start_license_time_type(
        self, client: AsyncClient, superuser_token: _token, license_for_test
    ):
        """
        Тест ошибки 422 при передаче некорректного формата даты в поле 'start_license_time'.

        Проверяет, что API не позволяет создать компанию,
        если поле 'start_license_time' передано в неверном формате.
        """
        new_license = await license_for_test()
        payload = generate_company_data(all_fields=True, license_id=new_license.id)
        payload['start_license_time'] = 'invalid_date'

        response = await client.post(
            URL.COMPANIES_ENDPOINT,
            json=payload,
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text
        assert any(
            error['loc'] == ['body', 'start_license_time']
            and error['msg']
            == 'Input should be a valid datetime or date, invalid character in year'
            for error in response.json()['detail']
        ), response.text

    @pytest.mark.asyncio
    async def test_create_company_description_too_short(
        self, client: AsyncClient, superuser_token: _token, license_for_test
    ):
        """
        Тест ошибки 422 при создании компании с description менее 2 символов.

        Проверяет, что API не позволяет создать компанию,
        если поле description содержит менее 2 символов.
        Убедимся, что ответ содержит правильное сообщение об ошибке и статус-код 422.
        """
        new_license = await license_for_test()
        payload = generate_company_data(all_fields=True, license_id=new_license.id)
        payload['description'] = 'A'

        response = await client.post(
            URL.COMPANIES_ENDPOINT,
            json=payload,
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text
        error_detail = response.json()['detail']
        assert any(
            error['loc'] == ['body', 'description']
            and error['msg'] == 'String should have at least 2 characters'
            for error in error_detail
        ), response.text

    @pytest.mark.asyncio
    async def test_create_company_description_too_long(
        self, client: AsyncClient, superuser_token: _token, license_for_test
    ):
        """
        Тест ошибки 422 при создании компании с description более 1000 символов.

        Проверяет, что API не позволяет создать компанию,
        если поле description содержит более 1000 символов.
        Убедимся, что ответ содержит правильное сообщение об ошибке и статус-код 422.
        """
        new_license = await license_for_test()
        payload = generate_company_data(all_fields=True, license_id=new_license.id)
        payload['description'] = 'A' * 256

        response = await client.post(
            URL.COMPANIES_ENDPOINT,
            json=payload,
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text
        error_detail = response.json()['detail']
        assert any(
            error['loc'] == ['body', 'description']
            and error['msg'] == 'String should have at most 255 characters'
            for error in error_detail
        ), response.text

    @pytest.mark.asyncio
    async def test_generate_unique_slug(self, client: AsyncClient, superuser_token: _token):
        """
        Тест успешной генерации уникального slug для компаний с одинаковыми названиями.

        Проверяет, что при создании двух компаний с одинаковым полем `name`
        их slug-значения будут разными. Убедимся, что API корректно обрабатывает
        дублирование названия и добавляет уникальный идентификатор в slug второй компании.
        """
        company_name = 'Тестовая Компания'

        jwt_token = superuser_token

        payload_1 = {'name': company_name}
        response_1 = await client.post(
            URL.COMPANIES_ENDPOINT,
            json=payload_1,
            headers=jwt_token,
        )
        assert response_1.status_code == status.HTTP_201_CREATED
        first_company_slug = response_1.json()['slug']

        payload_2 = {'name': company_name}
        response_2 = await client.post(
            URL.COMPANIES_ENDPOINT,
            json=payload_2,
            headers=jwt_token,
        )
        assert response_2.status_code == status.HTTP_201_CREATED
        second_company_slug = response_2.json()['slug']

        assert first_company_slug != second_company_slug, 'Слаг должен быть уникальным'
        assert second_company_slug.startswith(
            first_company_slug.split('-')[0]
        ), 'Слаг должен базироваться на названии'

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'invalid_value, message',
        INVALID_IMAGE,
    )
    async def test_create_company_invalid_logo_url(
        self,
        client: AsyncClient,
        superuser_token: _token,
        license_for_test,
        invalid_value,
        message,
    ):
        """
        Тест ошибки при передаче некорректной строки в 'logo'.

        Проверяет, что API не позволяет создать компанию,
        если поле 'logo' передано не в формате строки Base64.
        """
        new_license = await license_for_test()
        payload = generate_company_data(all_fields=True, license_id=new_license.id)
        payload['logo'] = invalid_value

        response = await client.post(
            URL.COMPANIES_ENDPOINT,
            json=payload,
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text
        error_detail = response.json()
        assert 'detail' in error_detail, response.text
        assert message == error_detail['detail']
        assert message == (
            detail := error_detail['detail']
        ), f'Ожидалось:\n{message}\nПолучили\n{detail}'

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'field, invalid_value',
        [
            ('name', ' Company'),
            ('name', 'Company '),
            ('description', ' Описание компании'),
            ('description', 'Описание компании '),
        ],
    )
    async def test_create_company_field_with_leading_or_trailing_spaces(
        self,
        client: AsyncClient,
        superuser_token: _token,
        license_for_test,
        field: str,
        invalid_value: str,
    ):
        """
        Тест ошибки 422 при передаче полей 'name' и 'description'
        с начальным или завершающим пробелом.

        Проверяет, что API не позволяет создавать компанию, если значения
        в полях 'name' или 'description' начинаются или заканчиваются пробелом.
        """
        new_license = await license_for_test()
        payload = generate_company_data(all_fields=True, license_id=new_license.id)
        payload[field] = invalid_value

        response = await client.post(
            URL.COMPANIES_ENDPOINT,
            json=payload,
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text
        error_detail = response.json()['detail']
        assert any(
            error['loc'] == ['body', field]
            and error['msg'] == 'Value error, Поле не может начинаться или заканчиваться пробелом.'
            for error in error_detail
        ), response.text

    @pytest.mark.asyncio
    async def test_create_company_without_license_and_start_time(
        self, client: AsyncClient, superuser_token: _token
    ):
        """
        Тест создания компании без 'license_id' и 'start_license_time'.

        Проверяет, что если не переданы 'license_id' и 'start_license_time',
        поле 'end_license_time' остается 'null'.
        """
        payload = generate_company_data()

        response = await client.post(
            URL.COMPANIES_ENDPOINT,
            json=payload,
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_201_CREATED, response.text
        data = response.json()
        assert data['end_license_time'] is None

    @pytest.mark.asyncio
    async def test_create_company_only_license_id(
        self, client: AsyncClient, superuser_token: _token, license_for_test
    ):
        """
        Тест ошибки 422 при передаче только 'license_id' без 'start_license_time'.

        Проверяет, что API не позволяет создать компанию, если передан 'license_id',
        но отсутствует 'start_license_time'.
        """
        new_license = await license_for_test()
        payload = generate_company_data(all_fields=True, license_id=new_license.id)
        del payload['start_license_time']

        response = await client.post(
            URL.COMPANIES_ENDPOINT,
            json=payload,
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text
        error_detail = response.json()['detail']
        assert any(
            error['msg']
            == (
                'Value error, Поля начала действия лицензии и '
                'тип лицензии заполняются одновременно.'
            )
            for error in error_detail
        ), response.text

    @pytest.mark.asyncio
    async def test_create_company_only_start_license_time(
        self, client: AsyncClient, superuser_token: _token
    ):
        """
        Тест ошибки 422 при передаче только 'start_license_time' без 'license_id'.

        Проверяет, что API не позволяет создать компанию, если передан 'start_license_time',
        но отсутствует 'license_id'.
        """
        payload = generate_company_data(all_fields=True)
        del payload['license_id']

        response = await client.post(
            URL.COMPANIES_ENDPOINT,
            json=payload,
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text
        error_detail = response.json()['detail']
        assert any(
            error['msg']
            == (
                'Value error, Поля начала действия лицензии и '
                'тип лицензии заполняются одновременно.'
            )
            for error in error_detail
        ), response.text

    @pytest.mark.asyncio
    async def test_create_company_non_existent_license(
        self, client: AsyncClient, superuser_token: _token, license_for_test
    ):
        """
        Тест ошибки 400 при создании компании с несуществующей license.

        Проверяет, что API не позволяет создать компанию с несуществующей license.
        Убедимся, что ответ содержит правильное сообщение об ошибке и статус-код 400.
        """
        new_license = await license_for_test()
        payload = generate_company_data(all_fields=True, license_id=new_license.id + ONE)

        jwt_token = superuser_token

        response = await client.post(
            URL.COMPANIES_ENDPOINT,
            json=payload,
            headers=jwt_token,
        )
        assert (
            response.status_code == 400
        ), 'Статус-код должен быть 400 при попытки создать компанию с несуществующей license'
        assert response.json()['detail'] == f'Лицензия с id {payload["license_id"]} не найдена.'

    @pytest.mark.asyncio
    async def test_create_company_existent_license(
        self, client: AsyncClient, superuser_token: _token, license_for_test
    ):
        """
        Тест успешного создания компании с существующей license.

        Проверяет, что API позволяет создать компанию с существующей license.
        Убедимся, что ответ содержит правильные значения и API возвращает 201
        """
        new_license = await license_for_test()
        payload = generate_company_data(all_fields=True, license_id=new_license.id)

        response = await client.post(
            URL.COMPANIES_ENDPOINT,
            json=payload,
            headers=superuser_token,
        )
        assert (
            response.status_code == status.HTTP_201_CREATED
        ), 'Статус-код должен быть 201 при попытки создать компанию с существующей license'
        data = response.json()
        assert data['license_id'] == payload['license_id']


class TestGetCompany:
    """Тесты получения списка компаний с сортировкой."""

    @pytest.mark.asyncio
    async def test_get_companies_success(
        self,
        client: AsyncClient,
        superuser_token: _token,
        company_for_test,
    ):
        """
        Тест успешного получения списка компаний.

        Проверяет, что API возвращает статус-код status.HTTP_200_OK и список компаний.
        Убедимся, что данные содержат ожидаемые поля.
        """
        await company_for_test({'name': 'Компания 1'})
        await company_for_test({'name': 'Компания 2'})

        response = await client.get(
            URL.COMPANIES_ENDPOINT,
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_200_OK, response.text
        companies = response.json()

        assert isinstance(companies, list), 'Ответ API должен быть списком компаний'
        assert len(companies) >= 2, 'В ответе должно быть как минимум две компании'

        expected_fields = {
            'id',
            'name',
            'description',
            'logo',
            'license_id',
            'max_admins_count',
            'max_employees_count',
            'start_license_time',
            'end_license_time',
            'is_active',
            'slug',
            'created_at',
            'updated_at',
        }

        for company in companies:
            assert expected_fields.issubset(
                company.keys()
            ), f'Компания должна содержать поля: {expected_fields}'

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'ordering, expected_sort',
        [
            ('name', lambda companies: sorted(companies, key=lambda x: x['name'])),
            ('-name', lambda companies: sorted(companies, key=lambda x: x['name'], reverse=True)),
            ('created_at', lambda companies: sorted(companies, key=lambda x: x['created_at'])),
            (
                '-created_at',
                lambda companies: sorted(companies, key=lambda x: x['created_at'], reverse=True),
            ),
            ('updated_at', lambda companies: sorted(companies, key=lambda x: x['updated_at'])),
            (
                '-updated_at',
                lambda companies: sorted(companies, key=lambda x: x['updated_at'], reverse=True),
            ),
        ],
    )
    async def test_get_companies_sorting(
        self,
        client: AsyncClient,
        superuser_token: _token,
        company_for_test,
        ordering,
        expected_sort,
    ):
        """
        Тест сортировки списка компаний по полям `name`, `created_at` и `updated_at`.

        Проверяет, что API корректно сортирует список компаний в порядке возрастания и убывания.
        """

        (await company_for_test({'name': 'Beta'}),)
        (await company_for_test({'name': 'Alpha'}),)
        (await company_for_test({'name': 'Gamma'}),)

        response = await client.get(
            f'{URL.COMPANIES_ENDPOINT}?ordering={ordering}',
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_200_OK, response.text
        result = response.json()

        sorted_companies = expected_sort(result)
        assert [c['name'] for c in result] == [c['name'] for c in sorted_companies]

    @pytest.mark.asyncio
    async def test_get_companies_without_token(
        self,
        client: AsyncClient,
    ):
        """
        Тест ошибки 401 при получении списка компаний без токена.

        Проверяет, что API не позволяет получить список компаний без авторизации.
        Убедимся, что ответ содержит сообщение 'Unauthorized' и статус-код 401.
        """

        response = await client.get(
            URL.COMPANIES_ENDPOINT,
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text
        assert response.json()['detail'] == 'Unauthorized'

    @pytest.mark.asyncio
    async def test_get_companies_invalid_token(self, client: AsyncClient):
        """
        Тест ошибки 401 при получении списка компаний с некорректным токеном.

        Проверяет, что API не позволяет получить список компаний с недействительным токеном.
        Убедимся, что ответ содержит сообщение 'Unauthorized' и статус-код 401.
        """

        invalid_token = {'Authorization': 'Bearer invalid_token_123'}

        response = await client.get(
            URL.COMPANIES_ENDPOINT,
            headers=invalid_token,
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text
        assert response.json()['detail'] == 'Unauthorized'

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'update_data, expected_field, expected_value',
        [
            ({'description': 'Новое описание'}, 'description', 'Новое описание'),
            ({'logo': IMAGE_BASE64_JPG}, 'logo', ''),
            ({'name': 'Новое имя'}, 'name', 'Новое имя'),
            ({'license_id': 1, 'start_license_time': datetime.now().isoformat()}, 'license_id', 1),
        ],
    )
    async def test_patch_company_single_field(
        self,
        client: AsyncClient,
        superuser_token: _token,
        company_for_test,
        update_data,
        expected_field,
        expected_value,
        license_for_test,
    ):
        """
        Тест успешного обновления одного поля компании через PATCH запрос.

        Проверяет, что API корректно обновляет указанное поле компании и возвращает
        ожидаемое значение. Используется параметризация для проверки разных полей.
        """
        company = await company_for_test()

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()
        if expected_field == 'logo':
            expected_value = get_path_logo(company.slug, 'jpg')
        assert data[expected_field] == expected_value, (
            f'Ожидалось значение {expected_value} в поле {expected_field}, '
            f'но получено {data[expected_field]}'
        )

    @pytest.mark.asyncio
    async def test_patch_company_all_fields(
        self,
        client: AsyncClient,
        superuser_token: _token,
        license_for_test,
        company_for_test,
    ):
        """
        Тест успешного обновления всех полей компании через PATCH запрос.

        Проверяет, что API корректно обновляет все поля компании и возвращает ожидаемые значения.
        """
        new_license = await license_for_test()
        company = await company_for_test()

        update_data = {
            'description': 'Обновленное описание',
            'logo': IMAGE_BASE64_JPG,
            'name': 'Обновленное имя',
            'license_id': new_license.id,
            'start_license_time': datetime.now(timezone.utc).isoformat(),
        }

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()

        for key, value in update_data.items():
            if 'time' in key and value:
                actual_time = datetime.fromisoformat(data[key]).isoformat()
                assert (
                    actual_time == value
                ), f'Ожидалось значение {value} в поле {key}, но получено {actual_time}'
            elif 'logo' == key:
                assert data[key] == get_path_logo(
                    company.slug, 'jpg'
                ), f'Ожидалось значение {value} в поле {key}, но получено {data[key]}'
            else:
                assert (
                    data[key] == value
                ), f'Ожидалось значение {value} в поле {key}, но получено {data[key]}'

    @pytest.mark.asyncio
    async def test_patch_company_name_too_short(
        self, client: AsyncClient, superuser_token: _token, company_for_test
    ):
        """
        Тест ошибки 422 при обновлении компании с name менее 2 символов.

        Проверяет, что API не позволяет обновить компанию, если поле name содержит менее 2 символов
        Убедимся, что ответ содержит правильное сообщение об ошибке и статус-код 422.
        """
        company = await company_for_test()

        update_data = {'name': 'A'}

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text
        error_detail = response.json()['detail']
        assert any(
            error['loc'] == ['body', 'name']
            and error['msg'] == 'String should have at least 2 characters'
            for error in error_detail
        ), response.text

    @pytest.mark.asyncio
    async def test_patch_company_name_too_long(
        self, client: AsyncClient, superuser_token: _token, company_for_test
    ):
        """
        Тест ошибки 422 при обновлении компании с name более 255 символов.

        Проверяет, что API не позволяет обновить компанию,
        если поле name содержит более 255 символов.
        Убедимся, что ответ содержит правильное сообщение об ошибке и статус-код 422.
        """
        company = await company_for_test()

        update_data = {'name': 's' * 256}

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text
        error_detail = response.json()['detail']
        assert any(
            error['loc'] == ['body', 'name']
            and error['msg'] == 'String should have at most 255 characters'
            for error in error_detail
        ), response.text

    @pytest.mark.asyncio
    async def test_patch_company_without_token(
        self,
        client: AsyncClient,
        company_for_test,
    ):
        """
        Тест ошибки 401 при обновлении компании без токена.

        Проверяет, что API не позволяет обновить компанию без авторизации.
        Убедимся, что ответ содержит сообщение 'Unauthorized' и статус-код 401.
        """
        company = await company_for_test()
        update_data = {'name': 'Новое имя'}

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text
        assert response.json()['detail'] == 'Unauthorized'

    @pytest.mark.asyncio
    async def test_patch_company_invalid_token(self, client: AsyncClient, company_for_test):
        """
        Тест ошибки 401 при обновлении компании с некорректным токеном.

        Проверяет, что API не позволяет обновить компанию с недействительным токеном.
        Убедимся, что ответ содержит сообщение 'Unauthorized' и статус-код 401.
        """
        company = await company_for_test()

        update_data = {'name': 'Новое имя'}

        invalid_token = {'Authorization': 'Bearer invalid_token_123'}

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
            headers=invalid_token,
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text
        assert response.json()['detail'] == 'Unauthorized'


class TestPatchCompanyValidation:
    """Тесты валидации данных при обновлении компании через PATCH запрос."""

    @pytest.mark.asyncio
    async def test_patch_company_invalid_description_type(
        self, client: AsyncClient, superuser_token: _token, company_for_test
    ):
        """Тест ошибки 422 при передаче числа в поле 'description'."""
        company = await company_for_test()
        update_data = {'description': 1}

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text

    @pytest.mark.asyncio
    async def test_patch_company_invalid_logo_type(
        self, client: AsyncClient, superuser_token: _token, company_for_test
    ):
        """Тест ошибки 422 при передаче массива в поле 'logo'."""
        company = await company_for_test()
        update_data = {'logo': ['invalid_logo_url']}

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text

    @pytest.mark.asyncio
    async def test_patch_company_invalid_license_id_type(
        self, client: AsyncClient, superuser_token: _token, company_for_test
    ):
        """Тест ошибки 422 при передаче строки в поле 'license_id'."""
        company = await company_for_test()
        update_data = {'license_id': 'invalid_id'}

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text

    @pytest.mark.asyncio
    async def test_patch_company_invalid_start_license_time_type(
        self, client: AsyncClient, superuser_token: _token, company_for_test
    ):
        """Тест ошибки 422 при некорректном формате 'start_license_time'."""
        company = await company_for_test()
        update_data = {'start_license_time': 'invalid_date'}

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text

    @pytest.mark.asyncio
    async def test_patch_company_description_too_short(
        self, client: AsyncClient, superuser_token: _token, company_for_test
    ):
        """Тест ошибки 422 при 'description' менее 2 символов."""
        company = await company_for_test()
        update_data = {'description': 'A'}

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text

    @pytest.mark.asyncio
    async def test_patch_company_description_too_long(
        self, client: AsyncClient, superuser_token: _token, company_for_test
    ):
        """Тест ошибки 422 при 'description' более 255 символов."""
        company = await company_for_test()
        update_data = {'description': 'A' * 256}

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'invalid_value, message',
        INVALID_IMAGE,
    )
    async def test_patch_company_invalid_logo_url(
        self,
        client: AsyncClient,
        superuser_token: _token,
        company_for_test,
        invalid_value,
        message,
    ):
        """
        Тест ошибки при передаче некорректной строки в 'logo'.

        Проверяет, что API не позволяет создать компанию,
        если поле 'logo' передано не в формате строки Base64.
        """
        company = await company_for_test()
        update_data = {'logo': invalid_value}

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text
        error_detail = response.json()
        assert 'detail' in error_detail, response.text
        assert message == (
            detail := error_detail['detail']
        ), f'Ожидалось:\n{message}\nПолучили\n{detail}'

    @pytest.mark.asyncio
    async def test_patch_company_field_with_leading_or_trailing_spaces(
        self, client: AsyncClient, superuser_token: _token, company_for_test
    ):
        """Тест ошибки 422 при полях с пробелами в начале или в конце."""
        company = await company_for_test()
        update_data = {'name': ' Company'}

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text

    @pytest.mark.asyncio
    async def test_patch_company_invalid_license_id(
        self, client: AsyncClient, superuser_token: _token, company_for_test
    ):
        """Тест ошибки 400 при несуществующем 'license_id'."""
        company = await company_for_test()
        update_data = {'license_id': 99999}

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text

    @pytest.mark.asyncio
    async def test_patch_company_only_license_id(
        self, client: AsyncClient, superuser_token: _token, company_for_test
    ):
        """Тест ошибки 422 при передаче только 'license_id' без 'start_license_time'."""
        company = await company_for_test()
        update_data = {'license_id': 1}

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text

    @pytest.mark.asyncio
    async def test_patch_company_only_start_license_time(
        self, client: AsyncClient, superuser_token: _token, company_for_test
    ):
        """Тест ошибки 422 при передаче только 'start_license_time' без 'license_id'."""
        company = await company_for_test()
        update_data = {'start_license_time': '2025-02-15T07:57:45.058Z'}

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, response.text

    @pytest.mark.asyncio
    async def test_patch_company_without_license_and_start_time(
        self, client: AsyncClient, superuser_token: _token, company_for_test
    ):
        """
        Тест успешного обновления компании без 'license_id' и 'start_license_time'.

        Проверяет, что если не переданы 'license_id' и 'start_license_time',
        поле 'end_license_time' остается 'null'.
        """
        company = await company_for_test()

        update_data = {
            'description': 'Обновление без лицензии',
        }

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()

        assert (
            data['end_license_time'] is None
        ), f'Ожидалось null в поле end_license_time, но получено {data["end_license_time"]}'

    @pytest.mark.asyncio
    @pytest.mark.parametrize('license_term_days', [30, 60, 365])
    async def test_patch_company_with_license_and_start_time(
        self,
        client: AsyncClient,
        superuser_token: _token,
        license_for_test,
        company_for_test,
        license_term_days,
    ):
        """
        Тест успешного обновления компании с 'license_id' и 'start_license_time'.

        Проверяет, что 'end_license_time' корректно рассчитывается в зависимости
        от значения 'license_term' лицензии.
        """
        new_license = await license_for_test({'license_term': timedelta(days=license_term_days)})
        company = await company_for_test()

        start_time = datetime.now(timezone.utc).isoformat()
        expected_end_time = (
            datetime.fromisoformat(start_time) + timedelta(days=license_term_days)
        ).isoformat()

        update_data = {'license_id': new_license.id, 'start_license_time': start_time}

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_200_OK, response.text
        data = response.json()

        actual_end_time = datetime.fromisoformat(data['end_license_time']).isoformat()

        assert actual_end_time == expected_end_time, (
            f'Ожидалось значение {expected_end_time} в поле end_license_time, '
            f'но получено {actual_end_time}'
        )


class TestDeleteCompany:
    """Тесты для удаления компании через DELETE запрос."""

    @pytest.mark.asyncio
    async def test_delete_company_success(
        self, client: AsyncClient, superuser_token: _token, company_for_test
    ):
        """
        Тест успешного удаления компании.

        Проверяет, что API корректно удаляет компанию по slug и возвращает статус-код 204.
        """
        company = await company_for_test()

        response = await client.delete(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            headers=superuser_token,
            follow_redirects=False,
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT, response.text

    @pytest.mark.asyncio
    async def test_delete_company_not_found(self, client: AsyncClient, superuser_token: _token):
        """
        Тест ошибки status.HTTP_404_NOT_FOUND при попытке удаления несуществующей компании.

        Проверяет, что API возвращает статус-код 404 и сообщение 'Объект не найден',
        если компания с указанным slug не существует.
        """

        nonexistent_slug = 'nonexistent-slug'
        response = await client.delete(
            f'{URL.COMPANIES_ENDPOINT}{nonexistent_slug}',
            headers=superuser_token,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
        assert (response_json := response.json()['detail']) == (
            f'Не найден объект Company по данному slug: {nonexistent_slug}'
        ), response_json

    @pytest.mark.asyncio
    async def test_delete_company_already_deleted(
        self, client: AsyncClient, superuser_token: _token, company_for_test
    ):
        """
        Тест ошибки status.HTTP_404_NOT_FOUND при повторном удалении одной и той же компании.

        Проверяет, что API возвращает статус-код 404 и сообщение 'Объект не найден',
        если попытаться удалить уже удалённую компанию.
        """
        company = await company_for_test()

        # Первое удаление - успешно
        response = await client.delete(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            headers=superuser_token,
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT, response.text

        # Повторное удаление - должно вернуть status.HTTP_404_NOT_FOUND
        response = await client.delete(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            headers=superuser_token,
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND, response.text
        assert (response_json := response.json()['detail']) == (
            f'Не найден объект Company по данному slug: {company.slug}'
        ), response_json

    @pytest.mark.asyncio
    async def test_delete_company_without_token(self, client: AsyncClient, company_for_test):
        """
        Тест ошибки 401 при удалении компании без токена.

        Проверяет, что API не позволяет удалить компанию без авторизации.
        Убедимся, что ответ содержит сообщение 'Unauthorized' и статус-код 401.
        """
        company = await company_for_test()

        response = await client.delete(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text
        assert response.json()['detail'] == 'Unauthorized'

    @pytest.mark.asyncio
    async def test_delete_company_invalid_token(self, client: AsyncClient, company_for_test):
        """
        Тест ошибки 401 при удалении компании с некорректным токеном.

        Проверяет, что API не позволяет удалить компанию с недействительным токеном.
        Убедимся, что ответ содержит сообщение 'Unauthorized' и статус-код 401.
        """
        company = await company_for_test()

        invalid_token = {'Authorization': 'Bearer invalid_token_123'}

        response = await client.delete(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            headers=invalid_token,
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED, response.text
        assert response.json()['detail'] == 'Unauthorized'
