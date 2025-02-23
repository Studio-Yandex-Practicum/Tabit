import asyncio

from termcolor import colored, cprint

from fake_data_factories.company_user_factories import create_company_users


async def fill_all_data():
    """
    Генерация тестовых данных для всех сущностей.
    """
    cprint(
        colored('Начинаем генерацию тестовых данных...', 'red', attrs=['reverse', 'blink']),
    )

    await create_company_users(count=3, company_id=6)

    cprint(
        colored('Генерация завершена!', 'red', attrs=['reverse', 'blink']),
    )


if __name__ == '__main__':
    asyncio.run(fill_all_data())
