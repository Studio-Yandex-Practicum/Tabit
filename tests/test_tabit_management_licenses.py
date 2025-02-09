import uuid

import pytest
from httpx import AsyncClient


def generate_license_data():
    """Генерирует уникальное имя лицензии для тестов."""
    return {
        'name': f'Test License {uuid.uuid4().hex[:8]}',
        'license_term': 'P1Y1M1D',
        'max_admins_count': 10,
        'max_employees_count': 50,
    }


class TestCreateLicense:
    @pytest.mark.asyncio
    async def test_create_license(self, client: AsyncClient):
        """Тест успешного создания лицензии.

        Проверяет, что API корректно создаёт лицензию при передаче валидных данных.
        Убедимся, что ответ содержит правильные значения и API возвращает статус-код 201.
        """
        license_data = generate_license_data()
        response = await client.post('/api/v1/admin/licenses/', json=license_data)

        assert response.status_code == 201
        result = response.json()

        assert result['name'] == license_data['name']
        assert result['license_term'] == 'P1Y31D'
        assert result['max_admins_count'] == license_data['max_admins_count']
        assert result['max_employees_count'] == license_data['max_employees_count']

    @pytest.mark.asyncio
    async def test_create_license_with_duplicate_name(self, client: AsyncClient, test_license):
        """Тест создания лицензии с дублирующимся `name`.

        Проверяет, что API отклоняет запрос с дубликатом имени и возвращает ошибку 400.
        """
        new_license = await test_license()

        duplicate_data = generate_license_data()
        duplicate_data['name'] = new_license.name

        response = await client.post('/api/v1/admin/licenses/', json=duplicate_data)

        assert response.status_code == 400
        result = response.json()

        assert result['detail'] == f"Лицензия с именем '{new_license.name}' уже существует."

    @pytest.mark.asyncio
    async def test_create_license_missing_name(self, client: AsyncClient):
        """Тест создания лицензии без поля `name`.

        Проверяет, что API отклоняет запрос и возвращает ошибку 422,
        если обязательное поле `name` отсутствует в теле запроса.
        """
        data = generate_license_data()
        del data['name']

        response = await client.post('/api/v1/admin/licenses/', json=data)

        assert response.status_code == 422
        result = response.json()

        assert result['detail'][0]['loc'] == ['body', 'name']
        assert result['detail'][0]['msg'] == 'Field required'

    @pytest.mark.asyncio
    async def test_create_license_with_invalid_name_type(self, client: AsyncClient):
        """Тест создания лицензии с некорректным типом поля name

        Проверяет, что при передаче числа в поле `name` API возвращает ошибку валидации
        со статус-кодом 422 и корректным сообщением об ошибке.
        """
        data = generate_license_data()
        data['name'] = 11

        response = await client.post('/api/v1/admin/licenses/', json=data)

        assert response.status_code == 422
        result = response.json()

        assert result['detail'][0]['loc'] == ['body', 'name']
        assert result['detail'][0]['msg'] == 'Input should be a valid string'

    @pytest.mark.asyncio
    async def test_create_license_with_empty_name(self, client: AsyncClient):
        """Тест создания лицензии с пустым значением поля name

        Проверяет, что при передаче пустой строки в поле `name` API возвращает ошибку валидации
        со статус-кодом 422 и корректным сообщением об ошибке.
        """
        data = generate_license_data()
        data['name'] = ''

        response = await client.post('/api/v1/admin/licenses/', json=data)

        assert response.status_code == 422
        result = response.json()

        assert result['detail'][0]['loc'] == ['body', 'name']
        assert result['detail'][0]['msg'] == 'String should have at least 2 characters'

    @pytest.mark.asyncio
    async def test_create_license_with_long_name(self, client: AsyncClient):
        """Тест создания лицензии с полем name, содержащим 101 символ

        Проверяет, что API отклоняет запрос со слишком длинным именем и возвращает ошибку валидации
        со статус-кодом 422 и корректным сообщением.
        """
        data = generate_license_data()
        data['name'] = 'A' * 101

        response = await client.post('/api/v1/admin/licenses/', json=data)

        assert response.status_code == 422
        result = response.json()

        assert result['detail'][0]['loc'] == ['body', 'name']
        assert result['detail'][0]['msg'] == 'String should have at most 100 characters'

    @pytest.mark.asyncio
    async def test_create_license_with_name_with_trailing_spaces(self, client: AsyncClient):
        """Тест создания лицензии с полем name, содержащим пробелы в начале и конце.

        Проверяет, что API отклоняет запрос и возвращает ошибку валидации
        со статус-кодом 422, если name содержит пробелы в начале или в конце.
        """
        data = generate_license_data()
        data['name'] = ' пробелы '

        response = await client.post('/api/v1/admin/licenses/', json=data)

        assert response.status_code == 422
        result = response.json()

        assert result['detail'][0]['loc'] == ['body', 'name']
        assert result['detail'][0]['msg'] == (
            'Value error, Поле не может начинаться или заканчиваться пробелом.'
        )

    @pytest.mark.asyncio
    async def test_create_license_with_invalid_license_term_format(self, client: AsyncClient):
        """Тест создания лицензии с некорректным форматом license_term.

        Проверяет, что API отклоняет запрос со статус-кодом 422, если `license_term`
        передан в неверном формате, например '1Y1S'.
        """
        data = generate_license_data()
        data['license_term'] = '1Y1S'

        response = await client.post('/api/v1/admin/licenses/', json=data)

        assert response.status_code == 422
        result = response.json()

        assert result['detail'][0]['loc'] == ['body', 'license_term']
        assert result['detail'][0]['msg'] == (
            'Value error, Поле не может быть пустым. Может быть целым числом, или строкой, '
            'обозначающее целое число, или строкой формата "P1D", "P1Y", "P1Y1D".'
        )

    @pytest.mark.asyncio
    async def test_create_license_with_numeric_license_term(self, client: AsyncClient):
        """Тест создания лицензии с `license_term` в виде числа (360 дней).

        Проверяет, что API корректно рассчитывает `license_term` и возвращает его
        в формате ISO ('P360D').
        """
        data = generate_license_data()
        data['license_term'] = 360

        response = await client.post('/api/v1/admin/licenses/', json=data)

        assert response.status_code == 201
        result = response.json()

        assert 'license_term' in result
        assert result['license_term'] == 'P360D'

    @pytest.mark.asyncio
    async def test_create_license_without_license_term(self, client: AsyncClient):
        """Тест создания лицензии без поля `license_term`.

        Проверяет, что API отклоняет запрос и возвращает ошибку 422,
        если отсутствует `license_term`.
        """
        data = generate_license_data()
        del data['license_term']

        response = await client.post('/api/v1/admin/licenses/', json=data)

        assert response.status_code == 422
        result = response.json()

        assert result['detail'][0]['loc'] == ['body', 'license_term']
        assert result['detail'][0]['msg'] == 'Field required'

    @pytest.mark.asyncio
    async def test_create_license_with_negative_license_term(self, client: AsyncClient):
        """Тест создания лицензии с отрицательным `license_term`.

        Проверяет, что API отклоняет запрос со статус-кодом 422, если `license_term`
        меньше 1 дня.
        """
        data = generate_license_data()
        data['license_term'] = -11

        response = await client.post('/api/v1/admin/licenses/', json=data)

        assert response.status_code == 422
        result = response.json()

        assert result['detail'][0]['loc'] == ['body', 'license_term']
        assert result['detail'][0]['msg'] == 'Input should be greater than or equal to 1 day'

    @pytest.mark.asyncio
    async def test_create_license_with_zero_license_term(self, client: AsyncClient):
        """Тест создания лицензии с `license_term` = 0.

        Проверяет, что API отклоняет запрос со статус-кодом 422, если `license_term` = 0.
        """
        data = generate_license_data()
        data['license_term'] = 0

        response = await client.post('/api/v1/admin/licenses/', json=data)

        assert response.status_code == 422
        result = response.json()

        assert result['detail'][0]['loc'] == ['body', 'license_term']
        assert result['detail'][0]['msg'] == 'Input should be greater than or equal to 1 day'

    @pytest.mark.asyncio
    async def test_create_license_with_zero_max_admins_count(self, client: AsyncClient):
        """Тест создания лицензии с `max_admins_count` = 0.

        Проверяет, что API отклоняет запрос со статус-кодом 422,
        так как `max_admins_count` должен быть больше 0.
        """
        data = generate_license_data()
        data['max_admins_count'] = 0

        response = await client.post('/api/v1/admin/licenses/', json=data)

        assert response.status_code == 422
        result = response.json()

        assert result['detail'][0]['loc'] == ['body', 'max_admins_count']
        assert result['detail'][0]['msg'] == 'Input should be greater than 0'

    @pytest.mark.asyncio
    async def test_create_license_without_max_admins_count(self, client: AsyncClient):
        """Тест создания лицензии без `max_admins_count`.

        Проверяет, что API отклоняет запрос и возвращает ошибку 422,
        если отсутствует `max_admins_count`.
        """
        data = generate_license_data()
        del data['max_admins_count']

        response = await client.post('/api/v1/admin/licenses/', json=data)

        assert response.status_code == 422
        result = response.json()

        assert result['detail'][0]['loc'] == ['body', 'max_admins_count']
        assert result['detail'][0]['msg'] == 'Field required'

    @pytest.mark.asyncio
    async def test_create_license_with_invalid_max_admins_count(self, client: AsyncClient):
        """Тест создания лицензии с `max_admins_count`, переданным как строка.

        Проверяет, что API отклоняет запрос и возвращает ошибку 422,
        так как `max_admins_count` должен быть целым числом.
        """
        data = generate_license_data()
        data['max_admins_count'] = 'true'

        response = await client.post('/api/v1/admin/licenses/', json=data)

        assert response.status_code == 422
        result = response.json()

        assert result['detail'][0]['loc'] == ['body', 'max_admins_count']
        assert result['detail'][0]['msg'] == (
            'Input should be a valid integer, unable to parse string as an integer'
        )

    @pytest.mark.asyncio
    async def test_create_license_with_zero_max_employees_count(self, client: AsyncClient):
        """Тест создания лицензии с `max_employees_count` = 0.

        Проверяет, что API отклоняет запрос со статус-кодом 422,
        так как `max_employees_count` должен быть больше 0.
        """
        data = generate_license_data()
        data['max_employees_count'] = 0

        response = await client.post('/api/v1/admin/licenses/', json=data)

        assert response.status_code == 422
        result = response.json()

        assert result['detail'][0]['loc'] == ['body', 'max_employees_count']
        assert result['detail'][0]['msg'] == 'Input should be greater than 0'

    @pytest.mark.asyncio
    async def test_create_license_without_max_employees_count(self, client: AsyncClient):
        """Тест создания лицензии без `max_employees_count`.

        Проверяет, что API отклоняет запрос и возвращает ошибку 422,
        если отсутствует `max_employees_count`.
        """
        data = generate_license_data()
        del data['max_employees_count']

        response = await client.post('/api/v1/admin/licenses/', json=data)

        assert response.status_code == 422
        result = response.json()

        assert result['detail'][0]['loc'] == ['body', 'max_employees_count']
        assert result['detail'][0]['msg'] == 'Field required'

    @pytest.mark.asyncio
    async def test_create_license_with_invalid_max_employees_count(self, client: AsyncClient):
        """Тест создания лицензии с `max_employees_count`, переданным как строка.

        Проверяет, что API отклоняет запрос и возвращает ошибку 422,
        так как `max_employees_count` должен быть целым числом.
        """
        data = generate_license_data()
        data['max_employees_count'] = 'true'

        response = await client.post('/api/v1/admin/licenses/', json=data)

        assert response.status_code == 422
        result = response.json()

        assert result['detail'][0]['loc'] == ['body', 'max_employees_count']
        assert result['detail'][0]['msg'] == (
            'Input should be a valid integer, unable to parse string as an integer'
        )


