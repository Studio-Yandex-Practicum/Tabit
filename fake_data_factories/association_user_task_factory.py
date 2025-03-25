from uuid import UUID

from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from termcolor import cprint

from fake_data_factories.constants import Color
from fake_data_factories.utils import start_and_end
from src.database.sc_db_session import sc_session
from src.problems.models.association_models import AssociationUserTask


class AssociationUserTaskFactory(AsyncSQLAlchemyFactory):
    """
    Фабрика генерации данных ассоциативной модели AssociationUserTask.

    Поля:
        - left_id: Обязательное поле. Ссылка на пользователя Tabit.
        - right_id: Обязательное поле. Ссылка на задачу.
    """

    left_id: UUID
    right_id: int

    class Meta:
        model = AssociationUserTask
        sqlalchemy_session = sc_session


@start_and_end(__name__)
async def create_user_task_associations(
    user_id: UUID,
    task_ids: list[int],
) -> None:
    """
    Создать запись в таблицу объекта AssociationUserTask.

    Поля:
        - user_id: uuid пользователя Tabit;
        - task_ids: список id задач.
    """
    for task_id in task_ids:
        await AssociationUserTaskFactory(left_id=user_id, right_id=task_id)
    cprint(
        f'Создано {len(task_ids)} ассоциативных связей задача-пользователь '
        f'от пользователя с id: {user_id}',
        Color.green,  # type: ignore
    )
