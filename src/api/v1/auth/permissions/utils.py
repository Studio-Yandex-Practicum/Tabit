from typing import Any, TypeVar
from uuid import UUID

from fastapi import HTTPException, Request, status

from src.users.models.enum import CompanyRole, TabitRole

# Типы для аннотаций
UserType = TypeVar('UserType')
ResourceID = int | str | UUID
Context = dict[str, Any]


def get_tabit_role(user: Any) -> TabitRole | None:
    """
    Возвращает роль пользователя Tabit в виде enum TabitRole

    Тип: RBAC (вспомогательная функция)
    Роли: Tabit Superuser, Tabit Admin

    Параметры:
    - user: пользователь TabitAdminUser

    Возвращает:
    - TabitRole.SUPERUSER, если пользователь суперпользователь
    - TabitRole.ADMIN в противном случае
    """
    if not user:
        return None

    # Проверяем атрибут is_superuser
    if hasattr(user, 'is_superuser') and user.is_superuser:
        return TabitRole.SUPERUSER

    # Проверяем атрибут role, если есть
    if hasattr(user, 'role'):
        # Если role уже enum
        if isinstance(user.role, TabitRole):
            return user.role

        # Если role строка, пробуем преобразовать в enum
        if isinstance(user.role, str):
            if user.role == TabitRole.SUPERUSER.value:
                return TabitRole.SUPERUSER
            elif user.role == TabitRole.ADMIN.value:
                return TabitRole.ADMIN

    # По умолчанию - обычный админ
    return TabitRole.ADMIN


def get_company_role(user: Any) -> CompanyRole | None:
    """
    Возвращает роль пользователя компании в виде enum CompanyRole

    Тип: RBAC (вспомогательная функция)
    Роли: Company Moderator, Company User

    Параметры:
    - user: пользователь UserTabit

    Возвращает:
    - CompanyRole.MODERATOR или CompanyRole.USER в зависимости от роли
    - None, если роль неизвестна
    """
    if not user:
        return None

    # Проверяем атрибут role
    if hasattr(user, 'role'):
        # Если role уже enum
        if isinstance(user.role, CompanyRole):
            return user.role

        # Если role строка, пробуем преобразовать в enum
        if isinstance(user.role, str):
            if user.role == CompanyRole.MODERATOR.value:
                return CompanyRole.MODERATOR
            elif user.role == CompanyRole.USER.value:
                return CompanyRole.USER

    # По умолчанию - обычный пользователь
    return CompanyRole.USER


def get_user_from_args(args: tuple, kwargs: dict) -> Any:
    """
    Извлекает пользователя из аргументов функции

    Тип: Вспомогательная функция (не относится напрямую к RBAC/ABAC)

    Параметры:
    - args: позиционные аргументы
    - kwargs: именованные аргументы

    Возвращает:
    - Объект пользователя или None
    """
    # Сначала проверяем kwargs
    user = kwargs.get('user')
    if user:
        return user

    # Если нет в kwargs, проверяем args
    for arg in args:
        # Проверяем признаки объекта пользователя
        if hasattr(arg, 'id') or hasattr(arg, 'role') or hasattr(arg, 'is_superuser'):
            return arg

    return None


def get_context_from_request(request: Request, params: list[str] = None) -> dict[str, Any]:
    """
    Извлекает контекстные параметры из запроса

    Тип: Вспомогательная функция (используется для обоих типов RBAC/ABAC)

    Параметры:
    - request: объект запроса
    - params: список названий параметров, которые нужно извлечь

    Возвращает:
    - Словарь с извлеченными параметрами
    """
    if params is None:
        params = [
            'company_slug',
            'problem_id',
            'task_id',
            'thread_id',
            'comment_id',
            'meeting_id',
            'message_id',
            'voting_id',
        ]

    context = {}
    path_params = request.path_params

    for key in params:
        if key in path_params:
            context[key] = path_params[key]

    return context


def get_context_from_kwargs(kwargs: dict, params: list[str] = None) -> dict[str, Any]:
    """
    Извлекает контекстные параметры из именованных аргументов

    Тип: Вспомогательная функция (используется для обоих типов RBAC/ABAC)

    Параметры:
    - kwargs: именованные аргументы
    - params: список названий параметров, которые нужно извлечь

    Возвращает:
    - Словарь с извлеченными параметрами
    """
    if params is None:
        params = [
            'company_slug',
            'problem_id',
            'task_id',
            'thread_id',
            'comment_id',
            'meeting_id',
            'message_id',
            'voting_id',
        ]

    context = {}

    for key in params:
        if key in kwargs:
            context[key] = kwargs[key]

    return context


def identify_resource_from_context(context: dict[str, Any]) -> tuple[str | None, Any]:
    """
    Определяет тип и ID ресурса из контекста

    Тип: ABAC (вспомогательная функция)

    Параметры:
    - context: словарь с контекстными параметрами

    Возвращает:
    - Кортеж (тип ресурса, ID ресурса) или (None, None)
    """
    resource_mapping = {
        'task_id': 'task',
        'comment_id': 'comment',
        'problem_id': 'problem',
        'message_id': 'message',
        'voting_id': 'voting',
    }

    for param, resource_type in resource_mapping.items():
        if param in context:
            return resource_type, context[param]

    return None, None


def create_forbidden_exception(message: str = None) -> HTTPException:
    """
    Создает исключение для случая отсутствия прав доступа

    Тип: Вспомогательная функция (используется для обоих типов RBAC/ABAC)

    Параметры:
    - message: сообщение об ошибке

    Возвращает:
    - HTTPException с кодом 403
    """
    if message is None:
        message = 'Недостаточно прав для выполнения операции'

    return HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=message)


def create_unauthorized_exception(message: str = None) -> HTTPException:
    """
    Создает исключение для случая отсутствия аутентификации

    Тип: Вспомогательная функция (используется для обоих типов RBAC/ABAC)

    Параметры:
    - message: сообщение об ошибке

    Возвращает:
    - HTTPException с кодом 401
    """
    if message is None:
        message = 'Пользователь не аутентифицирован'

    return HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=message)


def create_bad_request_exception(message: str = None) -> HTTPException:
    """
    Создает исключение для случая некорректного запроса

    Тип: Вспомогательная функция (используется для обоих типов RBAC/ABAC)

    Параметры:
    - message: сообщение об ошибке

    Возвращает:
    - HTTPException с кодом 400
    """
    if message is None:
        message = 'Некорректный запрос'

    return HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)
