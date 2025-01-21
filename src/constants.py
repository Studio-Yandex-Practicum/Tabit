from dataclasses import dataclass


@dataclass
class Endpoints:
    """Эндпоинты проекта."""

    MAIN = ''
    USER = '/users'
    DEPARTMENT = '/department'


@dataclass
class Tag:
    """Теги для эндпоинтов проекта."""

    MAIN = 'Main page'
    USERS = 'Users'
    COMPANIES = 'Companies'
