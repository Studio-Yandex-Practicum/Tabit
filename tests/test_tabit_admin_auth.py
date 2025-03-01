from http import HTTPStatus

import pytest
from httpx import AsyncClient

from tests.constants import (
    BAD_EMAIL,
    BAD_PASSWORD,
    GOOD_PASSWORD,
    URL,
)
from tests.utils import is_valid_uuid


class TestLoginAdminTabit:
    """
    Тесты на вход в систему администраторов сервиса Tabit.

    /api/v1/admin/auth/login
    """

    @pytest.mark.asyncio
    async def test_login_admin(self, client: AsyncClient, superuser, admin):
        """Тест на вход в систему администраторов сервиса с валидными данными."""
        variants = (
            (superuser, 'суперпользователя'),
            (admin, 'администратора сервиса'),
        )
        for user, text in variants:
            login_payload = {'username': user.email, 'password': GOOD_PASSWORD}
            response = await client.post(URL.ADMIN_LOGIN, data=login_payload)
            assert (
                response.status_code == HTTPStatus.OK
            ), f'При авторизации {text} у ответа должен быть статус 200:\n{response.text}'
            result = response.json()
            for key in ('access_token', 'refresh_token', 'token_type'):
                assert key in result, f'В теле ответа нет ключа {key}'
                assert result[key], f'В теле ответа нет значения у ключа {key}'

    @pytest.mark.asyncio
    async def test_login_not_admin(
        self,
        client: AsyncClient,
        moderator,
        employee,
    ):
        """Тест на вход в систему администраторов сервиса модератора и пользователя от компании."""
        variants = (
            (moderator, 'модератора от компании'),
            (employee, 'пользователя от компании'),
        )
        for user, text in variants:
            login_payload = {'username': user.email, 'password': GOOD_PASSWORD}
            response = await client.post(URL.ADMIN_LOGIN, data=login_payload)
            assert (
                response.status_code == HTTPStatus.BAD_REQUEST
            ), f'При авторизации {text} у ответа должен быть статус 400:\n{response.text}'
            result = response.json()
            assert 'detail' in result, 'В теле ответа с ошибкой нет ключа detail'

    @pytest.mark.asyncio
    async def test_login_admin_invalid(self, client: AsyncClient, admin):
        """
        Тест на вход в систему администраторов сервиса без заполнения обязательных полей формы.
        """
        bad_login_payloads: tuple[dict, ...] = (
            {
                'password': GOOD_PASSWORD,
            },
            {
                'username': admin.email,
            },
            {},
        )
        for bad_login_payload in bad_login_payloads:
            response = await client.post(URL.ADMIN_LOGIN, data=bad_login_payload)
            assert (
                response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY
            ), f'Не корректный ответ с данными\n{bad_login_payload}\n{response.text}'
            result = response.json()
            assert 'detail' in result, 'В теле ответа с ошибкой нет ключа detail'

    @pytest.mark.asyncio
    async def test_login_admin_bad_password(self, client: AsyncClient, admin):
        """Тест на вход в систему администраторов сервиса под неверным паролем."""
        login_payload = {'username': admin.email, 'password': f'NOT {GOOD_PASSWORD}'}
        response = await client.post(URL.ADMIN_LOGIN, data=login_payload)
        assert (
            response.status_code == HTTPStatus.BAD_REQUEST
        ), f'Не корректный ответ с данными\n{login_payload}\n{response.text}'
        result = response.json()
        assert 'detail' in result, 'В теле ответа с ошибкой нет ключа detail'


class TestLogoutAdminTabit:
    """
    Тесты на выход из системы администраторов сервиса Tabit.

    /api/v1/admin/auth/logout
    """

    @pytest.mark.asyncio
    async def test_logout_admin(self, client: AsyncClient, superuser_token, admin_token):
        """Тест на выход из системы администраторов сервиса."""
        variants = (
            (superuser_token, 'суперпользователя'),
            (admin_token, 'администратора сервиса'),
        )
        for token, text in variants:
            response = await client.post(URL.ADMIN_LOGOUT, headers=token)
            assert (
                response.status_code == HTTPStatus.NO_CONTENT
            ), f'При выходе из системы {text} должен быть статус ответа 204:\n{response.text}'

    @pytest.mark.asyncio
    async def test_logout_admin_not_access(
        self,
        client: AsyncClient,
        moderator_token,
        employee_token,
    ):
        """Тест на выход из системы администраторов сервиса."""
        variants: tuple = (
            (moderator_token, 'модератора от компании'),
            (employee_token, 'пользователя от компании'),
            ({}, 'неавторизованного пользователя'),
        )
        for token, text in variants:
            response = await client.post(URL.ADMIN_LOGOUT, headers=token)
            assert (
                response.status_code == HTTPStatus.UNAUTHORIZED
            ), f'При выходе из системы {text} должен быть статус ответа 401:\n{response.text}'


