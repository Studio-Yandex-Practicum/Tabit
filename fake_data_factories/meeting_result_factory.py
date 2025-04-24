import asyncio
from random import choice
from uuid import UUID

import factory
from async_factory_boy.factory.sqlalchemy import AsyncSQLAlchemyFactory
from termcolor import cprint

from fake_data_factories.company_factories import create_companies
from fake_data_factories.company_user_factories import create_company_users
from fake_data_factories.constants import (
    DEFAULT_MEETING_FEEDBACK,
    FAKER_MEETINGS_RESULT_COUNT,
    ColorCPrint,
)
from fake_data_factories.meeting_factory import create_meetings
from fake_data_factories.problem_factory import create_problems
from fake_data_factories.utils import start_and_end
from src.core.database.sc_db_session import sc_session
from src.models import (
    MeetingResult,
    MeetingResultEngagementEnum,
    MeetingResultEnum,
    MeetingResultSolutionEnum,
)


class MeetingResultFactory(AsyncSQLAlchemyFactory):
    """
    Фабрика для генерации данных встреч.

    Поля:
        - `meeting_id`: Обязательное поле. \
            Должен быть создан объект `Meeting`, чтобы передать полю id.
        - `owner_id`: Обязательное поле. \
            Должен быть создан объект `CompanyUser`, чтобы передать полю id (типа uuid).
        - `meeting_result`: Обязательное поле. Генерируется случайным выбором из MeetingResultEnum.
        - `participant_engagement: Обязательное поле. \
            Генерируется случайным выбором из MeetingResultEngagementEnum.
        - `problem_solution`: Обязательное поле. \
            Генерируется случайным выбором из MeetingResultSolutionEnum.
        - `meeting_feedback`: Необязательное поле. \
            Генерируется случайным выбором из DEFAULT_MEETING_FEEDBACK
    """

    meeting_id: int
    owner_id: UUID
    meeting_result: factory.LazyFunction = factory.LazyFunction(
        lambda: choice(list(MeetingResultEnum))
    )
    participant_engagement: factory.LazyFunction = factory.LazyFunction(
        lambda: choice(list(MeetingResultEngagementEnum))
    )
    problem_solution: factory.LazyFunction = factory.LazyFunction(
        lambda: choice(list(MeetingResultSolutionEnum))
    )
    meeting_feedback: factory.LazyFunction = factory.LazyFunction(
        lambda: choice(DEFAULT_MEETING_FEEDBACK)
    )

    class Meta:
        model = MeetingResult
        sqlalchemy_session = sc_session


@start_and_end(__name__)
async def create_meeting_result(
    count: int = FAKER_MEETINGS_RESULT_COUNT, **kwargs
) -> list[MeetingResult]:
    """
    Создать запись(-и) в таблицу объекта `MeetingResult`.

    Если функция запускается напрямую из текущего модуля, для этих проблем создаются:
    - компания (id компании передаётся в фабрику создания пользователя);
    - пользователь Tabit (uuid пользователя передаётся в фабрику);
    - проблема (id проблемы передаётся в фабрику создания встречи);
    - встреча (id встречи передаётся в фабрику)

    Если функция запускается через импорт, в неё нужно передать именованные аргументы \
    `owner_id` и 'meetings'. Если не передать 'owner_id', запустится фабрика создания \
    пользователей компании с предварительным запуском фабрики создания компании, далее \
    запустится фабрика создания проблемы от авторства созданного фабрикой пользователя, затем \
    будет создан список встреч, число которых будет равно параметру count, переданному в \
    данную функцию.

    Функция возвращает список встреч.
    """
    if 'owner_id' not in kwargs:
        company = next(iter(await create_companies(count=1)), None)
        user_tabit = next(iter(await create_company_users(count=1, company_id=company.id)), None)
        kwargs['owner_id'] = user_tabit.id
        problem = next(
            iter(await create_problems(count=1, owner_id=user_tabit.id, company_id=company.id)),
            None,
        )
        meetings = await create_meetings(
            count=count, owner_id=user_tabit.id, problem_id=problem.id
        )
        kwargs['meetings'] = meetings
    meetings_results = []
    for meeting in kwargs['meetings']:
        meetings_results.append(
            await MeetingResultFactory.create(meeting_id=meeting.id, owner_id=kwargs['owner_id'])
        )
    cprint(
        f'Создано {count} результатов встреч от пользователя с id: {kwargs["owner_id"]}',
        ColorCPrint.green,  # type: ignore
    )
    return meetings_results


if __name__ == '__main__':
    asyncio.run(create_meeting_result())
