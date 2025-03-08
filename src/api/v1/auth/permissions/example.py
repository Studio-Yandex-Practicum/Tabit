"""
Пример использования системы разграничения прав доступа
Это демонстрационный файл, показывающий, как интегрировать систему авторизации в эндпоинты
"""

from fastapi import APIRouter, Depends, Request

from src.api.v1.auth.dependencies import current_company_user, current_tabit_admin
from src.api.v1.auth.permissions.abac import ResourceOwnershipService, get_ownership_service
from src.api.v1.auth.permissions.decorators import (
    company_permission_required,
    get_company_role,
    get_tabit_role,
    permission_required,
    tabit_permission_required,
)
from src.api.v1.auth.permissions.dependencies import (
    require_company_membership,
    require_company_moderator,
    require_company_permission,
    require_resource_ownership,
    require_tabit_permission,
)
from src.api.v1.auth.permissions.service import AuthorizationService, get_authorization_service
from src.users.models.enum import CompanyRole

# Создаем роутер для примеров
router = APIRouter()


# Пример 1: Использование декоратора для проверки прав администраторов Tabit
@router.get('/admin/dashboard')
@tabit_permission_required('/admin/dashboard', 'GET')
async def get_admin_dashboard(user=Depends(current_tabit_admin)):
    """
    Пример использования декоратора tabit_permission_required
    Этот эндпоинт доступен только для администраторов Tabit
    """
    role = get_tabit_role(user)

    return {
        'status': 'success',
        'message': 'Добро пожаловать в панель администратора',
        'role': role.value,
    }


# Пример 2: Использование зависимости для проверки прав администраторов Tabit
@router.get('/admin/companies/overview')
async def get_companies_overview(
    permission=Depends(require_tabit_permission('/admin/companies/overview', 'GET')),
    user=Depends(current_tabit_admin),
):
    """
    Пример использования зависимости require_tabit_permission
    Этот эндпоинт доступен только для администраторов Tabit
    """
    role = get_tabit_role(user)

    return {'status': 'success', 'message': 'Обзор компаний', 'role': role.value}


# Пример 3: Использование декоратора для проверки прав пользователей компании
@router.get('/{company_slug}/problems')
@company_permission_required('/{company_slug}/problems', 'GET')
async def get_company_problems(company_slug: str, user=Depends(current_company_user)):
    """
    Пример использования декоратора company_permission_required
    Этот эндпоинт доступен для всех пользователей компании (модераторов и обычных пользователей)
    """
    role = get_company_role(user)

    return {
        'status': 'success',
        'message': f'Список проблем компании {company_slug}',
        'role': role.value,
    }


# Пример 4: Использование зависимости для проверки прав пользователей компании
@router.post('/{company_slug}/problems')
async def create_company_problem(
    company_slug: str,
    request: Request,
    permission=Depends(require_company_permission('/{company_slug}/problems', 'POST')),
    user=Depends(current_company_user),
):
    """
    Пример использования зависимости require_company_permission
    Этот эндпоинт доступен только для модераторов компании
    """
    role = get_company_role(user)

    return {
        'status': 'success',
        'message': f'Создана новая проблема в компании {company_slug}',
        'role': role.value,
    }


# Пример 5: Проверка принадлежности к компании (элемент ABAC)
@router.get('/{company_slug}/internal-data')
async def get_company_internal_data(
    company_slug: str,
    permission=Depends(require_company_membership()),
    user=Depends(current_company_user),
):
    """
    Пример использования зависимости require_company_membership
    Проверяет, принадлежит ли пользователь к компании (ABAC)
    """
    role = get_company_role(user)

    return {
        'status': 'success',
        'message': f'Внутренние данные компании {company_slug}',
        'role': role.value,
    }


# Пример 6: Проверка владения ресурсом (элемент ABAC)
@router.patch('/{company_slug}/problems/{problem_id}/tasks/{task_id}')
async def update_task(
    company_slug: str,
    problem_id: int,
    task_id: int,
    ownership=Depends(require_resource_ownership('task', 'task_id')),
    permission=Depends(
        require_company_permission(
            '/{company_slug}/problems/{problem_id}/tasks/{task_id}', 'PATCH'
        )
    ),
    user=Depends(current_company_user),
):
    """
    Пример использования зависимости require_resource_ownership
    Проверяет, является ли пользователь владельцем задачи (ABAC)
    """
    role = get_company_role(user)

    return {'status': 'success', 'message': f'Задача {task_id} обновлена', 'role': role.value}


