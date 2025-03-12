import pytest
from fastapi import status
from httpx import AsyncClient

from src.users.models.enum import RoleUserTabit
from tests.constants import (
    GOOD_PASSWORD,
    MODERATOR_TELEGRAM,
    PAYLOAD_FOR_PATCH_USER,
    PAYLOAD_FOR_PATCH_USER_EXTRA,
    URL,
    USER_TELEGRAM,
)


class TestLoginUser:
    """
    Тесты на вход в систему пользователей сервиса Tabit.

    /api/v1/auth/login
    """

    @pytest.mark.asyncio
    async def test_login_user(self, client: AsyncClient, moderator, employee):
        """Тест на вход в систему пользователей сервиса с валидными данными."""
        variants = (
            (moderator, 'модератора от компании'),
            (employee, 'пользователя от компании'),
        )
        for user, text in variants:
            login_payload = {'username': user.email, 'password': GOOD_PASSWORD}
            response = await client.post(URL.USER_LOGIN, data=login_payload)
            assert (
                response.status_code == status.HTTP_200_OK
            ), f'При авторизации {text} у ответа должен быть статус 200:\n{response.text}'
            result = response.json()
            for key in ('access_token', 'refresh_token', 'token_type'):
                assert key in result, f'В теле ответа нет ключа {key}'
                assert result[key], f'В теле ответа нет значения у ключа {key}'

    @pytest.mark.asyncio
    async def test_login_not_user(self, client: AsyncClient, superuser, admin):
        """
        Тест на вход в систему пользователей сервиса для пользователей
        суперпользователя и администратора сервиса.
        """
        variants = (
            (superuser, 'суперпользователя'),
            (admin, 'администратора сервиса'),
        )
        for user, text in variants:
            login_payload = {'username': user.email, 'password': GOOD_PASSWORD}
            response = await client.post(URL.USER_LOGIN, data=login_payload)
            assert (
                response.status_code == status.HTTP_400_BAD_REQUEST
            ), f'При авторизации {text} у ответа должен быть статус 400:\n{response.text}'
            result = response.json()
            assert 'detail' in result, 'В теле ответа с ошибкой нет ключа detail'

    @pytest.mark.asyncio
    async def test_login_user_invalid(self, client: AsyncClient, employee):
        """
        Тест на вход в систему пользователей сервиса без заполнения обязательных полей формы.
        """
        bad_login_payloads: tuple[dict, ...] = (
            {
                'password': GOOD_PASSWORD,
            },
            {
                'username': employee.email,
            },
            {},
        )
        for bad_login_payload in bad_login_payloads:
            response = await client.post(URL.ADMIN_LOGIN, data=bad_login_payload)
            assert (
                response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
            ), f'Не корректный ответ с данными\n{bad_login_payload}\n{response.text}'
            result = response.json()
            assert 'detail' in result, 'В теле ответа с ошибкой нет ключа detail'

    @pytest.mark.asyncio
    async def test_login_user_bad_password(self, client: AsyncClient, employee):
        """Тест на вход в систему пользователей сервиса под неверным паролем."""
        login_payload = {'username': employee.email, 'password': f'NOT {GOOD_PASSWORD}'}
        response = await client.post(URL.ADMIN_LOGIN, data=login_payload)
        assert (
            response.status_code == status.HTTP_400_BAD_REQUEST
        ), f'Не корректный ответ с данными\n{login_payload}\n{response.text}'
        result = response.json()
        assert 'detail' in result, 'В теле ответа с ошибкой нет ключа detail'


class TestLogoutUser:
    """
    Тесты на выход из системы пользователей сервиса Tabit.

    /api/v1/auth/logout
    """

    @pytest.mark.asyncio
    async def test_logout_user(self, client: AsyncClient, moderator_token, employee_token):
        """Тест на выход из системы пользователей сервиса."""
        variants = (
            (moderator_token, 'модератора от компании'),
            (employee_token, 'пользователя от компании'),
        )
        for token, text in variants:
            response = await client.post(URL.USER_LOGOUT, headers=token)
            assert (
                response.status_code == status.HTTP_204_NO_CONTENT
            ), f'При выходе из системы {text} должен быть статус ответа 204:\n{response.text}'

    @pytest.mark.asyncio
    async def test_logout_user_not_access(self, client: AsyncClient, superuser_token, admin_token):
        """Тест на выход из системы пользователей сервиса."""
        variants: tuple = (
            (superuser_token, 'суперпользователя'),
            (admin_token, 'администратора сервиса'),
            ({}, 'неавторизованного пользователя'),
        )
        for token, text in variants:
            response = await client.post(URL.USER_LOGOUT, headers=token)
            assert (
                response.status_code == status.HTTP_401_UNAUTHORIZED
            ), f'При выходе из системы {text} должен быть статус ответа 401:\n{response.text}'


