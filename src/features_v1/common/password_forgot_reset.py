import logging
from http import HTTPStatus
from typing import Any, Callable, Generic, TypeVar
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth.dependencies import current_superuser
from src.core.database.db_depends import get_async_session
from src.features_v1.constants import MiscConstants

T = TypeVar('T')

# Настройка логгера
logger = logging.getLogger(__name__)


class ForgotPasswordRequest(BaseModel):
    """Схема для запроса восстановления пароля"""

    email: str


class ResetPasswordRequest(BaseModel):
    """Схема для сброса пароля"""

    token: str
    new_password: str


class ForceResetPasswordRequest(BaseModel):
    """Схема для принудительного сброса пароля"""

    new_password: str


class ChangePasswordRequest(BaseModel):
    """Схема для смены пароля"""

    current_password: str
    new_password: str


class PasswordForgotResetMixin(Generic[T]):
    """Миксин для восстановления и сброса пароля"""

    def __init__(
        self,
        crud_instance: Any,
        user_model: type,
        current_user_dependency: Callable,
        user_type_name: str = 'пользователя',
    ):
        self.crud = crud_instance
        self.user_model = user_model
        self.current_user_dependency = current_user_dependency
        self.user_type_name = user_type_name

    def create_password_forgot_reset_routes(self, router: APIRouter, prefix: str = ''):
        """Создает роуты для восстановления и сброса пароля"""

        @router.post(
            f'{prefix}/forgot-password',
            status_code=HTTPStatus.OK,
            summary=f'Запрос на восстановление пароля {self.user_type_name}',
            description=(
                f'Отправляет email с токеном для восстановления пароля {self.user_type_name}'
            ),
        )
        async def forgot_password(
            request: ForgotPasswordRequest,
            session: AsyncSession = Depends(get_async_session),
        ) -> dict:
            """Запрос на восстановление пароля"""
            try:
                # Проверяем существование пользователя
                user = await self.crud.get_by_email(session, request.email)
                if not user:
                    raise HTTPException(
                        status_code=HTTPStatus.NOT_FOUND,
                        detail=f'{self.user_type_name.capitalize()} с таким email не найден',
                    )

                # Генерируем токен восстановления
                reset_token = await self.crud.create_password_reset_token(session, request.email)

                # Отправляем email с токеном
                await self._send_reset_email(request.email, reset_token)

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

        @router.post(
            f'{prefix}/reset-password',
            status_code=HTTPStatus.OK,
            summary=f'Сброс пароля {self.user_type_name} с токеном',
            description=f'Сброс пароля {self.user_type_name} с использованием токена из email',
            #            openapi_extra=MiscConstants.OPENAPI_EXTRA_ADMIN_AUTH,
        )
        async def reset_password(
            request: ResetPasswordRequest,
            session: AsyncSession = Depends(get_async_session),
        ) -> dict:
            """Сброс пароля с токеном"""
            try:
                # Проверяем токен
                if not await self.crud.verify_reset_token(session, request.token):
                    raise HTTPException(
                        status_code=HTTPStatus.BAD_REQUEST,
                        detail='Недействительный или истекший токен',
                    )

                # Сбрасываем пароль
                success = await self.crud.reset_password_with_token(
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
            summary=f'Принудительный сброс пароля {self.user_type_name}',
            description=f'Сброс пароля {self.user_type_name} суперпользователем',
            openapi_extra=MiscConstants.OPENAPI_EXTRA_ADMIN_AUTH,
        )
        async def force_reset_password(
            user_id: UUID,
            request: ForceResetPasswordRequest,
            session: AsyncSession = Depends(get_async_session),
        ) -> dict:
            """Принудительный сброс пароля"""
            try:
                # Принудительно сбрасываем пароль
                success = await self.crud.reset_password_by_admin(
                    session, user_id, request.new_password
                )

                if not success:
                    raise HTTPException(
                        status_code=HTTPStatus.BAD_REQUEST, detail='Не удалось сбросить пароль'
                    )

                return {
                    'message': f'Пароль {self.user_type_name} успешно сброшен',
                    'status': 'success',
                }

            except HTTPException:
                raise
            except Exception as e:
                raise HTTPException(
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    detail=f'Ошибка при принудительном сбросе пароля: {str(e)}',
                ) from e

        @router.get(
            f'{prefix}/verify-reset-token/{{token}}',
            status_code=HTTPStatus.OK,
            summary='Проверка токена восстановления пароля',
            description='Проверяет валидность токена для восстановления пароля',
        )
        async def verify_reset_token(
            token: str,
            session: AsyncSession = Depends(get_async_session),
        ) -> dict:
            """Проверка токена восстановления пароля"""
            try:
                is_valid = await self.crud.verify_reset_token(session, token)

                return {
                    'is_valid': is_valid,
                    'message': (
                        'Токен действителен' if is_valid else 'Токен недействителен или истек'
                    ),
                    'status': 'success',
                }

            except Exception as e:
                raise HTTPException(
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    detail=f'Ошибка при проверке токена: {str(e)}',
                ) from e

        @router.post(
            f'{prefix}/change-password',
            dependencies=[Depends(self.current_user_dependency)],
            status_code=HTTPStatus.OK,
            summary=f'Смена пароля {self.user_type_name}',
            description=f'Смена пароля {self.user_type_name} при знании текущего пароля',
            openapi_extra=MiscConstants.OPENAPI_EXTRA_ADMIN_AUTH,
        )
        async def change_password(
            request: ChangePasswordRequest,
            current_user=Depends(self.current_user_dependency),
            session: AsyncSession = Depends(get_async_session),
        ) -> dict:
            """Смена пароля пользователем"""
            try:
                is_valid = await self.crud.verify_password(
                    session, current_user.id, request.current_password
                )
                if not is_valid:
                    raise HTTPException(
                        status_code=HTTPStatus.BAD_REQUEST, detail='Неверный текущий пароль'
                    )
                success = await self.crud.change_password(
                    session, current_user.id, request.new_password
                )
                if not success:
                    raise HTTPException(
                        status_code=HTTPStatus.BAD_REQUEST, detail='Не удалось изменить пароль'
                    )
                return {'message': 'Пароль успешно изменен', 'status': 'success'}
            except HTTPException:
                logger.debug('HTTPException перехвачена и перебрасывается')
                raise
            except Exception as e:
                logger.error(f'Неожиданная ошибка при смене пароля: {e}')
                logger.error(f'Тип ошибки: {type(e)}')
                import traceback

                logger.error(f'Traceback: {traceback.format_exc()}')
                raise HTTPException(
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    detail=f'Ошибка при смене пароля: {str(e)}',
                ) from e

    async def _send_reset_email(self, email: str, token: str) -> None:
        """Отправка email с токеном восстановления пароля"""
        try:
            logger.info(f'Попытка отправки email на {email} с токеном {token}')

            # Временно закомментируем отправку email
            # Создаем схему email
            # email_data = EmailSchema(
            #     email_to=email,
            #     subject="Восстановление пароля",
            #     body=f"""
            #     <h2>Восстановление пароля</h2>
            #     <p>Для восстановления пароля перейдите по ссылке:</p>
            #     <p><a href="https://tabit.website/reset-password?token={token}">
            #         Восстановить пароль
            #     </a></p>
            #     <p>Или используйте токен: {token}</p>
            #     <p>Токен действителен 24 часа.</p>
            #     """
            # )

            # Отправляем email
            # await send_email(email_data)
            logger.info(f'Email успешно отправлен на {email}')

        except Exception as e:
            logger.error(f'Ошибка отправки email: {e}')
            # В продакшене здесь должно быть логирование


# TODO: реализовать отправку email в  src.services.email_service.send_email
# TODO: реализовать на фронте проверку токена после перехода
#       пользователя по ссылке из email.
#  Если токен не валидный, то перенаправлять на страницу с ошибкой.
#  Если токен валидный, то перенаправлять на страницу с формой смены пароля.
#  Если пароль успешно изменен, то перенаправлять на страницу с успешным изменением пароля.
#  Если пароль не изменен, то перенаправлять на страницу с ошибкой.

# =====================================================================┐
