from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.auth.jwt import jwt_auth_backend
from src.api.v1.auth.managers import tabit_admin, tabit_users
from src.database.db_depends import get_async_session
from src.tabit_management.schemas import AdminCreateSchema, AdminReadSchema, AdminUpdateSchema
from src.tabit_management.crud import admin_crud

router = APIRouter()


@router.get(
    '/',
    # TODO Уточнить целесообразность ручки
    # summary='',
)
async def get_tabit_admin(session: AsyncSession = Depends(get_async_session)):
    """Возвращает список администраторов."""

    return {'message': 'Здесь будет какая-то информация.'}


@router.post(
    '/refresh-token',
    summary='Обновить токен',
)
async def refresh_token_tabit_admin(session: AsyncSession = Depends(get_async_session)):
    """Эндпоинт для обновления токена JWT."""

    return {
        'access_token': 'новый токен доступа',
        'refresh_token': 'новый токен обновления',
    }


router.include_router(
    tabit_admin.get_auth_router(jwt_auth_backend),
    prefix='',
)

router.include_router(
    tabit_admin.get_reset_password_router(),
    prefix='',
)
router.include_router(
    tabit_admin.get_users_router(
        user_schema=AdminReadSchema,
        user_update_schema=AdminUpdateSchema,
    ),
    prefix='',
)
# TODO: Для тестирования работы БД сойдет, а вообще нужно создать отдельную ручку для создания
# модератора, с ограниченным доступом.
router.include_router(
    tabit_admin.get_register_router(
        user_schema=AdminReadSchema,
        user_create_schema=AdminCreateSchema,
    ),
    prefix='',
)
