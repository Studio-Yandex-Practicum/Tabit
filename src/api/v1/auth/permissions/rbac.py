from typing import Dict, List, Union

from src.users.models.enum import CompanyRole, TabitRole


# Базовый класс для RBAC
class RBACBase:
    """Базовый класс для RBAC"""

    def has_permission(self, endpoint: str, method: str, **context) -> bool:
        """Проверка прав доступа к эндпоинту с учетом контекста"""
        raise NotImplementedError('Subclasses must implement this method')

    @classmethod
    def get_role_permissions(cls) -> Dict[str, Dict[str, List[str]]]:
        """Получение разрешений для роли"""
        raise NotImplementedError('Subclasses must implement this method')


class TabitAdminRBAC(RBACBase):
    """Класс для управления доступом администраторов Tabit"""

    def __init__(self, role: TabitRole):
        self.role = role
        self.permissions = self.get_role_permissions().get(role, {})

    def has_permission(self, endpoint: str, method: str, **context) -> bool:
        """Проверяет, имеет ли администратор права на выполнение метода для эндпоинта"""
        # Проверим наличие прямого разрешения
        if endpoint in self.permissions and method in self.permissions[endpoint]:
            return True

        # Проверим наличие шаблонного разрешения с wildcards
        for route_pattern, methods in self.permissions.items():
            if self._match_endpoint_pattern(endpoint, route_pattern) and method in methods:
                return True

        return False

    def _match_endpoint_pattern(self, endpoint: str, pattern: str) -> bool:
        """
        Проверяет, соответствует ли эндпоинт шаблону.
        Поддерживает три типа шаблонов:
        1. Простые wildcards с использованием * (например /admin/*)
        2. Шаблоны с параметрами в фигурных скобках (например /admin/{id})
        3. Прямое совпадение строк

        Логика работы:
        1. Если в шаблоне есть символ *, он преобразуется в регулярное выражение .*
           и выполняется проверка полного совпадения с эндпоинтом.
        2. Если шаблон содержит параметры в фигурных скобках {param}, выполняется
           пошаговое сравнение частей пути, игнорируя параметры.
        3. Если шаблон не содержит специальных символов, выполняется прямое
           сравнение строк.

        Примеры:
        - /admin/* соответствует /admin/dashboard
        - /admin/{id} соответствует /admin/123
        - /admin/users точно соответствует /admin/users

        Возвращает:
        bool: True если эндпоинт соответствует шаблону, иначе False
        """
        # Преобразуем шаблон в регулярное выражение
        if '*' in pattern:
            # Заменяем * на .* для regex
            import re

            pattern_regex = pattern.replace('*', '.*')
            return bool(re.match(f'^{pattern_regex}$', endpoint))

        # Проверяем на соответствие шаблонам с параметрами {param}
        if '{' in pattern and '}' in pattern:
            pattern_parts = pattern.split('/')
            endpoint_parts = endpoint.split('/')

            # Если количество частей отличается, то шаблоны не совпадают
            if len(pattern_parts) != len(endpoint_parts):
                return False

            # Проверяем каждую часть
            for i, part in enumerate(pattern_parts):
                if '{' in part and '}' in part:
                    # Это параметр, пропускаем проверку
                    continue
                if part != endpoint_parts[i]:
                    return False

            return True

        # Прямое сравнение
        return pattern == endpoint

    @classmethod
    def get_role_permissions(cls) -> Dict[TabitRole, Dict[str, List[str]]]:
        """
        Возвращает словарь разрешений для ролей администраторов Tabit
        Формат: {
            'роль': {
                'эндпоинт': ['метод1', 'метод2', ...],
                ...
            },
            ...
        }
        """
        # Общие права для администраторов (TS и TA)
        common_admin_permissions = {
            # company.py
            '/{company_slug}/': ['GET'],
            '/{company_slug}/departments': ['GET', 'POST'],
            '/{company_slug}/departments/import': ['POST'],
            '/{company_slug}/department/{department_id}': ['GET', 'PATCH', 'DELETE'],
            '/{company_slug}/employees': ['GET', 'POST'],
            '/{company_slug}/employees/import': ['POST'],
            '/{company_slug}/employees/{uuid}': ['GET', 'PATCH', 'DELETE'],
            '/{company_slug}/feedback/': ['POST'],
            # company_user.py
            '/company_id/{uuid}/': ['GET', 'PATCH'],
            # problems.py
            '/{company_slug}/problems': ['GET', 'POST'],
            '/{company_slug}/problems/{problem_id}': ['GET', 'PATCH', 'DELETE'],
            # problem_feeds.py
            '/{company_slug}/problems/{problem_id}/thread': ['GET', 'POST'],
            '/{company_slug}/problems/{problem_id}/{thread_id}/comments': ['POST'],
            '/{company_slug}/problems/{problem_id}/{thread_id}/comments/{comment_id}': [
                'PATCH',
                'DELETE',
            ],
            '/{company_slug}/problems/{problem_id}/{thread_id}/comments/{comment_id}/like': [
                'POST'
            ],
            '/{company_slug}/problems/{problem_id}/{thread_id}/comments/{comment_id}/unlike': [
                'POST'
            ],
            # problem_meetings.py
            '/{company_slug}/problems/{problem_id}/meetings': ['GET', 'POST'],
            '/{company_slug}/problems/{problem_id}/meetings/{meeting_id}': [
                'GET',
                'PATCH',
                'DELETE',
            ],
            # surveys.py
            '/{company_slug}/surveys': ['GET', 'POST'],
            '/{company_slug}/surveys/{uuid}': ['GET'],
            '/{company_slug}/surveys/{uuid}/{survey_id}': ['GET'],
            '/{company_slug}/surveys/results/general': ['GET'],
            '/{company_slug}/surveys/results/personalized': ['GET'],
            '/{company_slug}/surveys/results/dynamics': ['GET'],
            '/{company_slug}/surveys/manage': ['POST', 'DELETE'],
            # tabit_management.py
            '/admin/': ['GET'],
            '/admin/staff': ['GET', 'POST'],
            '/admin/staff/{user_id}': ['GET', 'PUT', 'PATCH', 'DELETE'],
            '/admin/staff/{user_id}/resetpassword': ['POST'],
            # tabit_management_licenses.py
            '/admin/licenses': ['GET', 'POST'],
            '/admin/licenses/{license_id}': ['GET', 'PATCH', 'DELETE'],
            # tabit_management_companies.py
            '/admin/companies': ['GET', 'POST'],
            '/admin/companies/{company_slug}': ['PATCH', 'DELETE'],
            # tasks.py
            '/{company_slug}/problems/{problem_id}/tasks': ['GET', 'POST'],
            '/{company_slug}/problems/{problem_id}/tasks/{task_id}': ['GET', 'PATCH', 'DELETE'],
            # tabit_admin_auth.py (общие)
            '/admin/auth/me': ['GET', 'PATCH'],
            '/admin/auth/refresh-token': ['POST'],
            '/admin/auth/login': ['POST'],
            '/admin/auth/logout': ['POST'],
        }

        # Права только для Superuser
        superuser_permissions = {
            **common_admin_permissions,
            # tabit_admin_auth.py (только для TS)
            '/admin/auth': ['GET', 'POST'],
            '/admin/auth/{user_id}': ['GET', 'PATCH', 'DELETE'],
        }

        return {
            TabitRole.SUPERUSER: superuser_permissions,
            TabitRole.ADMIN: common_admin_permissions,
        }