# Пример 7: Использование сервисного слоя для императивных проверок
@router.post('/{company_slug}/problems/{problem_id}/comments')
async def create_comment(
    company_slug: str,
    problem_id: int,
    user=Depends(current_company_user),
    auth_service: AuthorizationService = Depends(get_authorization_service),
):
    """
    Пример использования сервисного слоя для императивных проверок
    Более гибкий подход для сложных сценариев авторизации
    """
    # Определяем роль пользователя
    role = get_company_role(user)

    # Устанавливаем RBAC-менеджер и контекст
    auth_service.set_rbac_manager(role, company_slug=company_slug)

    # Проверяем базовые разрешения
    endpoint = f'/{company_slug}/problems/{problem_id}/comments'
    method = 'POST'

    try:
        await auth_service.ensure_permission(endpoint, method)
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

    # Проверяем дополнительные условия (ABAC)
    # Например, только создатель проблемы или назначенный ответственный может комментировать
    try:
        # Для модераторов пропускаем эту проверку
        if role == CompanyRole.USER:
            await auth_service.ensure_resource_ownership(
                'problem', problem_id, getattr(user, 'id', None)
            )
    except Exception as e:
        return {'status': 'error', 'message': str(e)}

    # Если все проверки пройдены, создаем комментарий
    # (Здесь был бы код для создания комментария)

    return {
        'status': 'success',
        'message': f'Комментарий к проблеме {problem_id} создан',
        'role': role.value,
    }


# Пример 8: Использование ABAC напрямую для сложных правил доступа
@router.post('/{company_slug}/problems/{problem_id}/tasks/{task_id}/complete')
async def complete_task(
    company_slug: str,
    problem_id: int,
    task_id: int,
    user=Depends(current_company_user),
    ownership_service: ResourceOwnershipService = Depends(get_ownership_service),
):
    """
    Пример прямого использования ABAC-компонента
    Для действий, требующих сложных правил проверки владения ресурсом
    """
    # Определяем роль пользователя
    role = get_company_role(user)

    # Проверяем, является ли пользователь владельцем или исполнителем задачи
    is_task_owner = await ownership_service.check_task_ownership(
        task_id, getattr(user, 'id', None)
    )

    if not is_task_owner and role != CompanyRole.MODERATOR:
        return {'status': 'error', 'message': 'У вас нет прав для завершения этой задачи'}

    # Если проверка прошла успешно, завершаем задачу
    # (Здесь был бы код для завершения задачи)

    return {'status': 'success', 'message': f'Задача {task_id} завершена', 'role': role.value}


# Пример 9: Использование требования модератора компании
@router.get('/{company_slug}/moderate')
async def moderate_company(
    company_slug: str,
    is_moderator=Depends(require_company_moderator()),
    user=Depends(current_company_user),
):
    """
    Пример использования зависимости require_company_moderator
    Этот эндпоинт доступен только для модераторов компании
    """
    # Здесь мы уже уверены, что пользователь - модератор, но все равно получаем роль для ответа
    role = get_company_role(user)

    return {
        'status': 'success',
        'message': f'Панель модерации компании {company_slug}',
        'role': role.value,
    }


# Пример 10: Универсальный декоратор для проверки прав
@router.get('/universal/endpoint')
@permission_required('/universal/endpoint', 'GET', check_ownership=False)
async def universal_endpoint(request: Request, user=Depends(current_company_user)):
    """
    Пример использования универсального декоратора permission_required
    Определяет тип пользователя и применяет соответствующую логику проверки
    """
    # Проверяем, тип пользователя и получаем соответствующую роль
    if hasattr(user, 'is_superuser'):
        role = get_tabit_role(user)
    else:
        role = get_company_role(user)

    return {'status': 'success', 'message': 'Универсальный эндпоинт', 'role': role.value}
