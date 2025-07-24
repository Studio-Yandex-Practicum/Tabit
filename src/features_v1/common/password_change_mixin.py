import logging
from http import HTTPStatus

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.database.db_depends import get_async_session
from src.schemas.password import ChangePasswordRequest

logger = logging.getLogger(__name__)


class PasswordChangeMixin:
    def create_change_route(
        self,
        router: APIRouter,
        crud,
        current_user_dependency,
        user_type_name: str,
        prefix: str = '',
    ):
        @router.post(
            f'{prefix}/change-password',
            dependencies=[Depends(current_user_dependency)],
            status_code=HTTPStatus.OK,
            summary=f'Смена пароля {user_type_name}',
            description=f'Смена пароля {user_type_name} при знании текущего пароля',
        )
        async def change_password(
            request: ChangePasswordRequest,
            current_user=Depends(current_user_dependency),
            session: AsyncSession = Depends(get_async_session),
        ) -> dict:
            try:
                is_valid = await crud.verify_password(
                    session, current_user.id, request.current_password
                )
                if not is_valid:
                    raise HTTPException(
                        status_code=HTTPStatus.BAD_REQUEST, detail='Неверный текущий пароль'
                    )
                success = await crud.change_password(
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
