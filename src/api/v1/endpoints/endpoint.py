from fastapi import APIRouter, Depends
from src.api.v1.dependencies import current_superuser, fastapi_users


router = APIRouter()


@router.get('/')
async def main_page() -> str:
    """
    Представление главной страницы сайта

    Пока здесь ничего нет - в работе...
    """
    return 'Main page'


superuser_router = APIRouter(prefix='/admin', tags=['superuser'])


@superuser_router.get('/dashboard', dependencies=[Depends(current_superuser)])
async def admin_dashboard():
    """
    Эндпоинт панели управления для суперпользователей
    """
    return {'message': 'Для суперюзера'}


@superuser_router.get('/users', dependencies=[Depends(current_superuser)])
async def list_all_users():
    """
    Список всех пользователей для суперпользователя
    """
    users = await fastapi_users.get_all_users()
    return users


user_router = APIRouter(prefix='/user', tags=['user'])


@user_router.get(
    '/profile', dependencies=[Depends(fastapi_users.current_user(active=True))]
)
async def get_user_profile():
    """
    Получение профиля текущего пользователя
    """
    return {'message': 'Ваш профиль'}
