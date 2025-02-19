from dataclasses import dataclass


@dataclass
class Summary:
    """Содержит текст резюме конечных точек."""

    TABIT_ADMIN_AUTH_LIST: str = 'Список администраторов'
    TABIT_ADMIN_AUTH_GET_BY_ID: str = 'Карточка конкретного администратора сервиса'
    TABIT_ADMIN_AUTH_PATCH_BY_ID: str = 'Изменить данные конкретного администратора сервиса'
    TABIT_ADMIN_AUTH_DELETE_BY_ID: str = 'Удалить конкретного администратора сервиса'
    TABIT_ADMIN_AUTH_GET_ME: str = 'Доступ к своим данным администратора сервиса'
    TABIT_ADMIN_AUTH_PATCH_ME: str = 'Для редактирования своих данных администратору сервиса'
    TABIT_ADMIN_AUTH_REFRESH_TOKEN: str = 'Обновить токен'
    TABIT_ADMIN_AUTH_CREATE: str = 'Создать администратора сервиса'
    TABIT_ADMIN_AUTH_LOGIN: str = 'Авторизация'
    TABIT_ADMIN_AUTH_LOGOUT: str = 'Выход из система'

    TABIT_MANAGEMENT_COMPANY_LIST: str = 'Список всех компаний'
    TABIT_MANAGEMENT_COMPANY_CREATE: str = 'Создать новую компанию'
    TABIT_MANAGEMENT_COMPANY_UPDATE: str = 'Обновить данные компании'
    TABIT_MANAGEMENT_COMPANY_DELETE: str = 'Удалить компанию'

    COMPANY_USER_AUTH_LOGIN: str = 'Авторизация'
    COMPANY_USER_AUTH_LOGOUT: str = 'Выход из система'
    COMPANY_USER_AUTH_REFRESH_TOKEN: str = 'Обновить токен'


@dataclass
class Description:
    """Содержит текст описаний для конечных точек."""

    TABIT_ADMIN_AUTH_LIST: str = (
        'Возвращает список администраторов. Доступно только суперпользователю.'
    )
    TABIT_ADMIN_AUTH_GET_BY_ID: str = (
        'Отобразит карточку администратора сервиса по его `id`. Доступно только суперпользователю.'
    )
    TABIT_ADMIN_AUTH_PATCH_BY_ID: str = (
        'Изменить данные карточки администратора сервиса по его `id`. Доступно только '
        'суперпользователю.'
    )
    TABIT_ADMIN_AUTH_DELETE_BY_ID: str = (
        'Удалить администратора сервиса по его `id`. Доступно только суперпользователю. '
        'Удалить суперпользователя нельзя.'
    )
    TABIT_ADMIN_AUTH_GET_ME: str = (
        'Для доступа к своей учетной записи администраторов сервиса. '
        'Доступно только хозяину учетной записи.'
    )
    TABIT_ADMIN_AUTH_PATCH_ME: str = (
        'Позволит обновить данные о себе администратору сервиса. '
        'Доступно только хозяину учетной записи.'
    )
    TABIT_ADMIN_AUTH_REFRESH_TOKEN: str = (
        'Для обновления в токенов необходимо в заголовке '
        'Authorization передать refresh-token, вместо access-token. '
        'В ответ вернет два новых токена. Доступно только администраторам сервиса.'
    )
    TABIT_ADMIN_AUTH_CREATE: str = (
        'Создает нового администратора сервиса. Доступно только суперпользователю.'
    )
    TABIT_ADMIN_AUTH_LOGIN: str = 'Авторизация администраторов сервиса.'
    TABIT_ADMIN_AUTH_LOGOUT: str = 'Выход из системы администраторов сервиса.'

    TABIT_MANAGEMENT_COMPANY_LIST: str = (
        'Возвращает список всех компаний. Доступно только администраторам сервиса.'
    )
    TABIT_MANAGEMENT_COMPANY_CREATE: str = (
        'Создает новую компанию. Доступно только администраторам сервиса.'
        'Поля "license_id" и "start_license_time" либо оба указываются, либо не одного.'
    )
    TABIT_MANAGEMENT_COMPANY_UPDATE: str = (
        'Обновляет данные компании по её `slug`. Доступно только администраторам сервиса.'
    )
    TABIT_MANAGEMENT_COMPANY_DELETE: str = (
        'Удаляет компанию по её `slug`. Доступно только администраторам сервиса.'
        'Поля "license_id" и "start_license_time" либо оба указываются, либо не одного.'
    )

    COMPANY_USER_AUTH_LOGIN: str = 'Авторизация пользователя сервиса.'
    COMPANY_USER_AUTH_LOGOUT: str = 'Авторизация пользователя сервиса.'
    COMPANY_USER_AUTH_REFRESH_TOKEN: str = (
        'Для обновления в токенов необходимо в заголовке Authorization передать refresh-token, '
        'вместо access-token. В ответ вернет два новых токена. Доступно только пользователя '
        'сервиса. У администраторов сервиса своя конечная точка.'
    )


@dataclass
class TextError:
    """Содержит текст сообщений об ошибке."""

    FORBIDDEN_ROLE_ADMIN: str = 'Доступно только админам компаний.'
    LOGIN = 'Неверные учетные данные для входа в систему.'
    IS_SUPERUSER: str = 'Объект - суперпользователь.'
