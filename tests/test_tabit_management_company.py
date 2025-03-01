import random
import string
from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient

from tests.constants import URL


def generate_company_data(all_fields=False, license_id=None):
    """Генерирует реалистичные данные для создания компании."""

    def random_string(length=10):
        """Генерирует случайную строку указанной длины."""
        return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

    data = {'name': f'Компания {random_string(5)}'}

    if all_fields:
        data.update(
            {
                'description': f'Описание компании {random_string(15)}',
                'logo': f'https://example.com/logo_{random_string(6)}.png',
                'license_id': license_id,
                'start_license_time': '2025-02-15T07:57:45.058Z',
                'slug': f'company-{random_string(8).lower()}',
            }
        )

    return data


class TestCreateCompany:
    @pytest.mark.asyncio
    async def test_create_company_required_fields(
        self, client: AsyncClient, test_admin_token: str
    ):
        """
        Тест успешного создания компании с обязательными полями.

        Проверяет, что API корректно создаёт компанию при передаче только обязательных данных.
        Убедимся, что ответ содержит правильные значения и API возвращает статус-код 201.
        """
        payload = generate_company_data()

        response = await client.post(
            URL.COMPANIES_ENDPOINT,
            json=payload,
            headers=test_admin_token,
        )

        assert response.status_code == 201, response.text
        data = response.json()
        assert data['name'] == payload['name']
        assert 'slug' in data
        assert 'is_active' in data
        assert 'end_license_time' in data
        assert 'max_admins_count' in data
        assert 'max_employees_count' in data

    @pytest.mark.asyncio
    async def test_create_company_all_fields(
        self, client: AsyncClient, test_admin_token: str, license_for_test
    ):
        """
        Тест успешного создания компании со всеми полями.

        Проверяет, что API корректно создаёт компанию при передаче всех полей.
        Убедимся, что ответ содержит правильные значения и API возвращает статус-код 201.
        """
        new_license = await license_for_test()
        payload = generate_company_data(all_fields=True, license_id=new_license.id)

        response = await client.post(
            URL.COMPANIES_ENDPOINT,
            json=payload,
            headers=test_admin_token,
        )

        assert response.status_code == 201, response.text
        data = response.json()
        assert data['name'] == payload['name']
        assert data['slug'] == payload['slug']
        assert data['description'] == payload['description']
        assert data['logo'] == payload['logo']

    @pytest.mark.asyncio
    async def test_create_company_duplicate_slug(
        self, client: AsyncClient, test_admin_token: str, license_for_test
    ):
        """
        Тест ошибки 400 при создании компании с уже существующим slug.

        Проверяет, что API не позволяет создать компанию с дублирующимся slug.
        Убедимся, что ответ содержит правильное сообщение об ошибке и статус-код 400.
        """
        new_license = await license_for_test()
        payload = generate_company_data(all_fields=True, license_id=new_license.id)

        jwt_token = test_admin_token

        response = await client.post(
            URL.COMPANIES_ENDPOINT,
            json=payload,
            headers=jwt_token,
        )
        assert response.status_code == 201, response.text

        response = await client.post(
            URL.COMPANIES_ENDPOINT,
            json=payload,
            headers=jwt_token,
        )
        assert response.status_code == 400, response.text
        assert (
            response.json()['detail']
            == f"Компания с таким slug '{payload['slug']}' уже существует."
        )

    @pytest.mark.asyncio
    async def test_create_company_missing_name(
        self, client: AsyncClient, test_admin_token: str, license_for_test
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
            headers=test_admin_token,
        )

        assert response.status_code == 422, response.text
        error_detail = response.json()['detail']
        assert any(
            error['loc'] == ['body', 'name'] and error['msg'] == 'Field required'
            for error in error_detail
        ), response.text

    @pytest.mark.asyncio
    async def test_create_company_name_too_short(
        self, client: AsyncClient, test_admin_token: str, license_for_test
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
            headers=test_admin_token,
        )

        assert response.status_code == 422, response.text
        error_detail = response.json()['detail']
        assert any(
            error['loc'] == ['body', 'name']
            and error['msg'] == 'String should have at least 2 characters'
            for error in error_detail
        ), response.text

    @pytest.mark.asyncio
    async def test_create_company_name_too_long(
        self, client: AsyncClient, test_admin_token: str, license_for_test
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
            headers=test_admin_token,
        )

        assert response.status_code == 422, response.text
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

        assert response.status_code == 401, response.text
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

        assert response.status_code == 401, response.text
        assert response.json()['detail'] == 'Unauthorized'

    @pytest.mark.asyncio
    async def test_create_company_invalid_description_type(
        self, client: AsyncClient, test_admin_token: str, license_for_test
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
            headers=test_admin_token,
        )

        assert response.status_code == 422, response.text
        assert any(
            error['loc'] == ['body', 'description']
            and error['msg'] == 'Input should be a valid string'
            for error in response.json()['detail']
        ), response.text

    @pytest.mark.asyncio
    async def test_create_company_invalid_logo_type(
        self, client: AsyncClient, test_admin_token: str, license_for_test
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
            headers=test_admin_token,
        )

        assert response.status_code == 422, response.text
        assert any(
            error['loc'] == ['body', 'logo'] and error['msg'] == 'Input should be a valid string'
            for error in response.json()['detail']
        ), response.text

    @pytest.mark.asyncio
    async def test_create_company_invalid_license_id_type(
        self, client: AsyncClient, test_admin_token: str, license_for_test
    ):
        """
        Тест ошибки 422 при передаче строки в поле 'license_id'.

        Проверяет, что API не позволяет создать компанию,
        если поле 'license_id' передано не в виде числа.
        """
        new_license = await license_for_test()
        payload = generate_company_data(all_fields=True, license_id=new_license.id)
        payload['license_id'] = 'invalid_id'

        response = await client.post(
            URL.COMPANIES_ENDPOINT,
            json=payload,
            headers=test_admin_token,
        )

        assert response.status_code == 422, response.text
        assert any(
            error['loc'] == ['body', 'license_id']
            and error['msg']
            == 'Input should be a valid integer, unable to parse string as an integer'
            for error in response.json()['detail']
        ), response.text

    @pytest.mark.asyncio
    async def test_create_company_invalid_start_license_time_type(
        self, client: AsyncClient, test_admin_token: str, license_for_test
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
            headers=test_admin_token,
        )

        assert response.status_code == 422, response.text
        assert any(
            error['loc'] == ['body', 'start_license_time']
            and error['msg']
            == 'Input should be a valid datetime or date, invalid character in year'
            for error in response.json()['detail']
        ), response.text

    @pytest.mark.asyncio
    async def test_create_company_description_too_short(
        self, client: AsyncClient, test_admin_token: str, license_for_test
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
            headers=test_admin_token,
        )

        assert response.status_code == 422, response.text
        error_detail = response.json()['detail']
        assert any(
            error['loc'] == ['body', 'description']
            and error['msg'] == 'String should have at least 2 characters'
            for error in error_detail
        ), response.text

    @pytest.mark.asyncio
    async def test_create_company_description_too_long(
        self, client: AsyncClient, test_admin_token: str, license_for_test
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
            headers=test_admin_token,
        )

        assert response.status_code == 422, response.text
        error_detail = response.json()['detail']
        assert any(
            error['loc'] == ['body', 'description']
            and error['msg'] == 'String should have at most 255 characters'
            for error in error_detail
        ), response.text

    @pytest.mark.asyncio
    async def test_generate_unique_slug(self, client: AsyncClient, test_admin_token: str):
        """
        Тест успешной генерации уникального slug для компаний с одинаковыми названиями.

        Проверяет, что при создании двух компаний с одинаковым полем `name`
        их slug-значения будут разными. Убедимся, что API корректно обрабатывает
        дублирование названия и добавляет уникальный идентификатор в slug второй компании.
        """
        company_name = 'Тестовая Компания'

        jwt_token = test_admin_token

        payload_1 = {'name': company_name}
        response_1 = await client.post(
            URL.COMPANIES_ENDPOINT,
            json=payload_1,
            headers=jwt_token,
        )
        assert response_1.status_code == 201
        first_company_slug = response_1.json()['slug']

        payload_2 = {'name': company_name}
        response_2 = await client.post(
            URL.COMPANIES_ENDPOINT,
            json=payload_2,
            headers=jwt_token,
        )
        assert response_2.status_code == 201
        second_company_slug = response_2.json()['slug']

        assert first_company_slug != second_company_slug, 'Слаг должен быть уникальным'
        assert second_company_slug.startswith(first_company_slug.split('-')[0]), (
            'Слаг должен базироваться на названии'
        )

    @pytest.mark.asyncio
    async def test_create_company_invalid_logo_url(
        self, client: AsyncClient, test_admin_token: str, license_for_test
    ):
        """
        Тест ошибки 422 при передаче некорректного URL в поле 'logo'.

        Проверяет, что API не позволяет создать компанию,
        если поле 'logo' передано не в формате корректного URL.
        """
        new_license = await license_for_test()
        payload = generate_company_data(all_fields=True, license_id=new_license.id)
        payload['logo'] = 'string'

        response = await client.post(
            URL.COMPANIES_ENDPOINT,
            json=payload,
            headers=test_admin_token,
        )

        assert response.status_code == 422, response.text
        error_detail = response.json()['detail']
        assert any(
            error['loc'] == ['body', 'logo']
            and error['msg'] == 'Value error, Логотип должен быть валидным URL-адресом.'
            for error in error_detail
        ), response.text

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
        test_admin_token: str,
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
            headers=test_admin_token,
        )

        assert response.status_code == 422, response.text
        error_detail = response.json()['detail']
        assert any(
            error['loc'] == ['body', field]
            and error['msg'] == 'Value error, Поле не может начинаться или заканчиваться пробелом.'
            for error in error_detail
        ), response.text

    @pytest.mark.asyncio
    async def test_create_company_invalid_license_id(
        self,
        client: AsyncClient,
        test_admin_token: str,
    ):
        """
        Тест ошибки 400 при создании компании с несуществующим 'license_id'.

        Проверяет, что API не позволяет создать компанию, если передана несуществующая лицензия.
        Убедимся, что ответ содержит правильное сообщение об ошибке и статус-код 400.
        """
        payload = generate_company_data(all_fields=True, license_id=99999)

        response = await client.post(
            URL.COMPANIES_ENDPOINT,
            json=payload,
            headers=test_admin_token,
        )

        assert response.status_code == 400, response.text
        assert response.json() == {'detail': 'Лицензия с id 99999 не найдена.'}

    @pytest.mark.asyncio
    async def test_create_company_without_license_and_start_time(
        self, client: AsyncClient, test_admin_token: str
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
            headers=test_admin_token,
        )

        assert response.status_code == 201, response.text
        data = response.json()
        assert data['end_license_time'] is None

    @pytest.mark.asyncio
    @pytest.mark.parametrize('license_term_days', [30, 60, 365])
    async def test_create_company_with_license_and_start_time(
        self, client: AsyncClient, test_admin_token: str, license_for_test, license_term_days
    ):
        """
        Тест вычисления 'end_license_time' при наличии 'license_id' и 'start_license_time'.

        Проверяет, что 'end_license_time' корректно рассчитывается в зависимости
        от значения 'license_term' лицензии.
        """
        new_license = await license_for_test({'license_term': timedelta(days=license_term_days)})

        start_time = datetime.now().isoformat()
        expected_end_time = (
            datetime.fromisoformat(start_time) + timedelta(days=license_term_days)
        ).isoformat()

        payload = {
            'name': 'Тестовая компания',
            'license_id': new_license.id,
            'start_license_time': start_time,
        }

        response = await client.post(
            URL.COMPANIES_ENDPOINT,
            json=payload,
            headers=test_admin_token,
        )

        assert response.status_code == 201, response.text
        data = response.json()

        actual_end_time = (
            datetime.fromisoformat(data['end_license_time']).replace(tzinfo=None).isoformat()
        )

        assert actual_end_time == expected_end_time, (
            f'Ожидалось {expected_end_time}, но получено {actual_end_time}'
        )

    @pytest.mark.asyncio
    async def test_create_company_only_license_id(
        self, client: AsyncClient, test_admin_token: str, license_for_test
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
            headers=test_admin_token,
        )

        assert response.status_code == 422, response.text
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
        self, client: AsyncClient, test_admin_token: str
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
            headers=test_admin_token,
        )

        assert response.status_code == 422, response.text
        error_detail = response.json()['detail']
        assert any(
            error['msg']
            == (
                'Value error, Поля начала действия лицензии и '
                'тип лицензии заполняются одновременно.'
            )
            for error in error_detail
        ), response.text