class TestRefreshTokenUser:
    """
    Тесты получения нового токена по refresh-token для пользователей сервиса Tabit.

    /api/v1/auth/refresh-token
    """

    @pytest.mark.asyncio
    async def test_refresh_token_user(
        self,
        client: AsyncClient,
        moderator_refresh_token,
        employee_refresh_token,
    ):
        """Тест получения нового токена по refresh-token для пользователя сервиса Tabit."""
        variants = (
            (moderator_refresh_token, 'модератором от компании'),
            (employee_refresh_token, 'пользователем от компании'),
        )
        for token, text in variants:
            response = await client.post(URL.USER_REFRESH, headers=token)
            assert (
                response.status_code == status.HTTP_200_OK
            ), f'При получение токена {text} у ответа должен быть статус 200:\n{response.text}'
            result = response.json()
            for key in ('access_token', 'refresh_token', 'token_type'):
                assert key in result, f'В теле ответа нет ключа {key}'
                assert result[key], f'В теле ответа нет значения у ключа {key}'

    @pytest.mark.asyncio
    async def test_refresh_token_user_not_access(
        self,
        client: AsyncClient,
        superuser_refresh_token,
        admin_refresh_token,
    ):
        """
        Тест на ошибку получения нового токена по refresh-token для пользователя сервиса Tabit,
        если это суперпользователь или администратор сервиса.
        """
        variants: tuple = (
            ({}, 'не авторизированным пользователем'),
            (superuser_refresh_token, 'суперпользователем'),
            (admin_refresh_token, 'администратором сервиса'),
        )
        for token, text in variants:
            response = await client.post(URL.USER_REFRESH, headers=token)
            assert response.status_code == status.HTTP_401_UNAUTHORIZED, (
                f'При попытке получения токена {text} у ответа должен быть статус 401:\n'
                f'{response.text}'
            )
            result = response.json()
            assert 'detail' in result, 'В теле ответа с ошибкой нет ключа detail'



class TestGetMeUser:
    """
    Тест получение своих личных данных для пользователя сервиса Tabit.

    /api/v1/auth/me
    """

    @pytest.mark.asyncio
    async def test_get_me_user(self, client: AsyncClient, employee_token, moderator_token):
        """Тесты на получение личных данных для пользователя сервиса Tabit."""
        variants = (
            (moderator_token, RoleUserTabit.ADMIN, 'модератора от компании'),
            (employee_token, RoleUserTabit.EMPLOYEE, 'сотрудника компании'),
        )
        for token, role, text in variants:
            response = await client.get(URL.USER_ME, headers=token)
            assert response.status_code == status.HTTP_200_OK, (
                f'При получение личных данных {text} '
                f'должен быть ответ со статусом 200:\n{response.text}'
            )
            data = response.json()
            for key in (
                'id',
                'email',
                'is_active',
                'is_superuser',
                'is_verified',
                'name',
                'surname',
                'patronymic',
                'phone_number',
                'birthday',
                'telegram_username',
                'role',
                'start_date_employment',
                'end_date_employment',
                'avatar_link',
                'company_id',
                'current_department_id',
                'last_department_id',
                'department_transition_date',
                'employee_position',
                'created_at',
                'updated_at',
            ):
                assert key in data, f'Ключа {key} нет в теле ответа при запросе {text}:\n{data}'
                assert data[key] not in ('', None) if key not in (
                    'patronymic',
                    'phone_number',
                    'birthday',
                    'telegram_username',
                    'start_date_employment',
                    'end_date_employment',
                    'avatar_link',  
                    'current_department_id',
                    'last_department_id',
                    'department_transition_date',
                    'employee_position',    
                ) else True, (
                    f'Значение ключа {key} не должно быть пустым или быть null при запросе {text}:'
                    f'\n{data}'
                )
            assert data['role'] == role, (
                f'Роль пользователя {role} не соответствукт роли в ответе: {data['role']}'
            )
            for key in ('password', 'hashed_password'):
                assert key not in data, (
                    f'Значение ключа {key} не должно быть в теле ответа при запросе {text}:\n'
                    f'{data}'
                )

    @pytest.mark.asyncio
    async def test_get_me_admin_not_access(
        self,
        client: AsyncClient,
        superuser_token,
    ):
        """
        Тест на ошибку при получение личных данных для администраторов сервиса Tabit,
        если создавать попытается не суперпользователь сервиса.
        """
        variants: tuple = (
            ({}, status.HTTP_401_UNAUTHORIZED, 'неавторизованным пользователем'),
            (superuser_token, status.HTTP_401_UNAUTHORIZED, 'суперпользователем'),
        )
        for token, status_code, text in variants:
            response = await client.get(URL.USER_ME, headers=token)
            assert response.status_code == status_code, (
                f'При попытке получить личные данные {text} '
                f'не было ответа cо статусом {status_code}:\n{response.text}'
            )
            result = response.json()
            assert 'detail' in result, 'В теле ответа с ошибкой нет ключа detail'


