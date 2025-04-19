import asyncio
from random import choice
from uuid import UUID

import factory
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from termcolor import cprint

from fake_data_factories.association_user_task_factory import create_user_task_associations
from fake_data_factories.constants import (
    DEFAULT_TASK_DESCRIPTION_LENGTH,
    DEFAULT_TASK_NAMES,
    FAKER_TASK_COUNT,
    ColorCPrint,
)
from fake_data_factories.problem_factory import create_problems
from fake_data_factories.utils import start_and_end
from src.core.constants import ZERO
from src.core.database.sc_db_session import sc_session
from src.models import Task, TaskStatus


class TaskFactory(AsyncSQLAlchemyFactory):
    """
    Фабрика для генерации данных задачи.

    Поля:
        name: Название задачи.
        description: Описание.
        date_completion: Крайняя дата исполнения задачи.
        owner_id: Автор задачи. Внешний ключ.
        problem_id: Идентификатор проблемы, к которой относится задача.
        status: Статус выполнения задачи.
        transfer_counter: Счетчик переносов даты решения задач.
    """

    name: factory.LazyFunction = factory.LazyFunction(lambda: choice(DEFAULT_TASK_NAMES))
    description: factory.Faker = factory.Faker(
        'text', max_nb_chars=DEFAULT_TASK_DESCRIPTION_LENGTH
    )
    date_completion: factory.Faker = factory.Faker('future_date')
    owner_id: UUID
    problem_id: str
    status: factory.LazyFunction = factory.LazyFunction(lambda: choice(list(TaskStatus)))
    transfer_counter: int = ZERO

    class Meta:
        model = Task
        sqlalchemy_session = sc_session


@start_and_end(__name__)
async def create_tasks(count: int = FAKER_TASK_COUNT, **kwargs) -> None:
    """
    Функция для для пакетного создания задач.

    Функция создает указанное количество задач. Можно передать следуюшие аргументы:
        count: Количество задач для создания.
        owner_id: ID владельца задач.
        problem_id: ID проблемы, с которой связаны задачи.
    """
    if 'problem_id' not in kwargs or 'owner_id' not in kwargs:
        problem = next(iter(await create_problems(count=1)), None)
        kwargs['problem_id'] = problem.id
        kwargs['owner_id'] = problem.owner_id
    tasks = await TaskFactory.create_batch(count, **kwargs)
    cprint(
        f'Создано {count} задач в проблеме c id: {kwargs["problem_id"]} '
        f'от пользователя с id: {kwargs["owner_id"]}',
        ColorCPrint.green,  # type: ignore
    )
    await create_user_task_associations(
        user_id=kwargs['owner_id'], task_ids=[task.id for task in tasks]
    )


if __name__ == '__main__':
    asyncio.run(create_tasks())
