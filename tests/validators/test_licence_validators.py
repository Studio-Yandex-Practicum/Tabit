import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, MagicMock

from src.features_v1.validators.license_validators import (
    validate_license_exists,
    validate_license_name,
)


@pytest.mark.asyncio
async def test_validate_license_exists_found():
    """Проверка, что функция ничего не делает, если лицензия найдена."""
    session = MagicMock()
    mock_crud = AsyncMock()
    mock_crud.get = AsyncMock(return_value={"id": 1})

    import src.features_v1.validators.license_validators as validators
    validators.license_type_crud = mock_crud

    await validate_license_exists(session, 1)
    mock_crud.get.assert_awaited_once_with(session, 1)


@pytest.mark.asyncio
async def test_validate_license_exists_not_found():
    """Проверка, что выбрасывается исключение, если лицензия не найдена."""
    session = MagicMock()
    mock_crud = AsyncMock()
    mock_crud.get = AsyncMock(return_value=None)

    import src.features_v1.validators.license_validators as validators
    validators.license_type_crud = mock_crud

    with pytest.raises(HTTPException) as exc:
        await validate_license_exists(session, 42)
    assert exc.value.status_code == 400
    assert 'не найдена' in exc.value.detail


@pytest.mark.asyncio
async def test_validate_license_name_not_exists():
    """Проверка, что функция ничего не делает, если имя лицензии уникально."""
    session = MagicMock()
    mock_crud = AsyncMock()
    mock_crud.is_license_name_exists = AsyncMock(return_value=False)

    import src.features_v1.validators.license_validators as validators
    validators.license_type_crud = mock_crud

    await validate_license_name(session, "Уникальное имя")
    mock_crud.is_license_name_exists.assert_awaited_once_with(session, "Уникальное имя")


@pytest.mark.asyncio
async def test_validate_license_name_already_exists():
    """Проверка, что выбрасывается исключение, если имя лицензии уже занято."""
    session = MagicMock()
    mock_crud = AsyncMock()
    mock_crud.is_license_name_exists = AsyncMock(return_value=True)

    import src.features_v1.validators.license_validators as validators
    validators.license_type_crud = mock_crud

    with pytest.raises(HTTPException) as exc:
        await validate_license_name(session, "Существующее имя")
    assert exc.value.status_code == 400
    assert 'уже существует' in exc.value.detail
