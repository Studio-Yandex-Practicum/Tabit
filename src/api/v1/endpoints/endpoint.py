from fastapi import APIRouter, Depends
from src.api.v1.dependencies import current_superuser, fastapi_users
from src.logger import logger

main_router = APIRouter()


@main_router.get('/')
async def main_page() -> str:
    """
    Представление главной страницы сайта
    """
    logger.info('Main Page')
    return 'Main page'


superuser_router = APIRouter(prefix='/superuser', tags=['superuser'])


@superuser_router.get('/dashboard', dependencies=[Depends(current_superuser)])
async def superuser_dashboard():
    """
    Эндпоинт панели управления для суперпользователей
    """
    return {'message': 'Для суперпользователя'}


@superuser_router.get('/users', dependencies=[Depends(current_superuser)])
async def list_all_users():
    """
    Список всех пользователей для суперпользователя
    """
    users = await fastapi_users.get_all_users()
    return users


admin_router = APIRouter(prefix='/admin', tags=['admin'])


@admin_router.get('/profile', dependencies=[Depends(fastapi_users.current_user(active=True))])
async def get_admin_profile():
    """
    Получение профиля текущего администратора
    """
    return {'message': 'Профиль администратора'}
