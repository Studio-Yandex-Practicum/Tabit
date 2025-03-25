import asyncio

from termcolor import colored, cprint

from fake_data_factories.company_factories import create_companies
from fake_data_factories.company_user_factories import create_company_users
from fake_data_factories.constants import (
    FAKER_COMPANY_COUNT,
    FAKER_DEPARTMENT_COUNT,
    FAKER_TASK_COUNT,
    FAKER_USER_COUNT,
    LICENSE_TYPE_COUNT,
)
from fake_data_factories.department_factories import create_company_department
from fake_data_factories.license_type_factories import create_license_type
from fake_data_factories.message_feed_factory import create_message_feeds
from fake_data_factories.problem_factory import create_problems
from fake_data_factories.tabit_user_factories import create_tabit_admin_users
from fake_data_factories.task_factory import create_tasks


async def fill_all_data():
    """
    Генерация тестовых данных для всех сущностей.

    Шаги заполнения бд:
        1. companies: Заполняет бд `count` количеством компаний.
        2. Циклом по созданным компаниям, для каждой компании создает count работников
        компании(1 из них админ), и count департаментов.
        3. Заполняет бд count админами Tabit.
        4. Заполняет таблицу проблем (для этого создаёт компанию и пользователя этой компании).
        5. Заполняет ассоциативную таблицу пользователь-проблема (созданный на предыдущем этапе \
            пользователь будет автором этих проблем).
        6. Заполняет таблицу ленты сообщений (для первой проблемы, созданной на шаге 4, \
            создаются ленты сообщений от автора проблемы (чтобы гарантировать принадлежность \
            автора проблемы и ленты сообщений одной организации)).
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
        company_users = await create_company_users(count=FAKER_USER_COUNT, company_id=company.id)
        for company_user in company_users:
            if company_user.role != 'Админ':
                problem = next(
                    iter(
                        await create_problems(
                            count=1, company_slug=company.slug, owner_id=company_user.id
                        )
                    ),
                    None,
                )
                await create_message_feeds(
                    count=1, problem_id=problem.id, owner_id=problem.owner_id
                )
                await create_tasks(
                    count=FAKER_TASK_COUNT, problem_id=problem.id, owner_id=company_user.id
                )
        await create_company_department(count=FAKER_DEPARTMENT_COUNT, company_id=company.id)
    await create_tabit_admin_users(count=FAKER_USER_COUNT)

    cprint(
        colored('Генерация завершена!', 'red', attrs=['reverse', 'blink']),
    )


if __name__ == '__main__':
    asyncio.run(fill_all_data())
