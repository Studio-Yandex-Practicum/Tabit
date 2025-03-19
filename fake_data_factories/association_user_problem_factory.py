import asyncio
from uuid import UUID

from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from sqlalchemy import func, select
from termcolor import cprint

from fake_data_factories.company_factories import CompanyFactory
from fake_data_factories.company_user_factories import CompanyUserFactory
from fake_data_factories.problem_factory import create_problems
from src.database.sc_db_session import sc_session
from src.problems.models.association_models import AssociationUserProblem


class AssociationUserProblemFactory(AsyncSQLAlchemyFactory):
    """
    Фабрика генерации данных ассоциативной модели `AssociationUserProblem`.

    Поля:
        - `id`. Обязательное поле. \
            Должно передаваться максимальное значение id в таблице + 1.
        - `left_id`: Обязательное поле. Ссылка на пользователя Tabit. \
            Должен быть создан объект `UserTabit`, чтобы передать полю id (типа uuid).
        - `right_id`: Обязательное поле. Ссылка на проблему. \
            Должен быть создан объект `Problem`, чтобы передать полю id.
        - `status`: Обязательное поле. Значение по умолчанию - True.
    """

    id: int
    left_id: UUID
    right_id: int
    status: bool = True

    class Meta:
        model = AssociationUserProblem
        sqlalchemy_session = sc_session


async def create_user_problem_associations(
    user_id: UUID,
    problem_ids: list[int],
) -> None:
    """
    Создать запись(-и) в таблицу объекта `AssociationUserProblem`.

    Поля:
        - `user_id`: uuid пользователя Tabit;
        - `problem_ids`: список id проблем.
    """
    for problem_id in problem_ids:
        result = await sc_session.execute(select(func.max(AssociationUserProblem.id)))
        new_id = (result.scalar() or 0) + 1
        await AssociationUserProblemFactory.create(
            id=new_id,
            left_id=user_id,
            right_id=problem_id,
        )
    cprint(
        f'Создано {len(problem_ids)} ассоциативных связей проблема-пользователь '
        f'от пользователя с id: {user_id}',
        'green',
    )


async def main() -> None:
    """
    Запустить создание ассоциативных связей из модуля.

    Примечание: запускается фабрика проблем, которая создаёт компанию, \
        пользователя этой компании и пакет проблем от его авторства.
    """
    company = await CompanyFactory()
    user_tabit = await CompanyUserFactory(company_id=company.id)
    problems = await create_problems()
    problem_ids = [problem.id for problem in problems]
    await create_user_problem_associations(
        user_id=user_tabit.id,
        problem_ids=problem_ids,
    )


if __name__ == '__main__':
    asyncio.run(main())
