"""Модуль валидаторов эндпоинтов Company.py."""

import random

from fastapi import Depends, HTTPException, status
from fastapi_users.exceptions import InvalidPasswordException
from fastapi_users.manager import BaseUserManager
from slugify import slugify
from sqlalchemy import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth.managers import get_user_manager
from src.core.database.db_depends import get_async_session
from src.crud import (
    CRUDBase,
    comment_crud,
    company_crud,
    department_crud,
    license_type_crud,
    meeting_crud,
    message_feed_crud,
    moderator_crud,
    problem_crud,
    result_meeting_crud,
    task_crud,
    user_comment_association_crud,
    user_crud,
)
from src.features_v1.constants import Length, TextError
from src.models import (
    AssociationUserComment,
    CommentFeed,
    Company,
    CompanyUser,
    Department,
    Meeting,
    MeetingStatus,
    Problem,
    ProblemStatus,
    Task,
    TaskStatus,
)
from src.schemas import UserCreateSchema


async def check_department_name_duplicate(
    company_id: int,
    department_name: str,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """
    Проверяет есть ли уже отдел с таким именем.
    Args:
        company_id (int): id компании.
        department_name (str): имя отдела, которое проверяется.
        session (AsyncSession): Асинхронная сессия SQLAlchemy.
    Raises:
        HTTPException: Если отдел с таким именем уже существует,
                        возвращает ошибку 400 (BAD REQUEST).
    """
    departments = await department_crud.get_multi(
        session=session, filters={'company_id': company_id, 'name': department_name}
    )
    if departments:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=TextError.DEPARTMENT_EXIST,
        )


async def check_slug_duplicate(
    db_obj: Department | Company,
    session: AsyncSession = Depends(get_async_session),
) -> str:
    """
    Метод проверки и формирования `slug` объектов Company или Department.
    Args:
        db_obj (Department | Company): объект отдела или компании.
        session (AsyncSession): Асинхронная сессия SQLAlchemy.
    """
    base_slug = slugify(db_obj.name)[: Length.SLUG]
    new_slug = base_slug
    crud = department_crud if isinstance(db_obj, Department) else company_crud
    while await crud.get_multi(session=session, filters={'slug': new_slug}):
        new_slug = f'{base_slug[: Length.SLUG - 6]}-{random.randint(1000, 9999)}'
    return new_slug


async def validate_user_not_exists(
    user_data: UserCreateSchema,
    user_manager: BaseUserManager = Depends(get_user_manager),
) -> None:
    """
    Проверяет, что пользователь с таким email не существует.
    Args:
        user_data (UserCreateSchema): данные пользователя.
        user_manager (BaseUserManager): менеджер для пользователя.
    Raises:
        HTTPException: Если пользователь с таким email уже существует,
                        возвращает ошибку 400 (BAD REQUEST).
    """
    if user_data.email:
        user = await user_manager.user_db.get_by_email(user_data.email)
        if user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=TextError.EXISTS_EMAIL
            )


async def validate_password(
    user_data: UserCreateSchema,
    user_manager: BaseUserManager = Depends(get_user_manager),
) -> None:
    """
    Проверяет, что пароль соответствует требованиям.
    Args:
        user_data (UserCreateSchema): данные пользователя.
        user_manager (BaseUserManager): менеджер для пользователя.
    Raises:
        HTTPException: Если пароль не соответствует требованиям,
                        возвращает ошибку 400 (BAD REQUEST).
    """
    if user_data.password:
        try:
            await user_manager.validate_password(user_data.password, user_data)
        except InvalidPasswordException:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=TextError.INVALID_PASSWORD
            )


async def validator_check_object_exists(
    session: AsyncSession,
    model_crud: CRUDBase,
    object_id: int | UUID | None = None,
    object_slug: str | None = None,
    message: str = TextError.NOT_FOUND,
):
    """Проверит наличие и вернет объект из таблицы по id или slug."""
    object_model = (
        await model_crud.get_or_404(session, object_id)
        if object_id
        else (await model_crud.get_by_slug(session, object_slug, raise_404=True))
    )
    return object_model