class TestPatchMeUser:
    """
    Тест изменения своих личных данных для пользователей сервиса Tabit.

    /api/v1/auth/me
    """

    @pytest.mark.asyncio
    @pytest.mark.parametrize(
        'payload',
        PAYLOAD_FOR_PATCH_USER,
    )
    async def test_patch_me_user(
        self,
        client: AsyncClient,
        moderator_token,
        employee_token,
        payload: dict[str, str],
    ):
        """Тесты на изменение личных данных для пользователей сервиса Tabit."""
        variants = (
            (moderator_token, MODERATOR_TELEGRAM, 'модератором от компании'),
            (employee_token, USER_TELEGRAM, 'сотрудником компании'),
        )
        for token, telegram, text in variants:
            payload['telegram_username'] = telegram
            response_get = await client.get(
                URL.USER_ME,
                headers=token,
            )
            data_before = response_get.json()
            response_patch = await client.patch(
                URL.USER_ME,
                json=payload,
                headers=token,
            )
            assert response_patch.status_code == status.HTTP_200_OK, (
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
    async def test_patch_me_user_same_telegram(
        self,
        client: AsyncClient,
        moderator_token,
        employee_token,
    ):
        """Тесты на появление пользователей с одинаковым Telegram"""
        payload = {'telegram_username': MODERATOR_TELEGRAM}
        await client.patch(
            URL.USER_ME,
            json=payload,
            headers=moderator_token,
        )
        response = await client.patch(
            URL.USER_ME,
            json=payload,
            headers=employee_token,
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST, (
            f'При попытке создать запись с дублированием Telegram-имени'
            f'не было ответа cо статусом {status.HTTP_400_BAD_REQUEST}:\n{response.text}'
        )


    @pytest.mark.asyncio
    async def test_patch_me_user_extra_fields(
        self,
        client: AsyncClient,
        moderator_token,
        employee_token,
    ):
        """
            Тесты на попытку вставить дополнительные поля 
        при изменении личных данных для пользователей сервиса Tabit.
        """
        variants = (
            (moderator_token, 'модератором от компании'),
            (employee_token, 'сотрудником компании'),
        )
        payload = PAYLOAD_FOR_PATCH_USER[0]
        for token, text in variants:
            for extra_key, extra_value in PAYLOAD_FOR_PATCH_USER_EXTRA.items():
                payload[extra_key] = extra_value
                response = await client.patch(
                    URL.USER_ME,
                    json=payload,
                    headers=token,
                )
                assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, (
                    f'Некорректный ответ на звпрос с дополнительным полями\n'
                    f'{payload}:\n{response.text}'
                )


    @pytest.mark.asyncio
    async def test_patch_me_user_not_access(
        self,
        client: AsyncClient,
        superuser_token,
    ):
        """
        Тест на ошибку при изменение личных данных для пользователя сервиса Tabit,
        если входить без токена или с токеном администратора сервиса.
        """
        payload: dict[str, str] = {'name': 'Киширика', 'surname': 'Киширису'}
        variants: tuple = (
            ({}, status.HTTP_401_UNAUTHORIZED, 'неавторизованным пользователем'),
            (superuser_token, status.HTTP_401_UNAUTHORIZED, 'суперпользователя'),
        )
        for token, status_code, text in variants:
            response = await client.patch(
                URL.USER_ME,
                json=payload,
                headers=token,
            )
            assert response.status_code == status_code, (
                f'При попытке изменить личные данные {text} '
                f'не было ответа cо статусом {status_code}:\n{response.text}'
            )
            result = response.json()
            assert 'detail' in result, 'В теле ответа с ошибкой нет ключа detail'


class TestForgotPasswordUser:
    """
    Тесты восстановление пароля пользователей сервиса Tabit.

    /api/v1/auth/forgot-password
    """

    # TODO: Написать тесты, когда конечная точка будет работать.


class TestForgotResetUser:
    """
    Тесты сброса пароля пользователей сервиса Tabit.

    /api/v1/auth/reset-password
    """

    # TODO: Написать тесты, когда конечная точка будет работать.