class TestGetLicense:
    @pytest.mark.asyncio
    async def test_get_licenses(self, client: AsyncClient, test_license):
        """Тест получения списка лицензий.

        Проверяет, что API возвращает список лицензий, и каждая лицензия содержит
        ожидаемые поля: id, name, license_term, max_admins_count, max_employees_count,
        created_at, updated_at.
        """
        licenses = [await test_license() for _ in range(3)]

        response = await client.get('/api/v1/admin/licenses/')

        assert response.status_code == 200
        result = response.json()

        assert isinstance(result, list)
        assert len(result) == len(licenses)

        expected_keys = {
            'id',
            'name',
            'license_term',
            'max_admins_count',
            'max_employees_count',
            'created_at',
            'updated_at',
        }

        for license_data in result:
            assert isinstance(license_data, dict)
            assert expected_keys.issubset(license_data.keys())

    @pytest.mark.asyncio
    async def test_get_license_by_id(self, client: AsyncClient, async_session, test_license):
        """Тест получения лицензии по ID.

        Перед тестом вручную создаём запись в БД, чтобы гарантировать её существование.
        Затем делаем GET-запрос и проверяем корректность данных.
        """
        new_license = await test_license()

        response = await client.get(f'/api/v1/admin/licenses/{new_license.id}')

        assert response.status_code == 200
        result = response.json()

        assert result['id'] == new_license.id
        assert result['name'] == new_license.name
        assert result['license_term'] == 'P1D'
        assert result['max_admins_count'] == new_license.max_admins_count
        assert result['max_employees_count'] == new_license.max_employees_count

    @pytest.mark.asyncio
    async def test_get_license_not_found(self, client: AsyncClient):
        """Тест получения лицензии по несуществующему ID.

        Проверяет, что при запросе лицензии с несуществующим ID API возвращает статус-код 404
        и сообщение 'Объект не найден'.
        """
        response = await client.get('/api/v1/admin/licenses/99999')

        assert response.status_code == 404
        result = response.json()

        assert result == {'detail': 'Объект не найден'}


