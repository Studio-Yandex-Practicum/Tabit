import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.features_v1.validators.common_validators import (
    validator_check_object_exists,
)
from src.crud import CRUDBase


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
