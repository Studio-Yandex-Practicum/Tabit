DEFAULT_NUMBER_DEY_LICENSE: int = 1
DEFAULT_LICENSE_TERN: dict[str, int] = {'day': 1}

title_name_license: str = 'Название лицензии'
title_license_tern: str = 'Срок действия лицензии в днях'
title_max_admins_count: str = 'Максимальное количество админов'
title_max_employees_count: str = 'Максимальное количество сотрудников'
title_name_admin: str = 'Имя админа сервиса'
title_surname_admin: str = 'Фамилия админа сервиса'
title_patronymic_admin: str = 'Отчество админа сервиса'
title_phone_number_admin: str = 'Контактный телефон админа сервиса'

ERROR_FIELD_INTERVAL = (
    'Поле не может быть пустым. '
    'Может быть целым числом, или строкой, обозначающее целое число, '
    'или строкой формата "P1D", "P1Y", "P1Y1D".'
)
ERROR_FIELD_START_OR_END_SPACE = 'Поле не может начинаться или заканчиваться пробелом.'