async def check_telegram_username_for_duplicates(username: str, session: AsyncSession) -> None:
    """
    Функция проверяет, что в БД не существует пользователя с переданным telegram_username.
    В случае, если пользователь существует, то выбрасывается ошибка HTTP 400.
    Параметры:
        username: telegram_username, переданный в запросе к API;
        session: асинхронная сессия SQLAlchemy;
    """
    if username:
        if await moderator_crud.get_by_telegram_username(username, session):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=TextError.INVALID_TELEGRAM_USERNAME
            )


async def check_user_company(
    user_company_id: int, company_slug: str, session: AsyncSession
) -> None:
    """
    Валидатор, проверяющий соответствие компании юзера и запрошенной компании.

    Параметры:
        user_company_id: значение company_id в объекте пользователя;
        company_slug: path-параметр, соответствующий slug запрашиваемой компании.
    """

    company = await company_crud.get_or_404(session, user_company_id)
    if company.slug != company_slug:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=TextError.WRONG_COMPANY)


async def check_company_problem(
    user_company_id: int, problem_id: int, session: AsyncSession
) -> None:
    """
    Валидатор, проверяющий соответствие связанной с проблемой компанией и компанией юзера.

    Параметры:
        user_company_id: значение company_id в объекте пользователя;
        problem_id: path-параметр, соответствующий id запрашиваемой проблемы.
    """
    problem = await problem_crud.get_or_404(session, problem_id)
    company = await company_crud.get_or_404(session, problem.company_id)
    if company.id != user_company_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=TextError.WRONG_PROBLEM)


async def check_message_feed_and_problem(
    message_feed_id: int, problem_id: int, session: AsyncSession
) -> None:
    """
    Валидатор, проверяющий принадлежность запрошенного треда к запрошенной проблеме.

    Параметры:
        message_feed_id: path-параметр, соответствующий id запрашиваемого треда;
        problem_id: path-параметр, соответствующий id запрашиваемой проблемы.
    """
    message_feed = await message_feed_crud.get_or_404(session, message_feed_id)
    if message_feed.problem_id != problem_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=TextError.WRONG_MESSAGE_FEED
        )


async def check_comment_and_message_feed(
    comment_id: int, message_feed_id: int, session: AsyncSession
):
    """
    Валидатор, проверяющий принадлежность запрошенного комментария к запрошенному треду.

    Параметры:
        comment_id: path-параметр, соответствующий id запрашиваемого комментария;
        message_feed_id: path-параметр, соответствующий id запрашиваемого треда.

    Возвращает объект комментария в случае прохождения проверки.
    """
    comment = await comment_crud.get_or_404(session, comment_id)
    if comment.message_id != message_feed_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=TextError.WRONG_COMMENT)
    return comment


async def check_comment_owner(
    comment: CommentFeed, user_id: int, like_mode: bool = False
) -> CommentFeed:
    """
    Валидатор, сверяющий автора комментария и текущего пользователя.
    Работает в двух режимах, в зависимости от параметра like_mode:
        1) True: если текущий пользователь является автором комментария,то выбрасывается
           ошибка HTTP 400. Нужно для проверки возможности лайка комментария.
        2) False: если текущий пользователь не является автором комментария,то выбрасывается
           ошибка HTTP 403. Нужно для проверки возможности редактирования комментариев.

    Параметры:
        comment: объект комментария CommentFeed;
        user_id: UUID пользователя, сделавшего запрос к API;
        like_mode: опциональный параметр, определяет способ применения валидатора.
    """
    if like_mode:
        if comment.owner_id == user_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=TextError.LIKE_OWN_COMMENT
            )
    else:
        if comment.owner_id != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail=TextError.COMMENT_NOT_OWNER
            )


async def get_access_to_feeds(
    user_company_id: int, company_slug: str, problem_id: int, session: AsyncSession
) -> None:
    """
    Комбинация валидаторов check_user_company и check_company_problem.
    Используется для доступа к тредам.
    """
    await check_user_company(user_company_id, company_slug, session)
    await check_company_problem(user_company_id, problem_id, session)