class TestPatchLicense:
    @pytest.mark.asyncio
    async def test_patch_license_success(self, client: AsyncClient, test_license):
        """Тест успешного обновления лицензии.

        Проверяет, что API корректно обновляет лицензию при передаче валидных данных.
        """
        new_license = await test_license()

        patch_data = {
            'name': 'Updated License',
            'license_term': 'P1Y',
            'max_admins_count': 20,
            'max_employees_count': 100,
        }

        response = await client.patch(f'/api/v1/admin/licenses/{new_license.id}', json=patch_data)

        assert response.status_code == 200
        result = response.json()

        assert result['id'] == new_license.id
        assert result['name'] == patch_data['name']
        assert result['license_term'] == 'P1Y'
        assert result['max_admins_count'] == patch_data['max_admins_count']
        assert result['max_employees_count'] == patch_data['max_employees_count']

    @pytest.mark.asyncio
    async def test_update_license_with_duplicate_name(self, client: AsyncClient, test_license):
        """Тест обновления лицензии с `name`, которое уже существует у другой лицензии.

        Проверяет, что API отклоняет обновление имени на уже существующее и возвращает 400.
        """
        license_1 = await test_license()
        license_2 = await test_license()

        patch_data = {'name': license_1.name}

        response = await client.patch(f'/api/v1/admin/licenses/{license_2.id}', json=patch_data)

        assert response.status_code == 400
        result = response.json()

        assert result['detail'] == f"Лицензия с именем '{license_1.name}' уже существует."

    @pytest.mark.asyncio
    async def test_patch_license_missing_name(self, client: AsyncClient, test_license):
        """Тест обновления лицензии без поля `name`.

        Проверяет, что API корректно обновляет лицензию, если `name` не передан.
        """
        new_license = await test_license()

        patch_data = {'license_term': 'P1D'}

        response = await client.patch(f'/api/v1/admin/licenses/{new_license.id}', json=patch_data)
        assert response.status_code == 200

        result = response.json()
        assert result['name'] == new_license.name
        assert result['license_term'] == patch_data['license_term']

    @pytest.mark.asyncio
    async def test_patch_license_invalid_name(self, client: AsyncClient, test_license):
        """Тест обновления лицензии с некорректным `name`.

        Проверяет, что API отклоняет запрос, если `name` содержит неверные данные.
        """
        new_license = await test_license()

        patch_data = {'name': 123}

        response = await client.patch(f'/api/v1/admin/licenses/{new_license.id}', json=patch_data)
        assert response.status_code == 422

        result = response.json()
        assert result['detail'][0]['loc'] == ['body', 'name']
        assert result['detail'][0]['msg'] == 'Input should be a valid string'

    @pytest.mark.asyncio
    async def test_patch_license_name_too_long(self, client: AsyncClient, test_license):
        """Тест обновления лицензии с `name`, содержащим 101 символ.

        Проверяет, что API отклоняет запрос со слишком длинным `name`.
        """
        new_license = await test_license()

        patch_data = {'name': 'A' * 101}

        response = await client.patch(f'/api/v1/admin/licenses/{new_license.id}', json=patch_data)
        assert response.status_code == 422

        result = response.json()
        assert result['detail'][0]['loc'] == ['body', 'name']
        assert result['detail'][0]['msg'] == 'String should have at most 100 characters'

    @pytest.mark.asyncio
    async def test_patch_license_invalid_license_term(self, client: AsyncClient, test_license):
        """Тест обновления лицензии с некорректным `license_term`.

        Проверяет, что API отклоняет запрос, если `license_term` не соответствует ISO 8601.
        """
        new_license = await test_license()

        patch_data = {'license_term': '1Y1S'}

        response = await client.patch(f'/api/v1/admin/licenses/{new_license.id}', json=patch_data)
        assert response.status_code == 422

        result = response.json()
        assert result['detail'][0]['loc'] == ['body', 'license_term']
        assert result['detail'][0]['msg'] == (
            'Value error, Поле не может быть пустым. Может быть целым числом, или строкой, '
            'обозначающее целое число, или строкой формата "P1D", "P1Y", "P1Y1D".'
        )

    @pytest.mark.asyncio
    async def test_patch_license_negative_max_admins(self, client: AsyncClient, test_license):
        """Тест обновления лицензии с отрицательным `max_admins_count`.

        Проверяет, что API отклоняет запрос, если `max_admins_count` < 1.
        """
        new_license = await test_license()

        patch_data = {'max_admins_count': -5}

        response = await client.patch(f'/api/v1/admin/licenses/{new_license.id}', json=patch_data)
        assert response.status_code == 422

        result = response.json()
        assert result['detail'][0]['loc'] == ['body', 'max_admins_count']
        assert result['detail'][0]['msg'] == 'Input should be greater than 0'

    @pytest.mark.asyncio
    async def test_patch_license_invalid_max_employees_count(
        self, client: AsyncClient, test_license
    ):
        """Тест обновления лицензии с некорректным `max_employees_count`.

        Проверяет, что API отклоняет запрос, если `max_employees_count` передан как строка.
        """
        new_license = await test_license()

        patch_data = {'max_employees_count': 'true'}

        response = await client.patch(f'/api/v1/admin/licenses/{new_license.id}', json=patch_data)
        assert response.status_code == 422

        result = response.json()
        assert result['detail'][0]['loc'] == ['body', 'max_employees_count']
        assert result['detail'][0]['msg'] == (
            'Input should be a valid integer, unable to parse string as an integer'
        )

    @pytest.mark.asyncio
    async def test_patch_license_not_found(self, client: AsyncClient):
        """Тест обновления несуществующей лицензии.

        Проверяет, что API возвращает 404 при попытке обновить несуществующую запись.
        """
        patch_data = {'name': 'Updated License'}

        response = await client.patch('/api/v1/admin/licenses/99999', json=patch_data)
        assert response.status_code == 404

        result = response.json()
        assert result == {'detail': 'Объект не найден'}


class TestDeleteLicense:
    @pytest.mark.asyncio
    async def test_delete_license_success(self, client: AsyncClient, test_license):
        """Тест успешного удаления лицензии.

        Проверяет, что API корректно удаляет лицензию и возвращает статус 204.
        """
        new_license = await test_license()

        response = await client.delete(f'/api/v1/admin/licenses/{new_license.id}')

        assert response.status_code == 204

        response_check = await client.get(f'/api/v1/admin/licenses/{new_license.id}')
        assert response_check.status_code == 404

    @pytest.mark.asyncio
    async def test_delete_license_not_found(self, client: AsyncClient):
        """Тест удаления несуществующей лицензии.

        Проверяет, что API возвращает 404 при попытке удалить несуществующую запись.
        """
        non_existent_id = 99999

        response = await client.delete(f'/api/v1/admin/licenses/{non_existent_id}')

        assert response.status_code == 404
        result = response.json()

        assert result == {'detail': 'Объект не найден'}
