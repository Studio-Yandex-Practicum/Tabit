# TODO:
# В данном модуле содержатся функции всех синхронных валидаторов.
# В будущем нужно переписать все функции в корутины и поместить
# обновлённые валидаторы в соответствующие модули.

from fastapi import HTTPException, status

from src.features_v1.constants import TextError
from src.models import (
    Company, CompanyUser,
    Meeting, MeetingStatus,
    Problem, ProblemStatus,
    Task, TaskStatus
)


# ------------------------------------------------------------------------------
# Валидатор из common_validators.py
# ------------------------------------------------------------------------------
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


# ------------------------------------------------------------------------------
# Валидатор из meeting_validators.py
# ------------------------------------------------------------------------------
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


# ------------------------------------------------------------------------------
# Валидаторы из problem_validators.py
# ------------------------------------------------------------------------------
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


# ------------------------------------------------------------------------------
# Единственный валидатор из task_validators.py
# ------------------------------------------------------------------------------
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


# ------------------------------------------------------------------------------
# Валидаторы из user_validators.py
# ------------------------------------------------------------------------------
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