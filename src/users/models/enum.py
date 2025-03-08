from enum import StrEnum


class TabitRole(StrEnum):
    """Роли администраторов системы Tabit"""

    SUPERUSER = 'tabit_superuser'  # TS
    ADMIN = 'tabit_admin'  # TA


class CompanyRole(StrEnum):
    """Роли пользователей компаний"""

    MODERATOR = 'company_moderator'  # CM
    USER = 'company_user'  # CU
