# TODO:
# В данном модуле собраны тесты для синхронных валидаторов,
# которые в будущем будут переписаны в асинхронном виде

from unittest.mock import MagicMock

import pytest
from fastapi import HTTPException, status

from src.features_v1.constants import TextError
from src.features_v1.validators.sync_validators import (
    check_user_is_active,
    validate_close_problem,
    validate_is_member_problem,
    validate_meeting_was_held,
    validate_owner_object,
    validate_task_completed,
    validate_user_from_company,
    validator_check_not_is_superuser,
)
from src.models import Meeting, MeetingStatus, ProblemStatus, TaskStatus


# ------------------------------------------------------------------------------
# Тесты для из common_validators.py
# ------------------------------------------------------------------------------
class DummyModel:
    def __init__(self, owner_id):
        self.owner = DummyOwner(owner_id)


class DummyOwner:
    def __init__(self, id):
        self.id = id


class DummyUser:
    def __init__(self, id):
        self.id = id


def test_validate_owner_object_valid():
    """Проверка: пользователь совпадает с владельцем — ошибки нет."""
    user = DummyUser(id=1)
    row_model = DummyModel(owner_id=1)
    validate_owner_object(user, row_model)  # не должно быть исключения


def test_validate_owner_object_forbidden():
    """Проверка: пользователь не совпадает с владельцем — ошибка 403."""
    user = DummyUser(id=1)
    row_model = DummyModel(owner_id=2)

    with pytest.raises(HTTPException) as exc:
        validate_owner_object(user, row_model)

    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc.value.detail == TextError.FORBIDDEN_OWNER


# ------------------------------------------------------------------------------
# Тест для из meeting_validators.py
# ------------------------------------------------------------------------------
def test_validate_meeting_was_held_raises():
    meeting = MagicMock(spec=Meeting)
    meeting.status = MeetingStatus.HELD
    with pytest.raises(HTTPException) as exc:
        validate_meeting_was_held(meeting)
    assert exc.value.status_code == 422


# ------------------------------------------------------------------------------
# Тесты для из problem_validators.py
# ------------------------------------------------------------------------------
def test_validate_close_problem_completed_raises():
    problem = MagicMock(status=ProblemStatus.COMPLETED)

    with pytest.raises(HTTPException) as exc:
        validate_close_problem(problem)
    assert exc.value.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert exc.value.detail == TextError.CLOSE_PROBLEM


def test_validate_is_member_problem_forbidden():
    user = MagicMock()
    problem = MagicMock(members=[user])

    with pytest.raises(HTTPException) as exc:
        validate_is_member_problem(user, problem)
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc.value.detail == TextError.FORBIDDEN_NOT_MEMBER


# ------------------------------------------------------------------------------
# Тесты для из task_validators.py
# ------------------------------------------------------------------------------
def test_validate_task_completed_raises():
    task = MagicMock()
    task.status = TaskStatus.COMPLETED

    with pytest.raises(HTTPException) as exc_info:
        validate_task_completed(task)

    assert exc_info.value.status_code == 422
    assert exc_info.value.detail == TextError.TASK_COMPLETED


def test_validate_task_completed_ok():
    task = MagicMock()
    task.status = TaskStatus.IN_PROGRESS

    # Не должно выбрасываться исключение
    validate_task_completed(task)


# ------------------------------------------------------------------------------
# Тесты для из user_validators.py
# ------------------------------------------------------------------------------
def test_check_user_is_active_raises():
    user = MagicMock(is_active=False)
    with pytest.raises(HTTPException) as exc:
        check_user_is_active(user)
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST


def test_check_user_is_active_valid():
    user = MagicMock(is_active=True)
    assert check_user_is_active(user) is None


def test_validator_check_not_is_superuser_raises():
    user = MagicMock(is_superuser=True)
    with pytest.raises(HTTPException) as exc:
        validator_check_not_is_superuser(user)
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc.value.detail == TextError.IS_SUPERUSER


def test_validator_check_not_is_superuser_valid():
    user = MagicMock(is_superuser=False)
    assert validator_check_not_is_superuser(user) is None


def test_validate_user_from_company_raises():
    user = MagicMock(company_id=1)
    company = MagicMock(id=2, name='Company X')
    with pytest.raises(HTTPException) as exc:
        validate_user_from_company(user, company)
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    assert TextError.FORBIDDEN_FROM_COMPANY.format(company.name) in exc.value.detail


def test_validate_user_from_company_valid():
    user = MagicMock(company_id=1)
    company = MagicMock(id=1, name='Company X')
    assert validate_user_from_company(user, company) is None
