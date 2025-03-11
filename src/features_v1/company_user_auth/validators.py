"""
Валидаторы для эндпоинтов.
"""

from http import HTTPStatus

from fastapi import HTTPException

from src.features_v1.company_user_auth.constants import TextError


def check_user_is_active(user):
    """Проверит, что пользователь передан и является активным. Иначе ошибка 400."""
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=TextError.LOGIN,
        )