class TestCreateAdminTabit:
    """
    Тесты на создание администраторов сервиса Tabit.

    /api/v1/admin/auth
    """

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'payload',
        (
            {
                'patronymic': 'string',
                'phone_number': 'string',
                'email': 'user1@example.com',
                'password': GOOD_PASSWORD,
                'name': 'string',
                'surname': 'string',
            },
            {
                'phone_number': 'string',
                'email': 'user2@example.com',
                'password': GOOD_PASSWORD,
                'name': 'string',
                'surname': 'string',
            },
            {
                'patronymic': 'string',
                'email': 'user3@example.com',
                'password': GOOD_PASSWORD,
                'name': 'string',
                'surname': 'string',
            },
            {
                'email': 'user4@example.com',
                'password': GOOD_PASSWORD,
                'name': 'string',
                'surname': 'string',
            },
        ),
    )
    async def test_create_admin(
        self,
        client: AsyncClient,
        superuser_token,
        payload: dict[str, str],
    ):
        """
        Тест успешного создания администратора сервисаTabit.

        Проверит, что при передачи на конечную точку валидных данных, с вернет ответ 201.
        Проверит тело ответа на наличие и корректность возвращаемых значений.
        Все примеры содержат обязательные поля, но не все необязательные.
        """
        response = await client.post(
            URL.ADMIN_AUTH,
            json=payload,
            headers=superuser_token,
        )
        assert response.status_code == HTTPStatus.CREATED, response.text
        data = response.json()
        for key in (
            'id',
            'email',
            'name',
            'surname',
            'patronymic',
            'phone_number',
            'created_at',
            'updated_at',
        ):
            assert key in data, f'Ключа {key} нет в теле ответа.'
        assert is_valid_uuid(data['id']), 'Поле id не является uuid.'
        for key in data:
            if key in payload:
                assert (
                    data[key] == payload[key]
                ), f'Значение ключа {key} не соответствует переданному.'
            elif key in ('id', 'created_at', 'updated_at'):
                assert (
                    data[key] is not None
                ), f'Значение ключа {key} не должно быть пустым или null.'
            else:
                assert data[key] is None, f'Значение ключа {key} должно быть пустым или null.'

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'bad_payload',
        (
            {
                'email': 'user1@example.com',
                'password': GOOD_PASSWORD,
                'name': 'string',
            },
            {
                'email': 'user2@example.com',
                'password': GOOD_PASSWORD,
                'surname': 'string',
            },
            {
                'password': GOOD_PASSWORD,
                'name': 'string',
                'surname': 'string',
            },
            {
                'email': 'user4@example.com',
                'name': 'string',
                'surname': 'string',
            },
        ),
    )
    async def test_create_admin_bad_request(
        self,
        client: AsyncClient,
        superuser_token,
        bad_payload: dict[str, str],
    ):
        """
        Тест на ошибку при создании администратора сервиса Tabit, если были переданы не все поля.
        """
        response = await client.post(
            URL.ADMIN_AUTH,
            json=bad_payload,
            headers=superuser_token,
        )
        assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, response.text

        result = response.json()
        assert 'detail' in result, 'В теле ответа с ошибкой нет ключа detail'

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'bad_password',
        BAD_PASSWORD,
    )
    async def test_create_admin_bad_password(
        self,
        client: AsyncClient,
        superuser_token,
        bad_password: tuple[str, ...],
    ):
        """Тест на ошибку при создании администратора сервиса Tabit, если не валидный пароль."""
        for i, password in enumerate(bad_password):
            bad_payload: dict[str, str] = {
                'email': f'user{i}@example.com',
                'password': password,
                'name': 'string',
                'surname': 'string',
            }
            response = await client.post(
                URL.ADMIN_AUTH,
                json=bad_payload,
                headers=superuser_token,
            )
            assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, response.text

            result = response.json()
            assert 'detail' in result, 'В теле ответа с ошибкой нет ключа detail'

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'bad_email',
        BAD_EMAIL,
    )
    async def test_create_admin_bad_email(
        self,
        client: AsyncClient,
        superuser_token,
        bad_email: tuple[str, ...],
    ):
        """Тест на ошибку при создании администратора сервиса Tabit, если не валидный пароль."""
        for email in bad_email:
            bad_payload: dict[str, str] = {
                'email': email,
                'password': GOOD_PASSWORD,
                'name': 'string',
                'surname': 'string',
            }
            response = await client.post(
                URL.ADMIN_AUTH,
                json=bad_payload,
                headers=superuser_token,
            )
            assert response.status_code == HTTPStatus.UNPROCESSABLE_ENTITY, response.text

            result = response.json()
            assert 'detail' in result, 'В теле ответа с ошибкой нет ключа detail'

    @pytest.mark.asyncio
    async def test_create_admin_unique_email(self, client: AsyncClient, superuser_token):
        """
        Тест на ошибку при создании администратора сервиса Tabit,
        если пользователь с такой электронной почтой уже есть.
        """
        payload: dict[str, str] = {
            'email': 'user@example.com',
            'password': GOOD_PASSWORD,
            'name': 'string',
            'surname': 'string',
        }
        for _ in range(2):
            response = await client.post(
                URL.ADMIN_AUTH,
                json=payload,
                headers=superuser_token,
            )
        assert response.status_code == HTTPStatus.BAD_REQUEST, response.text

        result = response.json()
        assert 'detail' in result, 'В теле ответа с ошибкой нет ключа detail'

    @pytest.mark.asyncio
    async def test_create_admin_not_access(
        self,
        client: AsyncClient,
        admin_token,
        moderator_token,
        employee_token,
    ):
        """
        Тест на ошибку при создании администратора сервиса Tabit,
        если создавать попытается не суперпользователь сервиса.
        """
        payload: dict[str, str] = {
            'email': 'user10@example.com',
            'password': GOOD_PASSWORD,
            'name': 'string',
            'surname': 'string',
        }
        variants: tuple = (
            ({}, HTTPStatus.UNAUTHORIZED, 'неавторизованным пользователем'),
            (admin_token, HTTPStatus.FORBIDDEN, 'администратором сервиса'),
            (moderator_token, HTTPStatus.UNAUTHORIZED, 'модератором от компании'),
            (employee_token, HTTPStatus.UNAUTHORIZED, 'пользователем от компании'),
        )
        for token, status, text in variants:
            response = await client.post(
                URL.ADMIN_AUTH,
                json=payload,
                headers=token,
            )
            assert response.status_code == status, (
                f'При попытке создать администратора сервиса {text} '
                f'не было ответа cо статусом {status}:\n{response.text}'
            )
            result = response.json()
            assert 'detail' in result, 'В теле ответа с ошибкой нет ключа detail'


