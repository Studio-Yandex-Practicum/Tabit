import logging
from http import HTTPStatus
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth.dependencies import current_superuser
from src.core.database.db_depends import get_async_session
from src.schemas.password import ForceResetPasswordRequest, ResetPasswordRequest

logger = logging.getLogger(__name__)


class PasswordResetMixin:
    def create_reset_routes(self, router: APIRouter, crud, user_type_name: str, prefix: str = ''):
        @router.post(
            f'{prefix}/reset-password',
            status_code=HTTPStatus.OK,
            summary=f'Сброс пароля {user_type_name} с токеном',
            description=f'Сброс пароля {user_type_name} с использованием токена из email',
        )
        async def reset_password(
            request: ResetPasswordRequest,
            session: AsyncSession = Depends(get_async_session),
        ) -> dict:
            try:
                if not await crud.verify_reset_token(session, request.token):
                    raise HTTPException(
                        status_code=HTTPStatus.BAD_REQUEST,
                        detail='Недействительный или истекший токен',
                    )
                success = await crud.reset_password_with_token(
                    session, request.token, request.new_password
                )
                if not success:
                    raise HTTPException(
                        status_code=HTTPStatus.BAD_REQUEST, detail='Не удалось сбросить пароль'
                    )
                return {'message': 'Пароль успешно изменен', 'status': 'success'}
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    detail=f'Ошибка при сбросе пароля: {str(e)}',
                ) from e

        @router.post(
            f'{prefix}/{{user_id}}/force-reset-password',
            dependencies=[Depends(current_superuser)],
            status_code=HTTPStatus.OK,
            summary=f'Принудительный сброс пароля {user_type_name}',
            description=f'Сброс пароля {user_type_name} суперпользователем',
        )
        async def force_reset_password(
            user_id: UUID,
            request: ForceResetPasswordRequest,
            session: AsyncSession = Depends(get_async_session),
        ) -> dict:
            try:
                success = await crud.reset_password_by_admin(
                    session, user_id, request.new_password
                )
                if not success:
                    raise HTTPException(
                        status_code=HTTPStatus.BAD_REQUEST, detail='Не удалось сбросить пароль'
                    )
                return {
                    'message': f'Пароль {user_type_name} успешно сброшен',
                    'status': 'success',
                }
            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    detail=f'Ошибка при принудительном сбросе пароля: {str(e)}',
                ) from e
