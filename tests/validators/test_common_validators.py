import pytest
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.features_v1.validators.common_validators import (
    validator_check_object_exists,
    validate_owner_object,
)
from src.crud import CRUDBase
from src.features_v1.constants import TextError


class DummyModel:
    def __init__(self, owner_id):
        self.owner = DummyOwner(owner_id)


class DummyOwner:
    def __init__(self, id):
        self.id = id


class DummyUser:
    def __init__(self, id):
        self.id = id


@pytest.mark.asyncio
async def test_validator_check_object_exists_by_id(mocker):
    """Проверка получения объекта по ID."""
    session = mocker.Mock(spec=AsyncSession)
    model_crud = mocker.Mock(spec=CRUDBase)
    expected_obj = object()
    model_crud.get_or_404 = mocker.AsyncMock(return_value=expected_obj)

    result = await validator_check_object_exists(session, model_crud, object_id=1)

    assert result is expected_obj
    model_crud.get_or_404.assert_awaited_once_with(session, 1)


@pytest.mark.asyncio
async def test_validator_check_object_exists_by_slug(mocker):
    """Проверка получения объекта по slug."""
    session = mocker.Mock(spec=AsyncSession)
    model_crud = mocker.Mock(spec=CRUDBase)
    expected_obj = object()
    model_crud.get_by_slug = mocker.AsyncMock(return_value=expected_obj)

    result = await validator_check_object_exists(session, model_crud, object_slug="test-slug")

    assert result is expected_obj
    model_crud.get_by_slug.assert_awaited_once_with(session, "test-slug", raise_404=True)


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