import asyncio

from termcolor import colored, cprint

from fake_data_factories.association_user_tags_factories import create_user_tag_links
from fake_data_factories.company_factories import create_companies
from fake_data_factories.company_user_factories import create_company_users
from fake_data_factories.constants import (
    FAKER_COMPANY_COUNT,
    FAKER_DEPARTMENT_COUNT,
    FAKER_USER_COUNT,
    USER_TAGS_COUNT,
)
from fake_data_factories.department_factories import create_company_department
from fake_data_factories.tabit_user_factories import create_tabit_admin_users
from fake_data_factories.tag_user_factories import create_uset_tag


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

    companies = await create_companies(count=FAKER_COMPANY_COUNT)
    for company in companies:
        company_users = await create_company_users(count=FAKER_USER_COUNT, company_id=company.id)
        company_tags = await create_uset_tag(count=USER_TAGS_COUNT, company_id=company.id)
        company_first_tag = company_tags[0]
        await create_company_department(count=FAKER_DEPARTMENT_COUNT, company_id=company.id)
        for user in company_users:
            await create_user_tag_links(user_id=user.id, tag_id=company_first_tag.id)

    await create_tabit_admin_users(count=FAKER_USER_COUNT)

    cprint(
        colored('Генерация завершена!', 'red', attrs=['reverse', 'blink']),
    )


if __name__ == '__main__':
    asyncio.run(fill_all_data())
