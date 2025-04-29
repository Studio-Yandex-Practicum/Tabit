from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException, status

from src.features_v1.constants import TextError
from src.features_v1.validators.user_validators import (
    BaseUserValidator,
    check_telegram_username_for_duplicates,
    validate_field_members,
    validate_password,
    validate_user_not_exists,
)


@pytest.mark.asyncio
async def test_validate_user_not_exists_raises():
    mock_user_manager = MagicMock()
    mock_user_manager.user_db.get_by_email = AsyncMock(return_value=True)
    user_data = MagicMock(email='test@example.com')
    with pytest.raises(HTTPException) as exc:
        await validate_user_not_exists(user_data, mock_user_manager)
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc.value.detail == TextError.EXISTS_EMAIL


@pytest.mark.asyncio
async def test_validate_user_not_exists_valid():
    mock_user_manager = MagicMock()
    mock_user_manager.user_db.get_by_email = AsyncMock(return_value=None)
    user_data = MagicMock(email='test@example.com')
    assert await validate_user_not_exists(user_data, mock_user_manager) is None


@pytest.mark.asyncio
async def test_validate_password_valid():
    mock_user_manager = MagicMock()
    mock_user_manager.validate_password = AsyncMock(return_value=None)
    user_data = MagicMock(password='validpassword')
    assert await validate_password(user_data, mock_user_manager) is None


@pytest.mark.asyncio
async def test_check_telegram_username_for_duplicates_raises():
    session = AsyncMock()
    validator = BaseUserValidator(session=session)
    validator.check_telegram_username_exists = AsyncMock(return_value=True)

    # directly use the mocked method
    BaseUserValidator.check_telegram_username_exists = validator.check_telegram_username_exists

    with pytest.raises(HTTPException) as exc:
        await check_telegram_username_for_duplicates('existing_user', session)
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc.value.detail == TextError.EXISTS_USERNAME


@pytest.mark.asyncio
async def test_validate_field_members_invalid_user():
    session = AsyncMock()
    validator = BaseUserValidator(session=session)
    validator.get_user_by_uuid = AsyncMock(return_value=None)

    BaseUserValidator.get_user_by_uuid = validator.get_user_by_uuid

    with pytest.raises(HTTPException) as exc:
        await validate_field_members(session, [1], company_id=1)
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_validate_field_members_not_from_company():
    session = AsyncMock()
    user = MagicMock(company_id=2)
    validator = BaseUserValidator(session=session)
    validator.get_user_by_uuid = AsyncMock(return_value=user)

    BaseUserValidator.get_user_by_uuid = validator.get_user_by_uuid

    with pytest.raises(HTTPException) as exc:
        await validate_field_members(session, [1], company_id=1)
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
