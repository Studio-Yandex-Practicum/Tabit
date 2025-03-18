from typing import Any, Awaitable, Callable, TypeVar

from fastapi import Depends, Request

from src.api.v1.auth.dependencies import (
    current_company_moderator,
    current_company_user,
    current_tabit_admin,
    current_tabit_superuser,
)
from src.api.v1.auth.permissions.abac import ResourceOwnershipService, get_ownership_service
from src.api.v1.auth.permissions.rbac import CompanyRBAC, TabitAdminRBAC
from src.api.v1.auth.permissions.utils import (
    create_bad_request_exception,
    create_forbidden_exception,
    get_company_role,
    get_context_from_request,
    get_tabit_role,
    identify_resource_from_context,
)
from src.users.models.enum import CompanyRole

# Типы для зависимостей
UserType = TypeVar('UserType')
DependencyFunc = Callable[..., Any]
AsyncDependencyFunc = Callable[..., Awaitable[Any]]


def require_tabit_permission(endpoint: str, method: str) -> DependencyFunc:
    """
    Зависимость для проверки прав доступа администраторов Tabit (RBAC компонент)

    Тип: RBAC
    Роли: Tabit Superuser, Tabit Admin

    Проверяет наличие доступа на основе роли пользователя в системе Tabit.
    Superuser имеет доступ ко всем эндпоинтам, Admin имеет ограниченный доступ
    согласно настройкам TabitAdminRBAC.

    Пример использования:
    ```
    @router.get('/admin/')
    async def get_admin_dashboard(
        permission=Depends(require_tabit_permission('/admin/', 'GET')),
        user=Depends(current_tabit_admin)
    ):
        return {'status': 'success'}
    ```
    """

    def dependency(user=Depends(current_tabit_admin)) -> bool:
        # Определяем роль пользователя
        role = get_tabit_role(user)

        # Проверяем права доступа
        rbac = TabitAdminRBAC(role)
        if not rbac.has_permission(endpoint, method):
            raise create_forbidden_exception(
                f'Недостаточно прав для доступа к {method} {endpoint}'
            )
        return True

    return dependency


def require_company_permission(
    endpoint: str,
    method: str,
    check_ownership: bool = False,
    company_slug_param: str = 'company_slug',
) -> AsyncDependencyFunc:
    """
    Зависимость для проверки прав доступа пользователей компаний

    Тип: Комбинированный (RBAC + ABAC при check_ownership=True)
    Роли: Company Moderator, Company User

    Проверяет наличие доступа на основе роли пользователя в компании.
    Company Moderator имеет расширенные права, Company User имеет базовые права.
    При check_ownership=True также проверяет владение ресурсом (ABAC).

    Пример использования:
    ```
    @router.get('/{company_slug}/problems/')
    async def get_company_problems(
        company_slug: str,
        permission=Depends(require_company_permission('/{company_slug}/problems/', 'GET')),
        user=Depends(current_company_user)
    ):
        return {'status': 'success', 'company_slug': company_slug}
    ```

    Параметры:
    - endpoint: шаблон эндпоинта с возможными параметрами
    - method: HTTP метод
    - check_ownership: если True, будет проверять владение ресурсом (ABAC)
    - company_slug_param: имя параметра, содержащего slug компании
    """

    async def dependency(
        request: Request,
        user=Depends(current_company_user),
        ownership_service: ResourceOwnershipService = Depends(get_ownership_service)
        if check_ownership
        else None,
    ) -> bool:
        # Получаем параметры пути из запроса
        context = get_context_from_request(request)

        # Определяем роль пользователя
        role = get_company_role(user)

        # Переименовываем company_slug_param в company_slug для RBAC
        if company_slug_param in context and company_slug_param != 'company_slug':
            context['company_slug'] = context[company_slug_param]

        # Проверяем права доступа по ролям (RBAC)
        rbac = CompanyRBAC(role, **context)
        if not rbac.has_permission(endpoint, method, **context):
            raise create_forbidden_exception(
                f'Недостаточно прав для доступа к {method} {endpoint}'
            )

        # Если нужно проверить владение ресурсом (ABAC) и пользователь не модератор
        if check_ownership and ownership_service and role == CompanyRole.USER:
            # Определяем тип и ID ресурса из контекста
            resource_type, resource_id = identify_resource_from_context(context)

            # Проверяем владение ресурсом, если тип и ID определены
            if resource_type and resource_id:
                # Для обычных пользователей проверяем владение ресурсом через ABAC
                is_owner = await ownership_service.check_resource_ownership(
                    resource_type=resource_type,
                    resource_id=resource_id,
                    user_id=getattr(user, 'id', None),
                )

                if not is_owner:
                    raise create_forbidden_exception('У вас нет прав для управления этим ресурсом')

        return True

    return dependency


