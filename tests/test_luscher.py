import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import load_only, selectinload

from src.models import CompanyUser, SurveyCycleForUser
from src.models.enum import LuschersColorEnum
from tests.constants import UrlConstants


@pytest.mark.asyncio
class TestLuscherResultsForAuthenticatedUsers:
    """Тесты GET-запросов для получения результатов теста Люшера."""

    async def test_get_luscher_results(
        self,
        async_session,
        client: AsyncClient,
        survey_cycle_for_user_for_test,
        luscher_color_first,
        luscher_color_second,
        get_token_for_user,
    ):
        """
        Тест успешного получения результата теста Люшера для аутентифицированного пользователя.

        Проверяет:
        1. Успешный статус ответа (200 OK)
        2. Корректность формата ответа (словарь)
        3. Наличие ключа 'result' в ответе
        4. Соответствие текста результата одной из ожидаемых комбинаций Люшера
        """
        cycle_for_user, user, _ = await survey_cycle_for_user_for_test(return_related=True)

        user = await async_session.get(type(user), user.id)
        await luscher_color_second({'survey_cycle_for_user_id': cycle_for_user.id})
        token = await get_token_for_user(user)

        result = await async_session.execute(
            select(CompanyUser)
            .options(selectinload(CompanyUser.company))
            .where(CompanyUser.id == user.id)
        )

        user = result.scalars().first()
        company_slug = user.company.slug

        url = UrlConstants.LUSCHER_CREATE_RESULT.format(
            company_slug=company_slug,
            cycle_company_id=cycle_for_user.survey_cycle_for_company_id,
            cycle_user_id=cycle_for_user.id,
        )

        response = await client.get(url, headers=token)
        assert response.status_code == status.HTTP_200_OK
        response_json = response.json()
        assert isinstance(response_json, dict)
        assert 'result' in response_json
        result_text = response_json['result'].lower()
        from src.business_logic.luscher import get_combination

        combinations = await get_combination()
        assert any(value.lower() in result_text for value in combinations.values())


@pytest.mark.asyncio
class TestLuscherResultsForUnauthenticatedUsers:
    """Тесты GET-запросов для получения результатов теста Люшера."""

    async def test_get_luscher_results_unauthorized(
        self,
        async_session,
        client: AsyncClient,
        survey_cycle_for_user_for_test,
        luscher_color_first,
    ):
        """
        Тест запрета доступа к результатам теста Люшера для неавторизованных пользователей.

        Проверяет:
        1. Попытка получения результатов без токена авторизации
        2. Возвращается статус 401 Unauthorized
        """
        cycle_for_user, user, _ = await survey_cycle_for_user_for_test(return_related=True)

        await luscher_color_first({'survey_cycle_for_user_id': cycle_for_user.id})

        result = await async_session.execute(
            select(CompanyUser)
            .options(selectinload(CompanyUser.company))
            .where(CompanyUser.id == user.id)
        )
        user = result.scalars().first()

        url = UrlConstants.LUSCHER_CREATE_RESULT.format(
            company_slug=user.company.slug,
            cycle_company_id=cycle_for_user.survey_cycle_for_company_id,
            cycle_user_id=cycle_for_user.id,
        )

        response = await client.get(url)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED


@pytest.mark.asyncio
async def test_create_luscher_result(
    async_session: AsyncSession,
    client: AsyncClient,
    get_token_for_user,
    survey_cycle_for_user_for_test,
):
    """
    Тест успешного создания результата теста Люшера.

    Проверяет:
    1. Успешный статус ответа (201 Created)
    2. Корректное сохранение и возвращение данных (проверка selection_1)
    3. Работа эндпоинта с корректным токеном и валидным payload
    """
    cycle_for_user, user, _ = await survey_cycle_for_user_for_test(return_related=True)

    async with async_session as session:
        result = await session.execute(
            select(CompanyUser)
            .options(
                selectinload(CompanyUser.company), load_only(CompanyUser.id, CompanyUser.email)
            )
            .where(CompanyUser.id == user.id)
        )
        user = result.scalar_one()

    token = await get_token_for_user(user)
    company_slug = user.company.slug

    url = (
        f'/api/v1/{company_slug}/surveys/cycle/'
        f'{cycle_for_user.survey_cycle_for_company_id}/{cycle_for_user.id}/luscher_first'
    )

    payload = {
        'selection_1': LuschersColorEnum.Blue.value,
        'selection_2': LuschersColorEnum.Green.value,
        'selection_3': LuschersColorEnum.Red.value,
        'selection_4': LuschersColorEnum.Yellow.value,
        'selection_5': LuschersColorEnum.Violet.value,
        'selection_6': LuschersColorEnum.Brown.value,
        'selection_7': LuschersColorEnum.Black.value,
        'selection_8': LuschersColorEnum.Grey.value,
    }

    response = await client.post(url, headers=token, json=payload)

    if response.status_code != status.HTTP_201_CREATED:
        print('Response status:', response.status_code)
        print('Response body:', response.json())

    assert response.status_code == status.HTTP_201_CREATED
    response_data = response.json()
    assert response_data['selection_1'] == payload['selection_1']


@pytest.mark.asyncio
async def test_create_luscher_result_invalid_data(
    async_session: AsyncSession,
    client: AsyncClient,
    get_token_for_user,
    survey_cycle_for_user_for_test,
):
    """
    Тест создания результата теста Люшера с некорректными данными.

    Проверяет:
    1. Возвращение ошибки валидации (422 Unprocessable Entity) при отправке неправильных данных
    2. Корректную обработку ошибок на уровне валидации Pydantic / FastAPI
    """

    cycle_for_user, user, _ = await survey_cycle_for_user_for_test(return_related=True)

    async with async_session as session:
        user = await session.scalar(
            select(CompanyUser)
            .options(selectinload(CompanyUser.company))
            .where(CompanyUser.id == user.id)
        )

        cycle_for_user = await session.scalar(
            select(SurveyCycleForUser).where(SurveyCycleForUser.id == cycle_for_user.id)
        )

    token = await get_token_for_user(user)

    url = (
        f'/api/v1/{user.company.slug}/surveys/cycle/'
        f'{cycle_for_user.survey_cycle_for_company_id}/{cycle_for_user.id}/luscher_first'
    )

    payload = {
        'selection_1': LuschersColorEnum.Blue.value,
        'selection_2': LuschersColorEnum.Green.value,
        'selection_3': LuschersColorEnum.Red.value,
        'selection_4': LuschersColorEnum.Yellow.value,
        'selection_5': LuschersColorEnum.Violet.value,
        'selection_6': LuschersColorEnum.Brown.value,
        'selection_7': LuschersColorEnum.Black.value,
    }

    response = await client.post(url, headers=token, json=payload)

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY, (
        f'Ожидается status_code {status.HTTP_422_UNPROCESSABLE_ENTITY}, '
        f'получен {response.status_code}. '
        f'Тело ответа: {response.json()}'
    )
