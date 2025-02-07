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
