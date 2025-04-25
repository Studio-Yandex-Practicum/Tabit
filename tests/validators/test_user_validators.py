import pytest
from unittest.mock import AsyncMock, MagicMock
from fastapi import HTTPException, status

from src.features_v1.constants import TextError, ERROR_INVALID_TELEGRAM_USERNAME
from src.features_v1.validators.user_validators import (
    BaseUserValidator,
    validate_user_not_exists,
    validate_password,
    check_user_is_active,
    validator_check_not_is_superuser,
    validate_user_from_company,
    check_telegram_username_for_duplicates,
    validate_field_members,
)


@pytest.mark.asyncio
async def test_validate_user_not_exists_raises():
    mock_user_manager = MagicMock()
    mock_user_manager.user_db.get_by_email = AsyncMock(return_value=True)
    user_data = MagicMock(email="test@example.com")
    with pytest.raises(HTTPException) as exc:
        await validate_user_not_exists(user_data, mock_user_manager)
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc.value.detail == TextError.EXISTS_EMAIL


@pytest.mark.asyncio
async def test_validate_user_not_exists_valid():
    mock_user_manager = MagicMock()
    mock_user_manager.user_db.get_by_email = AsyncMock(return_value=None)
    user_data = MagicMock(email="test@example.com")
    assert await validate_user_not_exists(user_data, mock_user_manager) is None




@pytest.mark.asyncio
async def test_validate_password_valid():
    mock_user_manager = MagicMock()
    mock_user_manager.validate_password = AsyncMock(return_value=None)
    user_data = MagicMock(password="validpassword")
    assert await validate_password(user_data, mock_user_manager) is None


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
    company = MagicMock(id=2, name="Company X")
    with pytest.raises(HTTPException) as exc:
        validate_user_from_company(user, company)
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    assert TextError.FORBIDDEN_FROM_COMPANY.format(company.name) in exc.value.detail


def test_validate_user_from_company_valid():
    user = MagicMock(company_id=1)
    company = MagicMock(id=1, name="Company X")
    assert validate_user_from_company(user, company) is None


@pytest.mark.asyncio
async def test_check_telegram_username_for_duplicates_raises():
    session = AsyncMock()
    validator = BaseUserValidator(session=session)
    validator.check_telegram_username_exists = AsyncMock(return_value=True)

    # Патчим метод класса
    from src.features_v1.validators import user_validators
    user_validators.BaseUserValidator.check_telegram_username_exists = validator.check_telegram_username_exists

    with pytest.raises(HTTPException) as exc:
        await check_telegram_username_for_duplicates("existing_user", session)
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST
    assert exc.value.detail == ERROR_INVALID_TELEGRAM_USERNAME


@pytest.mark.asyncio
async def test_validate_field_members_invalid_user():
    session = AsyncMock()
    validator = BaseUserValidator(session=session)
    validator.get_user_by_uuid = AsyncMock(return_value=None)

    from src.features_v1.validators import user_validators
    user_validators.BaseUserValidator.get_user_by_uuid = validator.get_user_by_uuid

    with pytest.raises(HTTPException) as exc:
        await validate_field_members(session, [1], company_id=1)
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.asyncio
async def test_validate_field_members_not_from_company():
    session = AsyncMock()
    user = MagicMock(company_id=2)
    validator = BaseUserValidator(session=session)
    validator.get_user_by_uuid = AsyncMock(return_value=user)

    from src.features_v1.validators import user_validators
    user_validators.BaseUserValidator.get_user_by_uuid = validator.get_user_by_uuid

    with pytest.raises(HTTPException) as exc:
        await validate_field_members(session, [1], company_id=1)
    assert exc.value.status_code == status.HTTP_400_BAD_REQUEST