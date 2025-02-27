from http import HTTPStatus

import pytest
from httpx import AsyncClient

from tests.constants import (
    GOOD_PASSWORD,
    URL,
)


class TestLoginUser:
    """
    Тесты на вход в систему пользователей сервиса Tabit.

    /api/v1/auth/login
    """

    @pytest.mark.asyncio
    async def test_login_user(self, client: AsyncClient, moderator_1_company_1, user_1_company_1):
        """Тест на вход в систему пользователей сервиса с валидными данными."""
        variants = (
            (moderator_1_company_1, 'модератора от компании'),
            (user_1_company_1, 'пользователя от компании'),
        )
        for user, text in variants:
            login_payload = {'username': user.email, 'password': GOOD_PASSWORD}
            response = await client.post(URL.USER_LOGIN, data=login_payload)
            assert (
                response.status_code == HTTPStatus.OK
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
                response.status_code == HTTPStatus.BAD_REQUEST
            ), f'При авторизации {text} у ответа должен быть статус 400:\n{response.text}'
            result = response.json()
            assert 'detail' in result, 'В теле ответа с ошибкой нет ключа detail'

    @pytest.mark.asyncio
    async def test_login_user_invalid(self, client: AsyncClient, user_1_company_1):
        """
        Тест на вход в систему пользователей сервиса без заполнения обязательных полей формы.
        """
        bad_login_payloads: tuple[dict, ...] = (
            {'password': GOOD_PASSWORD},
            {
                'username': user_1_company_1.email,
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
    async def test_login_user_bad_password(self, client: AsyncClient, user_1_company_1):
        """Тест на вход в систему пользователей сервиса под неверным паролем."""
        login_payload = {'username': user_1_company_1.email, 'password': f'NOT {GOOD_PASSWORD}'}
        response = await client.post(URL.ADMIN_LOGIN, data=login_payload)
        assert (
            response.status_code == HTTPStatus.BAD_REQUEST
        ), f'Не корректный ответ с данными\n{login_payload}\n{response.text}'
        result = response.json()
        assert 'detail' in result, 'В теле ответа с ошибкой нет ключа detail'


class TestLogoutUser:
    """
    Тесты на выход из системы пользователей сервиса Tabit.

    /api/v1/auth/logout
    """

    @pytest.mark.asyncio
    async def test_logout_user(
        self, client: AsyncClient, moderator_1_company_1_token, user_1_company_1_token
    ):
        """Тест на выход из системы пользователей сервиса."""
        variants = (
            (moderator_1_company_1_token, 'модератора от компании'),
            (user_1_company_1_token, 'пользователя от компании'),
        )
        for token, text in variants:
            response = await client.post(URL.USER_LOGOUT, headers=token)
            assert (
                response.status_code == HTTPStatus.NO_CONTENT
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
                response.status_code == HTTPStatus.UNAUTHORIZED
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
        moderator_company_refresh_token,
        user_company_refresh_token,
    ):
        """Тест получения нового токена по refresh-token для пользователя сервиса Tabit."""
        variants = (
            (moderator_company_refresh_token, 'модератором от компании'),
            (user_company_refresh_token, 'пользователем от компании'),
        )
        for token, text in variants:
            response = await client.post(URL.USER_REFRESH, headers=token)
            assert (
                response.status_code == HTTPStatus.OK
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
            assert response.status_code == HTTPStatus.UNAUTHORIZED, (
                f'При попытке получения токена {text} у ответа должен быть статус 401:\n'
                f'{response.text}'
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
