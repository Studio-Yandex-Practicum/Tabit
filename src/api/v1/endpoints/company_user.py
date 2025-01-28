from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.dependencies import get_async_session


router = APIRouter()


@router.get('/{company_slug}/{uuid}/', response_model=dict)
def get_company_user(company_slug: str, uuid: str, session: AsyncSession = Depends(get_async_session)):
    """
    Личный кабинет пользователя.
    """
    # TODO: Реализовать получение информации о пользователе из базы данных.
    return {'message': f'Личный кабинет пользователя компании {company_slug}, ID {uuid}'}


@router.patch('/{company_slug}/{uuid}/', response_model=dict)
def patch_company_user(company_slug: str, uuid: str, session: AsyncSession = Depends(get_async_session)):
    """
    Редактирование профиля.
    """
    # TODO: Реализовать обновление данных пользователя в базе данных.
    return {'message': f'Профиль пользователя обновлен для компании {company_slug}, ID {uuid}'}


@router.post('/{company_slug}/feedback/', response_model=dict)
def post_feedback(company_slug: str, session: AsyncSession = Depends(get_async_session)):
    """
    Задать вопрос в разделе 'Помощь'.
    """
    # TODO: Реализовать сохранение данных обратной связи в базу данных.
    return {'message': f'Обратная связь отправлена для компании {company_slug}'}
