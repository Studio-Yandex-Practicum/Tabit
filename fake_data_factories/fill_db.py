import asyncio

from termcolor import colored, cprint

from fake_data_factories.company_factories import create_companies
from fake_data_factories.company_user_factories import create_company_users
from fake_data_factories.tabit_user_factories import create_tabit_admin_users


async def fill_all_data():
    """
    Генерация тестовых данных для всех сущностей.
    """
    cprint(
        colored('Начинаем генерацию тестовых данных...', 'red', attrs=['reverse', 'blink']),
    )

    companies = await create_companies(count=1)  # Если хотим создавать компанию отдельно
    first_company_id = companies[0].id if companies else None  # вытаскиваем id нужной
    await create_company_users(
        count=1, company_id=first_company_id, password='uasya'
    )  #  и сюда можем поместить company_id=first_company_id
    await create_tabit_admin_users(count=1)

    cprint(
        colored('Генерация завершена!', 'red', attrs=['reverse', 'blink']),
    )


if __name__ == '__main__':
    asyncio.run(fill_all_data())
