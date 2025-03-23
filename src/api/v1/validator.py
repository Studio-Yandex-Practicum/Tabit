"""
Валидаторы для эндпоинтов.
"""

from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.constants import TextError
from src.constants import TextError as ErrorText
from src.crud import CRUDBase
from src.companies.models import Company
from src.users.models import UserTabit
from src.problems.models import Problem, Meeting, Task
from src.problems.models.enums import StatusMeeting, StatusProblem, StatusTask


async def validator_check_object_exists(
    session: AsyncSession,
    model_crud: CRUDBase,
    object_id: int | UUID | None = None,
    object_slug: str | None = None,
    message: str = ErrorText.NOT_FOUND,
):
    """Проверит наличие и вернет объект из таблицы по id или slug."""
    object_model = (
        await model_crud.get_or_404(session, object_id, message)
        if object_id
        else (await model_crud.get_by_slug(session, object_slug, raise_404=True))
    )
    return object_model


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


def check_user_is_active(user):
    """Проверит, что пользователь передан и является активным. Иначе ошибка 400."""
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=TextError.LOGIN,
        )


def validate_user_from_company(user: UserTabit, company: Company):
    """
    Валидатор, проверит что пользователь из данной компании.
    Иначе ошибка 403
    """
    if user.company_id != company.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=TextError.FORBIDDEN_FROM_COMPANY.format(company.name),
        )


def validate_owner_object(user: UserTabit, row_model):
    """
    Валидатор, проверит что у переданной модели автор переданный пользователь.
    Иначе ошибка 403
    """
    if user.id != row_model.owner.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=TextError.FORBIDDEN_OWNER,
        )


def validate_is_member_problem(user: UserTabit, problem: Problem):
    """
    Валидатор, проверит что пользователь является участником проблемы.
    Иначе ошибка 403
    """
    if user in problem.members:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=TextError.FORBIDDEN_NOT_MEMBER,
        )


def validate_close_problem(problem: Problem):
    """
    Валидатор, проверит что проблема ещё не решена.
    Иначе ошибка 422
    """
    if problem.status == StatusProblem.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=TextError.CLOSE_PROBLEM,
        )


def validate_meeting_was_held(meeting: Meeting):
    """
    Валидатор, проверит что встреча не проведена.
    Иначе ошибка 422
    """
    if meeting.status == StatusMeeting.HELD:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=TextError.MEETING_WAS_HELD,
        )


def validate_task_completed(task: Task):
    """
    Валидатор, проверит что встреча не проведена.
    Иначе ошибка 422
    """
    if task.status == StatusTask.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=TextError.TASK_COMPLETED,
        )
