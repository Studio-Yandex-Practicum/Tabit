from typing import Any

from fastapi import Depends

from src.api.v1.auth.permissions.abac import ResourceOwnershipService, get_ownership_service
from src.api.v1.auth.permissions.rbac import CompanyRole, get_rbac_manager
from src.api.v1.auth.permissions.utils import create_forbidden_exception


class AuthorizationService:
    """
    Сервисный слой для авторизации, объединяющий RBAC и ABAC

    Тип: Комбинированный (RBAC + ABAC)
    Роли: Tabit Superuser, Tabit Admin, Company Moderator, Company User

    Этот класс предоставляет единую точку доступа для всех операций авторизации:
    1. Проверка прав доступа к эндпоинтам на основе ролей (RBAC)
    2. Проверка владения конкретными ресурсами (ABAC)

    Класс реализует фасад, абстрагирующий детали реализации RBAC и ABAC от
    конечных пользователей API.
    """

    def __init__(self, rbac_manager: Any, resource_ownership_service: ResourceOwnershipService):
        self.rbac_manager = rbac_manager
        self.resource_ownership_service = resource_ownership_service

    # Методы для работы с RBAC-компонентом
    def check_tabit_permission(self, user: Any, endpoint: str, method: str) -> bool:
        """
        Проверяет права доступа администратора Tabit

        Тип: RBAC
        Роли: Tabit Superuser, Tabit Admin

        Параметры:
        - user: пользователь TabitAdminUser
        - endpoint: эндпоинт (шаблон URL)
        - method: HTTP метод (GET, POST, PUT, PATCH, DELETE)

        Возвращает:
        - True, если доступ разрешен
        - False в противном случае
        """
        if not self.rbac_manager:
            raise ValueError('RBAC-менеджер не инициализирован')

        return self.rbac_manager.has_permission(endpoint, method)

    def check_company_permission(
        self,
        user: Any,
        endpoint: str,
        method: str,
        company_slug: str | None = None,
        **context: Any,
    ) -> bool:
        """
        Проверяет права доступа пользователя компании

        Тип: RBAC
        Роли: Company Moderator, Company User

        Параметры:
        - user: пользователь UserTabit
        - endpoint: эндпоинт (шаблон URL)
        - method: HTTP метод (GET, POST, PUT, PATCH, DELETE)
        - company_slug: идентификатор компании
        - context: дополнительный контекст для проверки

        Возвращает:
        - True, если доступ разрешен
        - False в противном случае
        """
        if not self.rbac_manager:
            raise ValueError('RBAC-менеджер не инициализирован')

        return self.rbac_manager.has_permission(endpoint, method, **(context or {}))

    # Методы для работы с ABAC-компонентом
    async def check_resource_ownership(
        self, user_id: int | str, resource_type: str, resource_id: int | str
    ) -> bool:
        """
        Проверяет владение ресурсом

        Тип: ABAC
        Роли: Company User (для проверки владения ресурсом)
              Company Moderator (обычно имеет доступ без проверки)

        Параметры:
        - user_id: ID пользователя
        - resource_type: тип ресурса (task, comment, problem, ...)
        - resource_id: ID ресурса

        Возвращает:
        - True, если пользователь владеет ресурсом
        - False в противном случае
        """
        return await self.resource_ownership_service.check_resource_ownership(
            resource_type, resource_id, user_id
        )

    # Комбинированные методы для полной авторизации
    async def authorize_tabit_user(self, user: Any, endpoint: str, method: str) -> bool:
        """
        Авторизует администратора Tabit для доступа к ресурсу

        Тип: RBAC
        Роли: Tabit Superuser, Tabit Admin

        Параметры:
        - user: пользователь TabitAdminUser
        - endpoint: эндпоинт (шаблон URL)
        - method: HTTP метод (GET, POST, PUT, PATCH, DELETE)

        Возвращает:
        - True, если авторизация успешна
        - False в противном случае

        Вызывает HTTPException с кодом 403, если авторизация не пройдена
        """
        if not self.check_tabit_permission(user, endpoint, method):
            raise create_forbidden_exception(
                f'Недостаточно прав для доступа к {method} {endpoint}'
            )
        return True

    async def authorize_company_user(
        self,
        user: Any,
        endpoint: str,
        method: str,
        check_ownership: bool = False,
        resource_type: str | None = None,
        resource_id: int | str | None = None,
        **context: Any,
    ) -> bool:
        """
        Авторизует пользователя компании для доступа к ресурсу

        Тип: Комбинированный (RBAC + ABAC при check_ownership=True)
        Роли: Company Moderator, Company User

        Параметры:
        - user: пользователь UserTabit
        - endpoint: эндпоинт (шаблон URL)
        - method: HTTP метод (GET, POST, PUT, PATCH, DELETE)
        - check_ownership: проверять ли владение ресурсом
        - resource_type: тип ресурса (task, comment, problem, ...)
        - resource_id: ID ресурса
        - context: дополнительный контекст для проверки

        Возвращает:
        - True, если авторизация успешна
        - False в противном случае

        Вызывает HTTPException с кодом 403, если авторизация не пройдена
        """
        # Проверка прав доступа на основе роли (RBAC)
        if not self.check_company_permission(user, endpoint, method, **context):
            raise create_forbidden_exception(
                f'Недостаточно прав для доступа к {method} {endpoint}'
            )

        # Проверка владения ресурсом (ABAC), если нужно
        if check_ownership and resource_type and resource_id:
            role = getattr(user, 'role', None)
            # Модераторы компании имеют доступ ко всем ресурсам
            if role == CompanyRole.MODERATOR or str(role) == CompanyRole.MODERATOR.value:
                return True

            user_id = getattr(user, 'id', None)
            if not user_id:
                raise create_forbidden_exception(
                    'Не удалось определить идентификатор пользователя'
                )

            if not await self.check_resource_ownership(user_id, resource_type, resource_id):
                raise create_forbidden_exception('У вас нет прав для управления этим ресурсом')

        return True


def get_authorization_service(
    rbac_manager=Depends(get_rbac_manager),
    ownership_service: ResourceOwnershipService = Depends(get_ownership_service),
) -> AuthorizationService:
    """
    Фабрика для создания сервиса авторизации

    Тип: Комбинированный (RBAC + ABAC)

    Параметры:
    - rbac_manager: менеджер RBAC
    - ownership_service: сервис проверки владения ресурсами

    Возвращает:
    - Экземпляр AuthorizationService
    """
    return AuthorizationService(rbac_manager, ownership_service)