class TestGetCompany:
    """Тесты получения списка компаний с сортировкой."""

    @pytest.mark.asyncio
    async def test_get_companies_success(
        self,
        client: AsyncClient,
        test_admin_token: str,
        company_for_test,
    ):
        """
        Тест успешного получения списка компаний.

        Проверяет, что API возвращает статус-код 200 и список компаний.
        Убедимся, что данные содержат ожидаемые поля.
        """
        await company_for_test({'name': 'Компания 1'})
        await company_for_test({'name': 'Компания 2'})

        response = await client.get(
            URL.COMPANIES_ENDPOINT,
            headers=test_admin_token,
        )

        assert response.status_code == 200, response.text
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
            assert expected_fields.issubset(company.keys()), (
                f'Компания должна содержать поля: {expected_fields}'
            )

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
        self, client: AsyncClient, test_admin_token: str, company_for_test, ordering, expected_sort
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
            headers=test_admin_token,
        )

        assert response.status_code == 200, response.text
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

        assert response.status_code == 401, response.text
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

        assert response.status_code == 401, response.text
        assert response.json()['detail'] == 'Unauthorized'

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'update_data, expected_field, expected_value',
        [
            ({'description': 'Новое описание'}, 'description', 'Новое описание'),
            (
                {'logo': 'https://example.com/new_logo.png'},
                'logo',
                'https://example.com/new_logo.png',
            ),
            ({'name': 'Новое имя'}, 'name', 'Новое имя'),
            ({'license_id': 1, 'start_license_time': datetime.now().isoformat()}, 'license_id', 1),
        ],
    )
    async def test_patch_company_single_field(
        self,
        client: AsyncClient,
        test_admin_token: str,
        company_for_test,
        update_data,
        expected_field,
        expected_value,
    ):
        """
        Тест успешного обновления одного поля компании через PATCH запрос.

        Проверяет, что API корректно обновляет указанное поле компании и возвращает
        ожидаемое значение. Используется параметризация для проверки разных полей.
        """
        company = await company_for_test({'name': 'Компания 1', 'slug': 'slug1'})

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
            headers=test_admin_token,
        )

        assert response.status_code == 200, response.text
        data = response.json()
        assert data[expected_field] == expected_value, (
            f'Ожидалось значение {expected_value} в поле {expected_field}, '
            f'но получено {data[expected_field]}'
        )

    @pytest.mark.asyncio
    async def test_patch_company_all_fields(
        self,
        client: AsyncClient,
        test_admin_token: str,
        license_for_test,
        company_for_test,
    ):
        """
        Тест успешного обновления всех полей компании через PATCH запрос.

        Проверяет, что API корректно обновляет все поля компании и возвращает ожидаемые значения.
        """
        new_license = await license_for_test()
        company = await company_for_test({'name': 'Компания 1', 'slug': 'slug1'})

        update_data = {
            'description': 'Обновленное описание',
            'logo': 'https://example.com/updated_logo.png',
            'name': 'Обновленное имя',
            'license_id': new_license.id,
            'start_license_time': datetime.now().isoformat(),
        }

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
            headers=test_admin_token,
        )

        assert response.status_code == 200, response.text
        data = response.json()

        for key, value in update_data.items():
            if 'time' in key and value:
                actual_time = datetime.fromisoformat(data[key]).replace(tzinfo=None).isoformat()
                assert actual_time == value, (
                    f'Ожидалось значение {value} в поле {key}, но получено {actual_time}'
                )
            else:
                assert data[key] == value, (
                    f'Ожидалось значение {value} в поле {key}, но получено {data[key]}'
                )

    @pytest.mark.asyncio
    async def test_patch_company_name_too_short(
        self, client: AsyncClient, test_admin_token: str, company_for_test
    ):
        """
        Тест ошибки 422 при обновлении компании с name менее 2 символов.

        Проверяет, что API не позволяет обновить компанию, если поле name содержит менее 2 символов
        Убедимся, что ответ содержит правильное сообщение об ошибке и статус-код 422.
        """
        company = await company_for_test({'name': 'Компания 1', 'slug': 'slug1'})

        update_data = {'name': 'A'}

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
            headers=test_admin_token,
        )

        assert response.status_code == 422, response.text
        error_detail = response.json()['detail']
        assert any(
            error['loc'] == ['body', 'name']
            and error['msg'] == 'String should have at least 2 characters'
            for error in error_detail
        ), response.text

    @pytest.mark.asyncio
    async def test_patch_company_name_too_long(
        self, client: AsyncClient, test_admin_token: str, company_for_test
    ):
        """
        Тест ошибки 422 при обновлении компании с name более 255 символов.

        Проверяет, что API не позволяет обновить компанию,
        если поле name содержит более 255 символов.
        Убедимся, что ответ содержит правильное сообщение об ошибке и статус-код 422.
        """
        company = await company_for_test({'name': 'Компания 1', 'slug': 'slug1'})

        update_data = {'name': 's' * 256}

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
            headers=test_admin_token,
        )

        assert response.status_code == 422, response.text
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
        company = await company_for_test({'name': 'Компания 1', 'slug': 'slug1'})
        update_data = {'name': 'Новое имя'}

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
        )

        assert response.status_code == 401, response.text
        assert response.json()['detail'] == 'Unauthorized'

    @pytest.mark.asyncio
    async def test_patch_company_invalid_token(self, client: AsyncClient, company_for_test):
        """
        Тест ошибки 401 при обновлении компании с некорректным токеном.

        Проверяет, что API не позволяет обновить компанию с недействительным токеном.
        Убедимся, что ответ содержит сообщение 'Unauthorized' и статус-код 401.
        """
        company = await company_for_test({'name': 'Компания 1', 'slug': 'slug1'})

        update_data = {'name': 'Новое имя'}

        invalid_token = {'Authorization': 'Bearer invalid_token_123'}

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
            headers=invalid_token,
        )

        assert response.status_code == 401, response.text
        assert response.json()['detail'] == 'Unauthorized'