async def get_access_to_comments(
    user_company_id: int,
    company_slug: str,
    problem_id: int,
    message_feed_id: int,
    session: AsyncSession,
) -> None:
    """
    Комбинация валидаторов check_user_company, check_company_problem и
    check_message_feed_and_problem. Используется для доступа к комментариям.
    """
    await get_access_to_feeds(user_company_id, company_slug, problem_id, session)
    await check_message_feed_and_problem(message_feed_id, problem_id, session)


async def check_comment_has_likes_from_user(
    user_id: int, comment_id: int, session: AsyncSession, like_mode: bool = False
) -> AssociationUserComment | None:
    """
    Валидатор, проверяющий, наличие лайка комментария от активного юзера.
    Работает в двух режимах, в зависимости от параметра like_mode:
        1) True: если запись о лайке обнаружена, то выбрасывается ошибка HTTP 400.
        2) False: если запись о лайке не обнаружена, то выбрасывается ошибка HTTP 400.
           В этом варианте возвращается объект модели AssociationUserComment.

    Параметры:
        user_id: UUID пользователя, сделавшего запрос к API;
        comment_id: path-параметр, соответствующий id запрашиваемого комментария;
        like_mode: опциональный параметр, определяет способ применения валидатора.
    """
    if like_mode:
        if await user_comment_association_crud.get(comment_id, user_id, session):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=TextError.REPEATED_LIKE
            )
    else:
        user_comment_obj = await user_comment_association_crud.get(comment_id, user_id, session)
        if not user_comment_obj:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=TextError.NOT_LIKED_COMMENT
            )
        return user_comment_obj


async def check_max_number_problems(session: AsyncSession, user: CompanyUser):
    """Проверит количество проблем, в которых участвует пользователь.

    Назначение:
        Установлен лимит количества проблем, в которых может участвовать пользователь.
    Параметры:
        user: экземпляр модели пользователя.
        session: Асинхронная сессия базы данных.
    Исключения:
        HTTPException: если превышен лимит.
    """
    all_open_problem = await problem_crud.get_all_open_problem_from_association_by_user_id(
        session,
        user,
    )
    if len(all_open_problem) >= Length.MAX_NUMBER_PROBLEM:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=TextError.PROBLEM_NUMBER.format(Length.MAX_NUMBER_PROBLEM),
        )


async def validate_field_members(
    session: AsyncSession,
    uuid_members: list[UUID] | None,
    company_id: int | None = None,
) -> None:
    """
    Проверит переданный список uuid пользователей на корректность uuid
    и принадлежность пользователей к переданной компании.

    Параметры
        session: Асинхронная сессия SQLAlchemy;
        uuid_members: список uuid пользователей;
        company_id: число - id компании из которой пользователи.
    """
    if not uuid_members:
        return
    for uuid in uuid_members:
        user = await user_crud.get(session, uuid)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=TextError.UUID_INVALID.format(uuid),
            )
        if company_id is not None and company_id != user.company_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=TextError.USER_NOT_FROM_COMPANY.format(uuid),
            )


def validate_close_problem(problem: Problem):
    """
    Валидатор, проверит что проблема ещё не решена.
    Иначе ошибка 422
    """
    if problem.status == ProblemStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=TextError.CLOSE_PROBLEM,
        )


def validate_owner_object(user: CompanyUser, row_model):
    """
    Валидатор, проверит что у переданной модели автор переданный пользователь.
    Иначе ошибка 403
    """
    if user.id != row_model.owner.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=TextError.FORBIDDEN_OWNER,
        )


def validate_user_from_company(user: CompanyUser, company: Company):
    """
    Валидатор, проверит что пользователь из данной компании.
    Иначе ошибка 403
    """
    if user.company_id != company.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=TextError.FORBIDDEN_FROM_COMPANY.format(company.name),
        )