class CompanyRBAC(RBACBase):
    """Класс для управления доступом пользователей компаний"""

    def __init__(self, role: CompanyRole, **context):
        self.role = role
        self.context = context
        self.permissions = self.get_role_permissions().get(role, {})

    def has_permission(self, endpoint: str, method: str, **context) -> bool:
        """
        Проверяет, имеет ли пользователь компании права на выполнение метода для эндпоинта
        с учетом контекста (принадлежность к компании и т.д.)
        """
        merged_context = {**self.context, **context}
        company_slug = merged_context.get('company_slug')

        # Заменяем {company_slug} на конкретное значение, если оно известно
        if company_slug and '{company_slug}' in endpoint:
            actual_endpoint = endpoint.replace('{company_slug}', company_slug)
        else:
            actual_endpoint = endpoint

        # Проверяем прямое соответствие
        if actual_endpoint in self.permissions and method in self.permissions[actual_endpoint]:
            return True

        # Проверяем шаблоны с wildcards или параметрами
        for route_pattern, methods in self.permissions.items():
            pattern = route_pattern

            # Если в контексте есть company_slug, подставляем его в шаблон
            if company_slug and '{company_slug}' in pattern:
                pattern = pattern.replace('{company_slug}', company_slug)

            if self._match_endpoint_pattern(actual_endpoint, pattern) and method in methods:
                return True

        return False

    def _match_endpoint_pattern(self, endpoint: str, pattern: str) -> bool:
        """
        Проверяет, соответствует ли эндпоинт шаблону
        Поддерживает простые wildcards шаблоны вида /company/* или /company/{id}/*
        """
        # Преобразуем шаблон в регулярное выражение
        if '*' in pattern:
            # Заменяем * на .* для regex
            import re

            pattern_regex = pattern.replace('*', '.*')
            return bool(re.match(f'^{pattern_regex}$', endpoint))

        # Проверяем на соответствие шаблонам с параметрами {param}
        if '{' in pattern and '}' in pattern:
            pattern_parts = pattern.split('/')
            endpoint_parts = endpoint.split('/')

            # Если количество частей отличается, то шаблоны не совпадают
            if len(pattern_parts) != len(endpoint_parts):
                return False

            # Проверяем каждую часть
            for i, part in enumerate(pattern_parts):
                if '{' in part and '}' in part:
                    # Это параметр, пропускаем проверку
                    continue
                if part != endpoint_parts[i]:
                    return False

            return True

        # Прямое сравнение
        return pattern == endpoint

    @classmethod
    def get_role_permissions(cls) -> Dict[CompanyRole, Dict[str, List[str]]]:
        """
        Возвращает словарь разрешений для ролей пользователей компаний

        Формат: {
            'роль': {
                'эндпоинт': ['метод1', 'метод2', ...],
                ...
            },
            ...
        }
        """
        # Права для обычных пользователей (CU)
        user_permissions = {
            # company.py
            '/{company_slug}/feedback': ['POST'],
            # company_user.py
            '/company_id/{uuid}': ['GET', 'PATCH'],
            # company_user_auth.py
            '/auth/login': ['POST'],
            '/auth/logout': ['POST'],
            '/auth/refresh-token': ['POST'],
            '/auth/forgot-password': ['POST'],
            '/auth/reset-password': ['POST'],
            # problems.py
            '/{company_slug}/problems': ['GET'],
            '/{company_slug}/problems/{problem_id}': ['GET'],
            # problem_feeds.py
            '/{company_slug}/problems/{problem_id}/thread': ['GET'],
            '/{company_slug}/problems/{problem_id}/{thread_id}/comments': ['POST'],
            '/{company_slug}/problems/{problem_id}/{thread_id}/comments/{comment_id}': [
                'PATCH',
                'DELETE',
            ],
            '/{company_slug}/problems/{problem_id}/{thread_id}/comments/{comment_id}/like': [
                'POST'
            ],
            '/{company_slug}/problems/{problem_id}/{thread_id}/comments/{comment_id}/unlike': [
                'POST'
            ],
            # problem_meetings.py
            '/{company_slug}/problems/{problem_id}/meetings': ['GET'],
            '/{company_slug}/problems/{problem_id}/meetings/{meeting_id}': ['GET'],
            # surveys.py
            '/{company_slug}/surveys': ['GET'],
            '/{company_slug}/surveys/{uuid}': ['GET'],
            '/{company_slug}/surveys/{uuid}/{survey_id}': ['GET'],
            '/{company_slug}/surveys/results/general': ['GET'],
            '/{company_slug}/surveys/results/personalized': ['GET'],
            '/{company_slug}/surveys/results/dynamics': ['GET'],
            # tasks.py
            '/{company_slug}/problems/{problem_id}/tasks': ['GET', 'POST'],
            '/{company_slug}/problems/{problem_id}/tasks/{task_id}': ['GET', 'PATCH', 'DELETE'],
        }

        # Права для модераторов компаний (CM)
        moderator_permissions = {
            **user_permissions,
            # company.py
            '/{company_slug}': ['GET'],
            '/{company_slug}/departments': ['GET', 'POST'],
            '/{company_slug}/departments/import': ['POST'],
            '/{company_slug}/department/{department_id}': ['GET', 'PATCH', 'DELETE'],
            '/{company_slug}/employees': ['GET', 'POST'],
            '/{company_slug}/employees/import': ['POST'],
            '/{company_slug}/employees/{uuid}': ['GET', 'PATCH', 'DELETE'],
            # problems.py
            '/{company_slug}/problems': ['POST'],
            '/{company_slug}/problems/{problem_id}': ['PATCH', 'DELETE'],
            # problem_feeds.py
            '/{company_slug}/problems/{problem_id}/thread': ['POST'],
            # problem_meetings.py
            '/{company_slug}/problems/{problem_id}/meetings': ['POST'],
            '/{company_slug}/problems/{problem_id}/meetings/{meeting_id}': ['PATCH', 'DELETE'],
            # surveys.py
            '/{company_slug}/surveys': ['POST'],
            '/{company_slug}/surveys/manage': ['POST', 'DELETE'],
        }

        return {CompanyRole.MODERATOR: moderator_permissions, CompanyRole.USER: user_permissions}


# Фабрика для создания специализированных RBAC объектов
def get_rbac_manager(role_type: Union[TabitRole, CompanyRole], **context):
    """Фабричный метод для создания RBAC объекта в зависимости от типа роли"""
    if isinstance(role_type, TabitRole):
        return TabitAdminRBAC(role_type)
    elif isinstance(role_type, CompanyRole):
        return CompanyRBAC(role_type, **context)
    else:
        raise ValueError(
            f'Неизвестный тип роли: {role_type}'
        )  # Code is unreachable, но хочу оставить на всякий случай
