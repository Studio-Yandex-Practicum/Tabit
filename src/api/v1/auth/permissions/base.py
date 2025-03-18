from abc import ABC, abstractmethod
from typing import Any, Generic, Protocol, TypeVar

T = TypeVar('T')


class RBACHandler(Protocol):
    """
    Протокол для обработчиков RBAC

    Тип: RBAC

    Определяет интерфейс компонентов, которые проверяют права доступа на основе ролей.
    Используется как для администраторов Tabit, так и для пользователей компаний.
    """

    def has_permission(self, endpoint: str, method: str, **context: Any) -> bool:
        """Проверяет наличие разрешения для эндпоинта"""
        ...


class ABACHandler(Protocol):
    """
    Протокол для обработчиков ABAC

    Тип: ABAC
    Роли: Company User, Company Moderator

    Определяет интерфейс компонентов, которые проверяют владение ресурсами
    на основе атрибутов. Применяется в основном для пользователей компании.
    """

    async def check_resource_ownership(
        self, resource_type: str, resource_id: Any, user_id: Any
    ) -> bool:
        """Проверяет владение ресурсом"""
        ...


class BasePermissionChecker(ABC, Generic[T]):
    """
    Базовый класс для проверки разрешений

    Тип: Абстрактный (используется как для RBAC, так и для ABAC)

    Типовой параметр:
    - T: тип роли пользователя
    """

    @abstractmethod
    def get_user_role(self, user: Any) -> T:
        """
        Возвращает роль пользователя

        Параметры:
        - user: пользователь

        Возвращает:
        - Роль пользователя
        """
        pass

    @abstractmethod
    def create_rbac_handler(self, role: T, **context: Any) -> RBACHandler:
        """
        Создает обработчик RBAC для проверки прав доступа

        Параметры:
        - role: роль пользователя
        - context: дополнительный контекст для проверки

        Возвращает:
        - Экземпляр RBACHandler
        """
        pass

    def check_permission(self, user: Any, endpoint: str, method: str, **context: Any) -> bool:
        """
        Проверяет наличие разрешения

        Тип: RBAC

        Параметры:
        - user: пользователь
        - endpoint: путь эндпоинта
        - method: HTTP метод
        - context: дополнительный контекст

        Возвращает:
        - True, если разрешение есть
        - False в противном случае
        """
        role = self.get_user_role(user)
        rbac = self.create_rbac_handler(role, **context)
        return rbac.has_permission(endpoint, method, **context)
