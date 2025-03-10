import asyncio

from termcolor import colored, cprint

from fake_data_factories.company_factories import create_companies
from fake_data_factories.company_user_factories import create_company_users
from fake_data_factories.constants import (
    FAKER_COMPANY_COUNT,
    FAKER_DEPARTMENT_COUNT,
    FAKER_USER_COUNT,
    LICENSE_TYPE_COUNT,
)
from fake_data_factories.department_factories import create_company_department
from fake_data_factories.license_type_factories import create_license_type
from fake_data_factories.tabit_user_factories import create_tabit_admin_users


async def fill_all_data():
    """
    Генерация тестовых данных для всех сущностей.

    Шаги заполнения бд:
        1. companies: Заполняет бд `count` количеством компаний.
        2. Циклом по созданным компаниям, для каждой компании создает count работников
        компании(1 из них админ), и count департаментов.
        3. Заполняет бд count админами Tabit.
    """
    cprint(
        colored('Начинаем генерацию тестовых данных...', 'red', attrs=['reverse', 'blink']),
    )
    license_types = await create_license_type(count=LICENSE_TYPE_COUNT)
    company_license_type = license_types[0]
    companies = await create_companies(
        count=FAKER_COMPANY_COUNT, license_id=company_license_type.id
    )
    for company in companies:
        await create_company_users(count=FAKER_USER_COUNT, company_id=company.id)
        await create_company_department(count=FAKER_DEPARTMENT_COUNT, company_id=company.id)
    await create_tabit_admin_users(count=FAKER_USER_COUNT)

    cprint(
        colored('Генерация завершена!', 'red', attrs=['reverse', 'blink']),
    )


if __name__ == '__main__':
    asyncio.run(fill_all_data())
