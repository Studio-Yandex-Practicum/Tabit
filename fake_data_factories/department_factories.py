import asyncio
import uuid
from copy import deepcopy

import factory
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from termcolor import cprint

from fake_data_factories.company_factories import CompanyFactory
from fake_data_factories.constants import DEFAULT_DEPARTMENT_NAMES, FAKER_DEPARTMENT_COUNT
from src.companies.models.models import Department
from src.database.sc_db_session import sc_session

available_departments_names = deepcopy(DEFAULT_DEPARTMENT_NAMES)


class DeparmentFactory(AsyncSQLAlchemyFactory):
    """
    Фабрика генерации данных департаментов компании.

    Поля:
        name: Обязатьльное поле. Выбирается поочередно из списка available_departments_names.
        company_id: Обязательное поле. При создании объекта фабрики: create() create_batch(),
        необходимо передавать в аргументы фабрики.
        slug: Обязательное поле. Slug генерируется библиотекой uuid.

    Важно! Поле name НЕ уникально в модели Department, но, создание двух и более департаментов
    для одной компании с одинаковым значением в поле name запрещено UniqueConstraint.
    Соответственно, для создаваемых департаментов поле name берется поочередно из списка
    available_departments_names, после чего они будут генерироваться в формате:
    `Отдел-uuid.uuid4().hex[:4]`
    """

    name: factory.LazyFunction = factory.LazyFunction(
        lambda: available_departments_names.pop(0)
        if available_departments_names
        else f'Отдел-{uuid.uuid4().hex[:4]}'
    )
    company_id: int
    slug: factory.LazyFunction = factory.LazyFunction(lambda: uuid.uuid4().hex[:6])

    class Meta:
        model = Department
        sqlalchemy_session = sc_session


async def create_company_department(count=FAKER_DEPARTMENT_COUNT, **kwargs):
    """
    Функция для наполнения таблицы бд Department.
    Если функция запускается напрямую из текущего модуля, для этих департаментов создается
    компания, id этой компании передается в фабрику.
    Если функция запускается через импорт, в неё нужно передать именованный аргумент company_id,
    чтобы он попал в kwargs для заполнения обязательного поля фабрики company_id.
    """
    if __name__ == '__main__':
        company = await CompanyFactory.create()
        kwargs['company_id'] = company.id
    await DeparmentFactory.create_batch(count, **kwargs)
    cprint(f'Создано {count} департаментов компании c id: {kwargs["company_id"]}', 'green')


if __name__ == '__main__':
    asyncio.run(create_company_department())