async def check_problem_exists(problem_id: int, session: AsyncSession):
    """Проверяет существование проблемы по ID.

    Назначение:
        Валидирует, что проблема существует в базе данных по заданному ID.
    Параметры:
        problem_id: Целое число, представляющее ID проблемы для проверки.
        session: Асинхронная сессия базы данных.
    Возвращаемое значение:
        Проверенная проблема, если она существует.
    Исключения:
        HTTPException: Если проблема не найдена.
    """

    try:
        await problem_crud.get_or_404(session, problem_id)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=TextError.PROBLEM_NOT_FOUND
        )


async def check_meeting_title_unique(title: str, session: AsyncSession):
    """Проверяет уникальность названия встречи.

    Назначение:
        Валидирует, что название встречи уникально и не используется в базе данных.
    Параметры:
        title: Строка, представляющая название встречи для проверки.
        session: Асинхронная сессия базы данных.
    Исключения:
        HTTPException: Если название встречи уже используется.
    """

    if not await meeting_crud.get_meeting(title=title, session=session):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=TextError.MEETING_TITLE_ALREADY_IN_USE
        )


async def check_meeting_date_available(date_meeting: str, session: AsyncSession):
    """Проверяет доступность даты встречи.

    Назначение:
        Валидирует, что дата встречи доступна и не конфликтует с существующими встречами.
    Параметры:
        date_meeting: Строка, представляющая дату встречи для проверки.
        session: Асинхронная сессия базы данных.
    Исключения:
        HTTPException: Если дата встречи уже занята.
    """

    if not await meeting_crud.get_meeting(date_meeting=date_meeting, session=session):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=TextError.DATE_MEETING_ALREADY_IN_USE
        )


async def check_meeting_exists(meeting_id: int, session: AsyncSession):
    """Проверяет существование встречи по ID.

    Назначение:
        Валидирует, что встреча существует в базе данных по заданному ID.
    Параметры:
        meeting_id: Целое число, представляющее ID встречи для проверки.
        session: Асинхронная сессия базы данных.
    Возвращаемое значение:
        Проверенная встреча, если она существует.
    Исключения:
        HTTPException: Если встреча не найдена.
    """
    try:
        await meeting_crud.get_or_404(session, meeting_id)
    except HTTPException:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=TextError.MEETING_NOT_FOUND
        )


async def check_result_meeting_unique(meeting_id: int, owner: CompanyUser, session: AsyncSession):
    """Проверяет что один пользователь может создать только один результат встречи.

    Назначение:
        Валидирует, что данный пользователь еще не создавал результат данной встречи.
    Параметры:
        meeting_id: Идентификатор связанной встречи.
        owner_id: Идентификатор создателя результата.
        session: Асинхронная сессия базы данных.
    Исключения:
        HTTPException: Если результат данной встречи уже создан пользователем.
    """

    if await result_meeting_crud.get_multi(
        filters={'meeting_id': meeting_id, 'owner_id': owner.id}, session=session
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=TextError.NOT_UNIQUE_RESULT_MEETING
        )


async def check_task_exists(task_id: int, session: AsyncSession):
    """Проверяет, существует ли задача в базе данных.

    Args:
        task_id: Идентификатор задачи.
        session: Асинхронная сессия SQLAlchemy.

    Raises:
        HTTPException: Если задача не найдена.
    """
    return await task_crud.get_or_404(session, task_id, message=TextError.TASK_NOT_FOUND)


async def check_tasks_for_company_problem_exist(
    company_slug: str, problem_id: int, session: AsyncSession
):
    """Проверяет, существуют ли задачи в базе данных.

    Args:
        company_slug: Уникальный идентификатор компании
        problem_id: Идентификатор проблемы
        session: Асинхронная сессия SQLAlchemy.

    Raises:
        HTTPException: Если задача не найдена.
    """
    tasks = await task_crud.get_by_company_and_problem(session, company_slug, problem_id)
    if tasks is None or tasks == []:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=TextError.TASK_FOR_PROBLEM_NOT_FOUND,
        )