class TestGetAdminTabit:
    """
    Тесты на получение списка администраторов сервиса Tabit.

    /api/v1/admin/auth
    """

    @pytest.mark.asyncio
    async def test_get_admins(self, client: AsyncClient, superuser_token):
        """Тесты на получение списка администраторов сервиса Tabit."""
        response = await client.get(URL.ADMIN_AUTH, headers=superuser_token)
        assert response.status_code == HTTPStatus.OK, response.text

        data = response.json()
        assert isinstance(data, list), 'Ответ должен возвращаться в виде списка'
        assert len(data) != 0, 'Ответ должен возвращаться не с пустым списком'

        data_row = data[0]
        for key in (
            'id',
            'email',
            'name',
            'surname',
            'patronymic',
            'phone_number',
            'created_at',
            'updated_at',
        ):
            assert key in data_row, f'Ключа {key} нет в теле ответа:\n{data_row}'
            assert (
                data_row[key] if key not in ('patronymic', 'phone_number') else True
            ), f'Значение ключа {key} не должно быть пустым или быть null:\n{data_row}'
        for key in ('password', 'hashed_password', 'is_active', 'is_superuser', 'is_verified'):
            assert (
                key not in data_row
            ), f'Значение ключа {key} не должно быть в теле ответа:\n{data_row}'

    @pytest.mark.asyncio
    async def test_get_admin_not_access(
        self,
        client: AsyncClient,
        admin_token,
        moderator_token,
        employee_token,
    ):
        """
        Тест на ошибку при получение списка администраторов сервиса Tabit,
        если создавать попытается не суперпользователь сервиса.
        """
        variants: tuple = (
            ({}, HTTPStatus.UNAUTHORIZED, 'неавторизованным пользователем'),
            (admin_token, HTTPStatus.FORBIDDEN, 'администратором сервиса'),
            (moderator_token, HTTPStatus.UNAUTHORIZED, 'модератором от компании'),
            (employee_token, HTTPStatus.UNAUTHORIZED, 'пользователем от компании'),
        )
        for token, status, text in variants:
            response = await client.get(URL.ADMIN_AUTH, headers=token)
            assert response.status_code == status, (
                f'При попытке получить список администраторов сервиса {text} '
                f'не было ответа cо статусом {status}:\n{response.text}'
            )
            result = response.json()
            assert 'detail' in result, 'В теле ответа с ошибкой нет ключа detail'


