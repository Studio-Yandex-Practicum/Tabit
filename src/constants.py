# TODO: создать класс Length, декорировать dataclass. Все длины упаковать в этот класс, из названий
# констант удалить слово LENGTH
LENGTH_NAME_USER: int = 100
LENGTH_NAME_COMPANY: int = 255
LENGTH_NAME_DEPARTMENT: int = 255
LENGTH_NAME_PROBLEM: int = 255
LENGTH_NAME_MEETING_PLACE: int = 255
LENGTH_SMALL_NAME: int = 30
LENGTH_TELEGRAM_USERNAME: int = 100
LENGTH_FILE_LINK: int = 2048
LENGTH_SLUG: int = 25

ZERO: int = 0

# crud
DEFAULT_SKIP = 0  # Значение по умолчанию для пропуска записей
DEFAULT_LIMIT = 100  # Ограничение количества записей
DEFAULT_AUTO_COMMIT = True  # для crud
