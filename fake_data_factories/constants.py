# Константы для генерации тестовых данных в Faker-сидерах

FAKER_USER_COUNT = 5  # Число пользователей для генерации
FAKER_COMPANY_COUNT = 5  # Число компаний для генерации
FAKER_DEPARTMENT_COUNT = 5  # Число отделов для генерации
DEFAULT_DEPARTMENT_NAMES = [
    'Отдел кадров',
    'Отдел менеджмента',
    'Отдел продаж',
    'IT-отдел',
    'Технический отдел',
]  # Имена для отделов компании
AMOUNT_OF_ADMIN = 1  # количество админов создаваемых для компании за 1 запуск скрипта
COMPANY_USER_CREATED_TEXT = '{role} компании c id={company_id}: {user_email}, пасс: {password}'
USER_TAGS_COUNT = 5