class TestGetMeAdminTabit:
    """
    Тест получение своих личных данных для администратора сервиса Tabit.

    /api/v1/admin/auth/me
    """

    @pytest.mark.asyncio
    async def test_get_me_admin(self, client: AsyncClient, superuser_token, admin_token):
        """Тесты на получение личных данных для администраторов сервиса Tabit."""
        variants = (
            (superuser_token, 'суперпользователем'),
            (admin_token, 'администратором сервиса'),
        )
        for token, text in variants:
            response = await client.get(URL.ADMIN_ME, headers=token)
            assert response.status_code == HTTPStatus.OK, (
                f'При получение личных данных {text} '
                f'должен быть ответ со статусом 200:\n{response.text}'
            )
            data = response.json()
            for key in (
                'id',
                'email',
                'name',
                'surname',
                'patronymic',
                'phone_number',
                'created_at',
                'updated_at',
            ):
                assert key in data, f'Ключа {key} нет в теле ответа при запросе {text}:\n{data}'
                assert data[key] if key not in ('patronymic', 'phone_number') else True, (
                    f'Значение ключа {key} не должно быть пустым или быть null при запросе {text}:'
                    f'\n{data}'
                )
            for key in ('password', 'hashed_password', 'is_active', 'is_superuser', 'is_verified'):
                assert key not in data, (
                    f'Значение ключа {key} не должно быть в теле ответа при запросе {text}:\n'
                    f'{data}'
                )

    @pytest.mark.asyncio
    async def test_get_me_admin_not_access(
        self,
        client: AsyncClient,
        moderator_token,
        employee_token,
    ):
        """
        Тест на ошибку при получение личных данных для администраторов сервиса Tabit,
        если создавать попытается не суперпользователь сервиса.
        """
        variants: tuple = (
            ({}, HTTPStatus.UNAUTHORIZED, 'неавторизованным пользователем'),
            (moderator_token, HTTPStatus.UNAUTHORIZED, 'модератором от компании'),
            (employee_token, HTTPStatus.UNAUTHORIZED, 'пользователем от компании'),
        )
        for token, status, text in variants:
            response = await client.get(URL.ADMIN_AUTH, headers=token)
            assert response.status_code == status, (
                f'При попытке получить личные данные {text} '
                f'не было ответа cо статусом {status}:\n{response.text}'
            )
            result = response.json()
            assert 'detail' in result, 'В теле ответа с ошибкой нет ключа detail'


