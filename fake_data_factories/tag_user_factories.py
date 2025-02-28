import factory
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from termcolor import cprint

from fake_data_factories.company_factories import CompanyFactory
from src.database.alembic_models import TagUser
from src.database.sc_db_session import sc_session


class TagUserFactory(AsyncSQLAlchemyFactory):
    name: str = factory.Faker('word')
    company_id: int

    class Meta:
        model = TagUser
        sqlalchemy_session = sc_session


async def create_company_department(count, **kwargs):
    """
    Функция для наполнения таблицы бд TagUser.
    Если функция запускается напрямую из текущего модуля, для этих департаментов создается
    компания, id этой компании передается в фабрику.
    Если функция запускается через импорт, в неё нужно передать именованный аргумент company_id,
    чтобы он попал в kwargs для заполнения обязательного поля фабрики company_id.
    """
    if __name__ == '__main__':
        company = await CompanyFactory.create()
        kwargs['company_id'] = company.id
    await TagUserFactory.create_batch(count, **kwargs)
    cprint(f'Создано {count} департаментов компании c id: {kwargs["company_id"]}', 'green')
