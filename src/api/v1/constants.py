"""
Модуль констант для энпоинтов приложения.
"""

from dataclasses import dataclass


@dataclass
class Summary:
    """Содержит текст резюме маршрутизаторов."""

    TABIT_ADMIN_AUTH_LIST: str = 'Список администраторов'
    TABIT_ADMIN_AUTH_GET_BY_ID: str = 'Карточка конкретного администратора сервиса'
    TABIT_ADMIN_AUTH_PATCH_BY_ID: str = 'Изменить данные конкретного администратора сервиса'
    TABIT_ADMIN_AUTH_DELETE_BY_ID: str = 'Удалить конкретного администратора сервиса'
    TABIT_ADMIN_AUTH_GET_ME: str = 'Доступ к своим данным администратора сервиса'
    TABIT_ADMIN_AUTH_PATCH_ME: str = 'Для редактирования своих данных администратору сервиса'
    TABIT_ADMIN_AUTH_LOGIN: str = 'Авторизация'
    TABIT_ADMIN_AUTH_LOGOUT: str = 'Выход из система'
    TABIT_ADMIN_AUTH_CREATE: str = 'Создать администратора сервиса'

    TABIT_MANAGEMENT_COMPANY_LIST: str = 'Список всех компаний'
    TABIT_MANAGEMENT_COMPANY_CREATE: str = 'Создать новую компанию'
    TABIT_MANAGEMENT_COMPANY_UPDATE: str = 'Обновить данные компании'
    TABIT_MANAGEMENT_COMPANY_DELETE: str = 'Удалить компанию'

    TABIT_COMPANY: str = 'Получить данные о компании'
    TABIT_COMPANY_DEPARTMENTS_LIST: str = 'Получить список всех отделов компании'
    TABIT_COMPANY_DEPARTMENTS_CREATE: str = 'Создать новый отдел компании'
    TABIT_COMPANY_DEPARTMENT: str = 'Получить данные об отделе компании'
    TABIT_COMPANY_DEPARTMENTS_UPDATE: str = 'Обновить данные об отделе компании'
    TABIT_COMPANY_DEPARTMENTS_DELETE: str = 'Удалить отдел компании'
    TABIT_COMPANY_DEPARTMENTS_IMPORT: str = 'Импортировать список отделов компании'

    TABIT_COMPANY_EMPLOYEES_LIST: str = 'Получить список всех сотрудников компании'
    TABIT_COMPANY_EMPLOYEE: str = 'Получить информацию о сотруднике компании'
    TABIT_COMPANY_EMPLOYEES_CREATE: str = 'Добавить сотрудника в отдел компании'
    TABIT_COMPANY_EMPLOYEES_UPDATE: str = 'Изменить данные сотрудника компании'
    TABIT_COMPANY_EMPLOYEES_DELETE: str = 'Удалить сотрудника компании'
    TABIT_COMPANY_EMPLOYEES_IMPORT: str = 'Импортировать список сотрудников компании'


TEXT_ERROR_FORBIDDEN_ROLE_ADMIN: str = 'Доступно только админам компаний'