class TestPatchMeAdminTabit:
    """
    Тест изменения своих личных данных для администратора сервиса Tabit.

    /api/v1/admin/auth/me
    """

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'payload',
        (
            {
                'patronymic': 'Императрица',
                'phone_number': '8 800 700-06-11',
                'name': 'Киширика',
                'surname': 'Киширису',
            },
            {
                'phone_number': '8 800 700-06-11',
                'surname': 'Киширису',
            },
            {
                'patronymic': 'Императрица',
            },
        ),
    )
    async def test_patch_me_admin(
        self,
        client: AsyncClient,
        superuser_token,
        admin_token,
        payload: dict[str, str],
    ):
        """Тесты на изменение личных данных для администраторов сервиса Tabit."""
        variants = (
            (superuser_token, 'суперпользователем'),
            (admin_token, 'администратором сервиса'),
        )
        for token, text in variants:
            response_get = await client.get(
                URL.ADMIN_ME,
                headers=token,
            )
            data_before = response_get.json()
            response_patch = await client.patch(
                URL.ADMIN_ME,
                json=payload,
                headers=token,
            )
            assert response_patch.status_code == HTTPStatus.OK, (
                f'При изменение своих личных данных {text} статус ответа должен быть 200:\n'
                f'{response_patch.text}'
            )
            data_after = response_patch.json()
            for key in data_before:
                if key in payload:
                    assert (
                        data_after[key] == payload[key]
                    ), f'При изменение своих личных данных {text} значение {key} не поменялось.'
                elif key == 'updated_at':
                    assert (
                        data_after[key] != data_before[key]
                    ), f'При изменение своих личных данных {text} значение {key} не поменялось.'
                else:
                    assert data_after[key] == data_before[key], (
                        f'При изменение своих личных данных {text} значение {key} поменялось, '
                        'а не должно.'
                    )

    @pytest.mark.asyncio
    async def test_patch_me_admin_not_access(
        self,
        client: AsyncClient,
        moderator_token,
        employee_token,
    ):
        """
        Тест на ошибку при изменение личных данных для администраторов сервиса Tabit,
        если создавать попытается не суперпользователь или админ сервиса.
        """
        payload: dict[str, str] = {'name': 'Киширика', 'surname': 'Киширису'}
        variants: tuple = (
            ({}, HTTPStatus.UNAUTHORIZED, 'неавторизованным пользователем'),
            (moderator_token, HTTPStatus.UNAUTHORIZED, 'модератором от компании'),
            (employee_token, HTTPStatus.UNAUTHORIZED, 'пользователем от компании'),
        )
        for token, status, text in variants:
            response = await client.patch(
                URL.ADMIN_ME,
                json=payload,
                headers=token,
            )
            assert response.status_code == status, (
                f'При попытке получить личные данные {text} '
                f'не было ответа cо статусом {status}:\n{response.text}'
            )
            result = response.json()
            assert 'detail' in result, 'В теле ответа с ошибкой нет ключа detail'


class TestGetIdAdminTabit:
    """
    Тесты получение личных данных администратора сервиса Tabit по его id.

    /api/v1/admin/auth/{user_id}
    """

    @pytest.mark.asyncio
    async def test_get_id_admin(self, client: AsyncClient, superuser_token, superuser, admin):
        variants = (
            (superuser, 'суперпользователя'),
            (admin, 'администратора сервиса'),
        )
        for user, text in variants:
            url = URL.ADMIN_AUTH + str(user.id)
            response = await client.get(url, headers=superuser_token)
            assert response.status_code == HTTPStatus.OK, (
                f'При получение личных данных {text} по его id'
                f'должен быть ответ со статусом 200:\n{response.text}'
            )
            data = response.json()
            for key in (
                'id',
                'email',
                'name',
                'surname',
                'patronymic',
                'phone_number',
                'created_at',
                'updated_at',
            ):
                assert key in data, f'Ключа {key} нет в теле ответа при запросе {text}:\n{data}'
                assert data[key] if key not in ('patronymic', 'phone_number') else True, (
                    f'Значение ключа {key} не должно быть пустым или быть null при запросе {text}:'
                    f'\n{data}'
                )
            for key in ('password', 'hashed_password', 'is_active', 'is_superuser', 'is_verified'):
                assert key not in data, (
                    f'Значение ключа {key} не должно быть в теле ответа при запросе {text}:\n'
                    f'{data}'
                )

    @pytest.mark.asyncio
    async def test_get_id_admin_not_access(
        self,
        client: AsyncClient,
        admin,
        admin_token,
        moderator_token,
        employee_token,
    ):
        """
        Тест на ошибку при получение личных данных для администраторов сервиса Tabit по его id,
        если создавать попытается не суперпользователь сервиса.
        """
        variants: tuple = (
            ({}, HTTPStatus.UNAUTHORIZED, 'неавторизованным пользователем'),
            (admin_token, HTTPStatus.FORBIDDEN, 'администратором сервиса'),
            (moderator_token, HTTPStatus.UNAUTHORIZED, 'модератором от компании'),
            (employee_token, HTTPStatus.UNAUTHORIZED, 'пользователем от компании'),
        )
        url = URL.ADMIN_AUTH + str(admin.id)
        for token, status, text in variants:
            response = await client.get(url, headers=token)
            assert response.status_code == status, (
                f'При попытке {text} получить данные администратора сервиса по его id '
                f'не было ответа cо статусом {status}:\n{response.text}'
            )
            result = response.json()
            assert 'detail' in result, 'В теле ответа с ошибкой нет ключа detail'


