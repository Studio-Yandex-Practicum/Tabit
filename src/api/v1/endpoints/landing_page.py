from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.dependencies import get_async_session


router = APIRouter()


@router.get('/auth/info/', response_model=dict)
def get_auth_info(session: AsyncSession = Depends(get_async_session)):
    """
    Получение цены, контактов и т.д. для landing page.
    """
    # TODO: Подключить получение динамических данных.
    return {'message': 'Информация для landing page'}


@router.post('/auth/demo/', response_model=dict)
def post_auth_demo(session: AsyncSession = Depends(get_async_session)):
    """
    Получить демо из формы landing page.
    """
    # TODO: Реализовать сохранение данных формы в базу данных для аналитики или обратной связи.
    return {'message': 'Форма демо отправлена'}