def require_superuser() -> DependencyFunc:
    """
    Зависимость для проверки, является ли пользователь суперпользователем

    Тип: RBAC
    Роли: Только Tabit Superuser

    Проверяет наличие роли суперпользователя. Для всех остальных ролей
    доступ запрещен.

    Пример использования:
    ```
    @router.get('/admin/super-access')
    async def super_access(
        is_superuser=Depends(require_superuser()),
        user=Depends(current_tabit_admin)
    ):
        return {'status': 'success'}
    ```
    """

    def dependency(user=Depends(current_tabit_superuser)) -> bool:
        # Функция current_tabit_superuser уже проверяет,
        # является ли пользователь суперпользователем
        # Если нет, она выбросит исключение
        return True

    return dependency


def require_company_moderator() -> DependencyFunc:
    """
    Зависимость для проверки, является ли пользователь модератором компании

    Тип: RBAC
    Роли: Только Company Moderator

    Проверяет наличие роли модератора компании. Для всех остальных ролей
    доступ запрещен, включая Company User.

    Пример использования:
    ```
    @router.get('/{company_slug}/manage')
    async def company_management(
        company_slug: str,
        is_moderator=Depends(require_company_moderator()),
        user=Depends(current_company_user)
    ):
        return {'status': 'success'}
    ```
    """

    def dependency(user=Depends(current_company_moderator)) -> bool:
        # Функция current_company_moderator уже проверяет,
        # является ли пользователь модератором компании
        # Если нет, она выбросит исключение
        return True

    return dependency


# Вспомогательные зависимости для проверки принадлежности к компании
def require_company_membership(company_slug_param: str = 'company_slug') -> DependencyFunc:
    """
    Зависимость для проверки принадлежности пользователя к компании

    Тип: ABAC
    Роли: Company Moderator, Company User

    Проверяет принадлежность пользователя к компании на основе атрибута company_slug.
    Атрибутивная проверка, не связанная с ролью пользователя в компании.

    Пример использования:
    ```
    @router.get('/{company_slug}/internal')
    async def company_internal(
        company_slug: str,
        membership=Depends(require_company_membership()),
        user=Depends(current_company_user)
    ):
        return {'status': 'success'}
    ```
    """

    def dependency(request: Request, user=Depends(current_company_user)) -> bool:
        # Получаем параметры пути из запроса
        path_params = request.path_params
        company_slug = path_params.get(company_slug_param)

        if not company_slug:
            raise create_bad_request_exception(f'Параметр {company_slug_param} не найден')

        # Проверяем принадлежность пользователя к компании
        user_company_slug = getattr(user, 'company_slug', None)
        if user_company_slug != company_slug:
            raise create_forbidden_exception(f'У вас нет доступа к компании {company_slug}')

        return True

    return dependency


def require_resource_ownership(resource_type: str, resource_id_param: str) -> AsyncDependencyFunc:
    """
    Зависимость для проверки владения ресурсом

    Тип: ABAC
    Роли: Company Moderator (имеет автоматический доступ ко всем ресурсам),
          Company User (проверяется владение ресурсом)

    Проверяет, является ли пользователь владельцем ресурса на основе его атрибутов.
    Модераторы компании имеют доступ ко всем ресурсам без проверки владения.

    Пример использования:
    ```
    @router.patch('/{company_slug}/problems/{problem_id}/tasks/{task_id}')
    async def update_task(
        company_slug: str,
        problem_id: int,
        task_id: int,
        ownership=Depends(require_resource_ownership('task', 'task_id')),
        user=Depends(current_company_user)
    ):
        return {'status': 'success'}
    ```
    """

    async def dependency(
        request: Request,
        user=Depends(current_company_user),
        ownership_service: ResourceOwnershipService = Depends(get_ownership_service),
    ) -> bool:
        # Получаем параметры пути из запроса
        path_params = request.path_params
        resource_id = path_params.get(resource_id_param)

        if not resource_id:
            raise create_bad_request_exception(f'Параметр {resource_id_param} не найден')

        # Получаем роль пользователя
        role = get_company_role(user)

        # Проверяем владение ресурсом
        # Модераторы всегда имеют доступ к любым ресурсам компании
        if role == CompanyRole.MODERATOR:
            return True

        # Проверяем владение ресурсом через ABAC-компонент
        is_owner = await ownership_service.check_resource_ownership(
            resource_type=resource_type, resource_id=resource_id, user_id=getattr(user, 'id', None)
        )

        if not is_owner:
            raise create_forbidden_exception('У вас нет прав для управления этим ресурсом')

        return True

    return dependency