class TestPatchIdAdminTabit:
    """
    Тесты изменения личных данных администратора сервиса Tabit по его id.

    /api/v1/admin/auth/{user_id}
    """

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'payload',
        (
            {
                'patronymic': 'Императрица',
                'phone_number': '8 800 700-06-11',
                'name': 'Киширика',
                'surname': 'Киширису',
            },
            {
                'phone_number': '8 800 700-06-11',
                'surname': 'Киширису',
            },
            {
                'patronymic': 'Императрица',
            },
        ),
    )
    async def test_patch_id_admin(
        self,
        client: AsyncClient,
        superuser_token,
        superuser,
        admin,
        payload: dict[str, str],
    ):
        """Тест на изменение данных администраторов сервиса Tabit по его id."""
        variants = (
            (superuser, 'суперпользователя'),
            (admin, 'администратора сервиса'),
        )
        for user, text in variants:
            url = URL.ADMIN_AUTH + str(user.id)
            response_get = await client.get(
                url,
                headers=superuser_token,
            )
            data_before = response_get.json()
            response_patch = await client.patch(
                url,
                json=payload,
                headers=superuser_token,
            )
            assert response_patch.status_code == HTTPStatus.OK, (
                f'При изменение данных {text} по его id статус ответа должен быть 200:\n'
                f'{response_patch.text}'
            )
            data_after = response_patch.json()
            for key in data_before:
                if key in payload:
                    assert (
                        data_after[key] == payload[key]
                    ), f'При изменение данных {text} по его id значение {key} не поменялось.'
                elif key == 'updated_at':
                    assert (
                        data_after[key] != data_before[key]
                    ), f'При изменение данных {text} по его id значение {key} не поменялось.'
                else:
                    assert data_after[key] == data_before[key], (
                        f'При изменение данных {text} по его id значение {key} поменялось, '
                        'а не должно.'
                    )

    @pytest.mark.asyncio
    async def test_patch_id_admin_not_access(
        self,
        client: AsyncClient,
        admin,
        admin_token,
        moderator_token,
        employee_token,
    ):
        """
        Тест на ошибку при изменение личных данных для администраторов сервиса Tabit,
        если создавать попытается не суперпользователь.
        """
        payload: dict[str, str] = {'name': 'Киширика', 'surname': 'Киширису'}
        url = URL.ADMIN_AUTH + str(admin.id)
        variants: tuple = (
            ({}, HTTPStatus.UNAUTHORIZED, 'неавторизованным пользователем'),
            (admin_token, HTTPStatus.FORBIDDEN, 'администратором сервиса'),
            (moderator_token, HTTPStatus.UNAUTHORIZED, 'модератором от компании'),
            (employee_token, HTTPStatus.UNAUTHORIZED, 'пользователем от компании'),
        )
        for token, status, text in variants:
            response = await client.patch(
                url,
                json=payload,
                headers=token,
            )
            assert response.status_code == status, (
                f'При попытке {text} изменить данные администратора сервиса по его id '
                f'не было ответа cо статусом {status}:\n{response.text}'
            )
            result = response.json()
            assert 'detail' in result, 'В теле ответа с ошибкой нет ключа detail'


