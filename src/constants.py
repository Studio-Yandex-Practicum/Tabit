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

    
    
LENGTH_NAME_USER: int = 100
LENGTH_SMALL_NAME: int = 30
LENGTH_TELEGRAM_USERNAME: int = 100
