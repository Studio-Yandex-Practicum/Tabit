import functools
from typing import Callable, ParamSpec, TypeVar, cast

from src.api.v1.auth.permissions.abac import get_ownership_service
from src.api.v1.auth.permissions.rbac import CompanyRBAC, TabitAdminRBAC
from src.api.v1.auth.permissions.utils import (
    create_forbidden_exception,
    create_unauthorized_exception,
    get_company_role,
    get_context_from_kwargs,
    get_tabit_role,
    get_user_from_args,
    identify_resource_from_context,
)
from src.users.models.enum import CompanyRole

# Типы для аннотаций
P = ParamSpec('P')
R = TypeVar('R')


def tabit_permission_required(endpoint: str, method: str):
    """
    Декоратор для проверки прав доступа администраторов Tabit

    Тип: RBAC
    Роли: Tabit Superuser, Tabit Admin

    Проверяет наличие доступа на основе роли пользователя в системе Tabit.
    Superuser имеет доступ ко всем эндпоинтам, Admin имеет ограниченный доступ
    согласно настройкам TabitAdminRBAC.

    Пример использования:
    ```
    @router.get('/admin/')
    @tabit_permission_required('/admin/', 'GET')
    async def get_admin_dashboard(user=Depends(current_tabit_admin)):
        return {'status': 'success'}
    ```
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # Получаем пользователя из аргументов
            user = get_user_from_args(args, kwargs)

            if not user:
                raise create_unauthorized_exception()

            # Определяем роль пользователя
            role = get_tabit_role(user)

            # Проверяем права доступа
            rbac = TabitAdminRBAC(role)
            if not rbac.has_permission(endpoint, method):
                raise create_forbidden_exception(
                    f'Недостаточно прав для доступа к {method} {endpoint}'
                )

            return await func(*args, **kwargs)

        return cast(Callable[P, R], wrapper)

    return decorator


def company_permission_required(endpoint: str, method: str, check_ownership: bool = False):
    """
    Декоратор для проверки прав доступа пользователей компании

    Тип: Комбинированный (RBAC + ABAC при check_ownership=True)
    Роли: Company Moderator, Company User

    Проверяет наличие доступа на основе роли пользователя в компании.
    Company Moderator имеет расширенные права, Company User имеет базовые права.
    При check_ownership=True также проверяет владение ресурсом (ABAC) для обычных пользователей.

    Пример использования:
    ```
    @router.get('/{company_slug}/problems/')
    @company_permission_required('/{company_slug}/problems/', 'GET')
    async def get_company_problems(company_slug: str, user=Depends(current_company_user)):
        return {'status': 'success', 'company_slug': company_slug}
    ```

    Параметры:
    - endpoint: шаблон эндпоинта с возможными параметрами
    - method: HTTP метод
    - check_ownership: если True, будет проверять владение ресурсом (ABAC)
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # Получаем пользователя из аргументов
            user = get_user_from_args(args, kwargs)

            if not user:
                raise create_unauthorized_exception()

            # Определяем роль пользователя
            role = get_company_role(user)

            # Собираем контекст для проверки прав
            context = get_context_from_kwargs(kwargs)

            # Проверяем права доступа (RBAC)
            rbac = CompanyRBAC(role, **context)
            if not rbac.has_permission(endpoint, method, **context):
                raise create_forbidden_exception(
                    f'Недостаточно прав для доступа к {method} {endpoint}'
                )

            # Если нужно проверить владение ресурсом (ABAC) и пользователь не модератор
            if check_ownership and role == CompanyRole.USER:
                # Определяем тип и ID ресурса из контекста
                resource_type, resource_id = identify_resource_from_context(context)

                # Проверяем владение ресурсом, если тип и ID определены
                if resource_type and resource_id:
                    # Получаем сервис для проверки владения ресурсами
                    ownership_service = get_ownership_service()

                    # Для обычных пользователей проверяем владение ресурсом через ABAC-компонент
                    if not await ownership_service.check_resource_ownership(
                        resource_type=resource_type,
                        resource_id=resource_id,
                        user_id=getattr(user, 'id', None),
                    ):
                        raise create_forbidden_exception(
                            'У вас нет прав для управления этим ресурсом'
                        )

            return await func(*args, **kwargs)

        return cast(Callable[P, R], wrapper)

    return decorator


def permission_required(
    endpoint: str, method: str, admin_only: bool = False, check_ownership: bool = False
):
    """
    Универсальный декоратор для проверки прав доступа

    Тип: Комбинированный (RBAC + ABAC при check_ownership=True)
    Роли: Tabit Superuser, Tabit Admin, Company Moderator, Company User

    Универсальный декоратор, который определяет тип пользователя (админ Tabit или
    пользователь компании) и применяет соответствующую логику проверки прав.
    При admin_only=True доступ разрешен только администраторам Tabit.
    При check_ownership=True проверяется владение ресурсом для обычных пользователей компании.

    Пример использования:
    ```
    @router.get('/some/endpoint')
    @permission_required('/some/endpoint', 'GET')
    async def some_handler(request: Request, user=Depends(current_company_user)):
        return {'status': 'success'}
    ```

    Параметры:
    - endpoint: шаблон эндпоинта
    - method: HTTP метод
    - admin_only: если True, то доступ разрешен только администраторам Tabit
    - check_ownership: если True, будет проверять владение ресурсом (для пользователей компаний)
    """

    def decorator(func: Callable[P, R]) -> Callable[P, R]:
        # Предварительное создание декораторов для их последующего использования
        tabit_decorator = tabit_permission_required(endpoint, method)
        company_decorator = company_permission_required(endpoint, method, check_ownership)

        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            # Получаем пользователя из аргументов
            user = get_user_from_args(args, kwargs)

            if not user:
                raise create_unauthorized_exception()

            # Проверяем, является ли пользователь администратором Tabit
            is_tabit_admin = admin_only or hasattr(user, 'is_superuser')

            # Применяем соответствующий декоратор
            if is_tabit_admin:
                # Создаем обертку для декоратора tabit_permission_required
                return await tabit_decorator(func)(*args, **kwargs)
            else:
                # Создаем обертку для декоратора company_permission_required
                return await company_decorator(func)(*args, **kwargs)

        return cast(Callable[P, R], wrapper)

    return decorator