class TestDeleteIdAdminTabit:
    """
    Тесты удаления администратора сервиса Tabit по его id.

    /api/v1/admin/auth/{user_id}
    """

    @pytest.mark.asyncio
    async def test_delete_id_admin(
        self,
        client: AsyncClient,
        superuser_token,
        admin,
    ):
        """Тест удаления администратора сервиса Tabit по его id."""
        url = URL.ADMIN_AUTH + str(admin.id)
        response_delete = await client.delete(
            url,
            headers=superuser_token,
        )
        assert response_delete.status_code == HTTPStatus.NO_CONTENT, (
            f'При удачном удалении администратора сервиса по его id '
            'статус ответа должен быть 204:\n'
            f'{response_delete.text}'
        )
        response_get = await client.get(
            url,
            headers=superuser_token,
        )
        assert response_get.status_code == HTTPStatus.NOT_FOUND, (
            f'Возможно, администратор сервиса не был удален из базы данных:\n'
            f'{response_get.text}'
        )

    @pytest.mark.asyncio
    async def test_not_delete_id_superuser(
        self,
        client: AsyncClient,
        superuser_token,
        superuser,
    ):
        """Тест на ошибку удаления суперпользователя Tabit по его id."""
        url = URL.ADMIN_AUTH + str(superuser.id)
        response_delete = await client.delete(
            url,
            headers=superuser_token,
        )
        assert response_delete.status_code == HTTPStatus.BAD_REQUEST, (
            f'При попытке удалить суперпользователя по его id статус ответа должен быть 204:\n'
            f'{response_delete.text}'
        )
        response_get = await client.get(
            url,
            headers=superuser_token,
        )
        assert response_get.status_code == HTTPStatus.OK, (
            f'Возможно, суперпользователь был удален из базы данных '
            '(если так, возможно, вернулся ответ со статусом 401):\n'
            f'{response_get.text}'
        )

    @pytest.mark.asyncio
    async def test_delete_id_admin_not_access(
        self,
        client: AsyncClient,
        admin,
        superuser_token,
        admin_token,
        moderator_token,
        employee_token,
    ):
        """
        Тест на ошибку при удалении администраторов сервиса Tabit по его id,
        если создавать попытается не суперпользователь.
        """
        url = URL.ADMIN_AUTH + str(admin.id)
        variants: tuple = (
            ({}, HTTPStatus.UNAUTHORIZED, 'неавторизованным пользователем'),
            (admin_token, HTTPStatus.FORBIDDEN, 'администратором сервиса'),
            (moderator_token, HTTPStatus.UNAUTHORIZED, 'модератором от компании'),
            (employee_token, HTTPStatus.UNAUTHORIZED, 'пользователем от компании'),
        )
        for token, status, text in variants:
            response_delete = await client.delete(
                url,
                headers=token,
            )
            assert response_delete.status_code == status, (
                f'При попытке {text} удалении администратора сервиса по его id статус ответа '
                f'должен быть {status}:\n'
                f'{response_delete.text}'
            )
            response_get = await client.get(
                url,
                headers=superuser_token,
            )
            assert response_get.status_code == HTTPStatus.OK, (
                f'Возможно, администратор сервиса был удален из базы данных:\n'
                f'{response_get.text}'
            )


class TestRefreshTokenAdminTabit:
    """
    Тесты получения нового токена по refresh-token для администраторов сервиса Tabit.

    /api/v1/admin/auth/refresh-token
    """

    @pytest.mark.asyncio
    async def test_refresh_token_admin(
        self,
        client: AsyncClient,
        superuser_refresh_token,
        admin_refresh_token,
    ):
        """Тест получения нового токена по refresh-token для администраторов сервиса Tabit."""
        variants = (
            (superuser_refresh_token, 'суперпользователем'),
            (admin_refresh_token, 'администратором сервиса'),
        )
        for token, text in variants:
            response = await client.post(URL.ADMIN_REFRESH, headers=token)
            assert (
                response.status_code == HTTPStatus.OK
            ), f'При получение токена {text} у ответа должен быть статус 200:\n{response.text}'
            result = response.json()
            for key in ('access_token', 'refresh_token', 'token_type'):
                assert key in result, f'В теле ответа нет ключа {key}'
                assert result[key], f'В теле ответа нет значения у ключа {key}'

    @pytest.mark.asyncio
    async def test_refresh_token_admin_not_access(
        self,
        client: AsyncClient,
        moderator_refresh_token,
        employee_refresh_token,
    ):
        """
        Тест на ошибку получения нового токена по refresh-token для администраторов сервиса Tabit,
        если это не суперпользователь и не администратор сервиса.
        """
        variants: tuple = (
            ({}, 'не авторизированным пользователем'),
            (moderator_refresh_token, 'модератором от компании'),
            (employee_refresh_token, 'пользователем от компании'),
        )
        for token, text in variants:
            response = await client.post(URL.ADMIN_REFRESH, headers=token)
            assert response.status_code == HTTPStatus.UNAUTHORIZED, (
                f'При попытке получения токена {text} у ответа должен быть статус 401:\n'
                f'{response.text}'
            )
            result = response.json()
            assert 'detail' in result, 'В теле ответа с ошибкой нет ключа detail'


class TestForgotPasswordAdminTabit:
    """
    Тесты восстановление пароля администраторов сервиса Tabit.

    /api/v1/admin/auth/forgot-password
    """

    # TODO: Написать тесты, когда конечная точка будет работать.


class TestForgotResetAdminTabit:
    """
    Тесты сброса пароля администраторов сервиса Tabit.

    /api/v1/admin/auth/reset-password
    """

    # TODO: Написать тесты, когда конечная точка будет работать.