async def check_company_exists(company_slug: str, session: AsyncSession):
    """Проверяет существование компании по slug.

    Назначение:
        Валидирует, что компания существует в базе данных по заданному slug.
    Параметры:
        company_slug: Строка, представляющая slug компании для проверки.
        session: Асинхронная сессия базы данных.
    Возвращаемое значение:
        Проверенная компания, если она существует.
    Исключения:
        HTTPException: Если компания не найдена.
    """

    if not await company_crud.get_by_company_slug(session, company_slug):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=TextError.COMPANY_NOT_FOUND
        )


def validate_is_member_problem(user: CompanyUser, problem: Problem):
    """
    Валидатор, проверит что пользователь является участником проблемы.
    Иначе ошибка 403
    """
    if user in problem.members:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=TextError.FORBIDDEN_NOT_MEMBER,
        )


def validate_meeting_was_held(meeting: Meeting):
    """
    Валидатор, проверит что встреча не проведена.
    Иначе ошибка 422
    """
    if meeting.status == MeetingStatus.HELD:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=TextError.MEETING_WAS_HELD,
        )


def validate_task_completed(task: Task):
    """
    Валидатор, проверит что встреча не проведена.

    Иначе ошибка 422
    """
    if task.status == TaskStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=TextError.TASK_COMPLETED,
        )


def check_user_is_active(user):
    """Проверит, что пользователь передан и является активным. Иначе ошибка 400."""
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=TextError.LOGIN,
        )


def validator_check_not_is_superuser(
    user_model_object,
    message: str = TextError.IS_SUPERUSER,
) -> None:
    """
    Проверит, не является ли пользователь суперпользователем.
    Если является: выкинет ошибку 400.
    """
    if user_model_object.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
        )


async def check_company_and_department(
    company_id: int, department_id: int | None, session: AsyncSession
) -> None:
    """
    Функция проверяет существование объектов Company и Department с указанными id.
    Если объекты существуют, то далее проверяется наличие связи между ними.
    Параметры:
        company_id: id компании, переданный в запросе к API;
        department_id: id отдела, переданный в запросе к API;
        session: асинхронная сессия SQLAlchemy;
    """
    if not await company_crud.get(session, company_id):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=TextError.COMPANY_NOT_FOUND
        )
    if department_id:
        department = await department_crud.get(session, department_id)
        if not department:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=TextError.DEPARTMENT_NOT_FOUND,
            )
    else:
        return
    if department.company_id != company_id:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=TextError.WRONG_COMPANY_DEPARTMENT,
        )


async def validate_company_slug(session: AsyncSession, slug: str) -> None:
    """
    Проверяет, существует ли компания с таким slug в базе.

    :param session: Асинхронная сессия SQLAlchemy
    :param slug: Проверяемый slug
    :raises HTTPException: Если slug уже существует в БД
    """
    if await company_crud.is_company_slug_exists(session, slug):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Компания с таким slug '{slug}' уже существует.",
        )


async def validate_license_exists(session: AsyncSession, license_id: int) -> None:
    """
    Проверяет, существует ли лицензия с переданным license_id в базе данных.

    Args:
        session (AsyncSession): Асинхронная сессия SQLAlchemy.
        license_id (int): Идентификатор лицензии.

    Raises:
        HTTPException: Если лицензия с данным license_id не найдена.
    """
    license_exists = await license_type_crud.get(session, license_id)
    if not license_exists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Лицензия с id {license_id} не найдена.',
        )


async def validate_license_name(session: AsyncSession, license_name: str):
    """
    Проверяет, существует ли лицензия с данным именем.

    Args:
        session (AsyncSession): Асинхронная сессия SQLAlchemy.
        license_name (str): Название лицензии, которую нужно проверить.

    Raises:
        HTTPException: Если лицензия с таким именем уже существует,
                        возвращает ошибку 400 (BAD REQUEST).
    """
    if await license_type_crud.is_license_name_exists(session, license_name):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Лицензия с именем '{license_name}' уже существует.",
        )