class TestPatchCompanyValidation:
    """Тесты валидации данных при обновлении компании через PATCH запрос."""

    @pytest.mark.asyncio
    async def test_patch_company_invalid_description_type(
        self, client: AsyncClient, test_admin_token: str, company_for_test
    ):
        """Тест ошибки 422 при передаче числа в поле 'description'."""
        company = await company_for_test({'name': 'Компания 1', 'slug': 'slug1'})
        update_data = {'description': 1}

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
            headers=test_admin_token,
        )

        assert response.status_code == 422, response.text

    @pytest.mark.asyncio
    async def test_patch_company_invalid_logo_type(
        self, client: AsyncClient, test_admin_token: str, company_for_test
    ):
        """Тест ошибки 422 при передаче массива в поле 'logo'."""
        company = await company_for_test({'name': 'Компания 1', 'slug': 'slug1'})
        update_data = {'logo': ['invalid_logo_url']}

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
            headers=test_admin_token,
        )

        assert response.status_code == 422, response.text

    @pytest.mark.asyncio
    async def test_patch_company_invalid_license_id_type(
        self, client: AsyncClient, test_admin_token: str, company_for_test
    ):
        """Тест ошибки 422 при передаче строки в поле 'license_id'."""
        company = await company_for_test({'name': 'Компания 1', 'slug': 'slug1'})
        update_data = {'license_id': 'invalid_id'}

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
            headers=test_admin_token,
        )

        assert response.status_code == 422, response.text

    @pytest.mark.asyncio
    async def test_patch_company_invalid_start_license_time_type(
        self, client: AsyncClient, test_admin_token: str, company_for_test
    ):
        """Тест ошибки 422 при некорректном формате 'start_license_time'."""
        company = await company_for_test({'name': 'Компания 1', 'slug': 'slug1'})
        update_data = {'start_license_time': 'invalid_date'}

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
            headers=test_admin_token,
        )

        assert response.status_code == 422, response.text

    @pytest.mark.asyncio
    async def test_patch_company_description_too_short(
        self, client: AsyncClient, test_admin_token: str, company_for_test
    ):
        """Тест ошибки 422 при 'description' менее 2 символов."""
        company = await company_for_test({'name': 'Компания 1', 'slug': 'slug1'})
        update_data = {'description': 'A'}

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
            headers=test_admin_token,
        )

        assert response.status_code == 422, response.text

    @pytest.mark.asyncio
    async def test_patch_company_description_too_long(
        self, client: AsyncClient, test_admin_token: str, company_for_test
    ):
        """Тест ошибки 422 при 'description' более 255 символов."""
        company = await company_for_test({'name': 'Компания 1', 'slug': 'slug1'})
        update_data = {'description': 'A' * 256}

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
            headers=test_admin_token,
        )

        assert response.status_code == 422, response.text

    @pytest.mark.asyncio
    async def test_patch_company_invalid_logo_url(
        self, client: AsyncClient, test_admin_token: str, company_for_test
    ):
        """Тест ошибки 422 при некорректном URL в поле 'logo'."""
        company = await company_for_test({'name': 'Компания 1', 'slug': 'slug1'})
        update_data = {'logo': 'invalid_url'}

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
            headers=test_admin_token,
        )

        assert response.status_code == 422, response.text

    @pytest.mark.asyncio
    async def test_patch_company_field_with_leading_or_trailing_spaces(
        self, client: AsyncClient, test_admin_token: str, company_for_test
    ):
        """Тест ошибки 422 при полях с пробелами в начале или в конце."""
        company = await company_for_test({'name': 'Компания 1', 'slug': 'slug1'})
        update_data = {'name': ' Company'}

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
            headers=test_admin_token,
        )

        assert response.status_code == 422, response.text

    @pytest.mark.asyncio
    async def test_patch_company_invalid_license_id(
        self, client: AsyncClient, test_admin_token: str, company_for_test
    ):
        """Тест ошибки 400 при несуществующем 'license_id'."""
        company = await company_for_test({'name': 'Компания 1', 'slug': 'slug1'})
        update_data = {'license_id': 99999}

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
            headers=test_admin_token,
        )

        assert response.status_code == 422, response.text

    @pytest.mark.asyncio
    async def test_patch_company_only_license_id(
        self, client: AsyncClient, test_admin_token: str, company_for_test
    ):
        """Тест ошибки 422 при передаче только 'license_id' без 'start_license_time'."""
        company = await company_for_test({'name': 'Компания 1', 'slug': 'slug1'})
        update_data = {'license_id': 1}

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
            headers=test_admin_token,
        )

        assert response.status_code == 422, response.text

    @pytest.mark.asyncio
    async def test_patch_company_only_start_license_time(
        self, client: AsyncClient, test_admin_token: str, company_for_test
    ):
        """Тест ошибки 422 при передаче только 'start_license_time' без 'license_id'."""
        company = await company_for_test({'name': 'Компания 1', 'slug': 'slug1'})
        update_data = {'start_license_time': '2025-02-15T07:57:45.058Z'}

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
            headers=test_admin_token,
        )

        assert response.status_code == 422, response.text

    @pytest.mark.asyncio
    async def test_patch_company_without_license_and_start_time(
        self, client: AsyncClient, test_admin_token: str, company_for_test
    ):
        """
        Тест успешного обновления компании без 'license_id' и 'start_license_time'.

        Проверяет, что если не переданы 'license_id' и 'start_license_time',
        поле 'end_license_time' остается 'null'.
        """
        company = await company_for_test({'name': 'Компания 1', 'slug': 'slug1'})

        update_data = {
            'description': 'Обновление без лицензии',
        }

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
            headers=test_admin_token,
        )

        assert response.status_code == 200, response.text
        data = response.json()

        assert data['end_license_time'] is None, (
            f'Ожидалось null в поле end_license_time, но получено {data["end_license_time"]}'
        )

    @pytest.mark.asyncio
    @pytest.mark.parametrize('license_term_days', [30, 60, 365])
    async def test_patch_company_with_license_and_start_time(
        self,
        client: AsyncClient,
        test_admin_token: str,
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
        company = await company_for_test({'name': 'Компания 1', 'slug': 'slug1'})

        start_time = datetime.now().isoformat()
        expected_end_time = (
            (datetime.fromisoformat(start_time) + timedelta(days=license_term_days))
            .replace(tzinfo=None)
            .isoformat()
        )

        update_data = {'license_id': new_license.id, 'start_license_time': start_time}

        response = await client.patch(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            json=update_data,
            headers=test_admin_token,
        )

        assert response.status_code == 200, response.text
        data = response.json()

        actual_end_time = (
            datetime.fromisoformat(data['end_license_time']).replace(tzinfo=None).isoformat()
        )

        assert actual_end_time == expected_end_time, (
            f'Ожидалось значение {expected_end_time} в поле end_license_time, '
            f'но получено {actual_end_time}'
        )


class TestDeleteCompany:
    """Тесты для удаления компании через DELETE запрос."""

    @pytest.mark.asyncio
    async def test_delete_company_success(
        self, client: AsyncClient, test_admin_token: str, company_for_test
    ):
        """
        Тест успешного удаления компании.

        Проверяет, что API корректно удаляет компанию по slug и возвращает статус-код 204.
        """
        company = await company_for_test({'name': 'Компания 1', 'slug': 'slug1'})

        response = await client.delete(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            headers=test_admin_token,
            follow_redirects=False,
        )

        assert response.status_code == 204, response.text

    @pytest.mark.asyncio
    async def test_delete_company_not_found(self, client: AsyncClient, test_admin_token: str):
        """
        Тест ошибки 404 при попытке удаления несуществующей компании.

        Проверяет, что API возвращает статус-код 404 и сообщение 'Объект не найден',
        если компания с указанным slug не существует.
        """

        response = await client.delete(
            f'{URL.COMPANIES_ENDPOINT}nonexistent-slug',
            headers=test_admin_token,
        )

        assert response.status_code == 404, response.text
        assert response.json()['detail'] == 'Объект не найден'

    @pytest.mark.asyncio
    async def test_delete_company_already_deleted(
        self, client: AsyncClient, test_admin_token: str, company_for_test
    ):
        """
        Тест ошибки 404 при повторном удалении одной и той же компании.

        Проверяет, что API возвращает статус-код 404 и сообщение 'Объект не найден',
        если попытаться удалить уже удалённую компанию.
        """
        company = await company_for_test({'name': 'Компания 1', 'slug': 'slug1'})

        # Первое удаление - успешно
        response = await client.delete(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            headers=test_admin_token,
        )
        assert response.status_code == 204, response.text

        # Повторное удаление - должно вернуть 404
        response = await client.delete(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            headers=test_admin_token,
        )
        assert response.status_code == 404, response.text
        assert response.json()['detail'] == 'Объект не найден'

    @pytest.mark.asyncio
    async def test_delete_company_without_token(self, client: AsyncClient, company_for_test):
        """
        Тест ошибки 401 при удалении компании без токена.

        Проверяет, что API не позволяет удалить компанию без авторизации.
        Убедимся, что ответ содержит сообщение 'Unauthorized' и статус-код 401.
        """
        company = await company_for_test({'name': 'Компания 1', 'slug': 'slug1'})

        response = await client.delete(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
        )

        assert response.status_code == 401, response.text
        assert response.json()['detail'] == 'Unauthorized'

    @pytest.mark.asyncio
    async def test_delete_company_invalid_token(self, client: AsyncClient, company_for_test):
        """
        Тест ошибки 401 при удалении компании с некорректным токеном.

        Проверяет, что API не позволяет удалить компанию с недействительным токеном.
        Убедимся, что ответ содержит сообщение 'Unauthorized' и статус-код 401.
        """
        company = await company_for_test({'name': 'Компания 1', 'slug': 'slug1'})

        invalid_token = {'Authorization': 'Bearer invalid_token_123'}

        response = await client.delete(
            f'{URL.COMPANIES_ENDPOINT}{company.slug}',
            headers=invalid_token,
        )

        assert response.status_code == 401, response.text
        assert response.json()['detail'] == 'Unauthorized'
