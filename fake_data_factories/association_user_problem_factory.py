from uuid import UUID

from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from termcolor import cprint

from fake_data_factories.constants import ColorCPrintConstants
from fake_data_factories.utils import start_and_end
from src.core.database.sc_db_session import sc_session
from src.models import AssociationUserProblem


class AssociationUserProblemFactory(AsyncSQLAlchemyFactory):
    """
    Фабрика генерации данных ассоциативной модели `AssociationUserProblem`.

    Поля:
        - `left_id`: Обязательное поле. Ссылка на пользователя Tabit. \
            Должен быть создан объект `CompanyUser`, чтобы передать полю id (типа uuid).
        - `right_id`: Обязательное поле. Ссылка на проблему. \
            Должен быть создан объект `Problem`, чтобы передать полю id.
        - `status`: Обязательное поле. Значение по умолчанию - True.
    """

    left_id: UUID
    right_id: int
    status: bool = True

    class Meta:
        model = AssociationUserProblem
        sqlalchemy_session = sc_session


@start_and_end(__name__)
async def create_user_problem_associations(
    user_id: UUID,
    problem_ids: list[int],
) -> list[AssociationUserProblem]:
    """
    Создать запись(-и) в таблицу объекта `AssociationUserProblem`.

    Поля:
        - `user_id`: uuid пользователя Tabit;
        - `problem_ids`: список id проблем.

    Функция возвращате список созданных записей.
    """
    user_problem_associations = []
    for problem_id in problem_ids:
        user_problem_associations.append(
            await AssociationUserProblemFactory.create(
                left_id=user_id,
                right_id=problem_id,
            )
        )
    cprint(
        f'Создано {len(problem_ids)} ассоциативных связей проблема-пользователь '
        f'от пользователя с id: {user_id}',
        ColorCPrintConstants.green,  # type: ignore
    )
    return user_problem_associations
