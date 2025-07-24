import logging
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.db_depends import get_async_session
from src.schemas.password import ForgotPasswordRequest

logger = logging.getLogger(__name__)


class PasswordForgotMixin:
    def create_forgot_route(self, router: APIRouter, crud, user_type_name: str, prefix: str = ''):
        @router.post(
            f'{prefix}/forgot-password',
            status_code=HTTPStatus.OK,
            summary=f'Запрос на восстановление пароля {user_type_name}',
            description=f'Отправляет email с токеном для восстановления пароля {user_type_name}',
        )
        async def forgot_password(
            request: ForgotPasswordRequest,
            session: AsyncSession = Depends(get_async_session),
        ) -> dict:
            try:
                user = await crud.get_by_email(session, request.email)
                if not user:
                    raise HTTPException(
                        status_code=HTTPStatus.NOT_FOUND,
                        detail=f'{user_type_name.capitalize()} с таким email не найден',
                    )
                reset_token = await crud.create_password_reset_token(session, request.email)
                logger.info(f'reset_token: {reset_token}')
                # ===============================================
                # Раскомментировать для отправки email
                # await self._send_reset_email(request.email, reset_token)
                # ===============================================
                logger.info(f'Email успешно отправлен на {request.email}')
                return {
                    'message': (
                        f'Инструкции по восстановлению пароля отправлены на email {request.email}'
                    ),
                    'status': 'success',
                }
            except Exception as e:
                raise HTTPException(
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    detail=f'Ошибка при обработке запроса восстановления пароля: {str(e)}',
                ) from e
