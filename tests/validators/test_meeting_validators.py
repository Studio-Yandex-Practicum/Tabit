import pytest
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, MagicMock

from src.features_v1.validators.meeting_validators import (
    check_meeting_exists,
    check_meeting_title_unique,
    check_meeting_date_available,
    check_result_meeting_unique,
    validate_meeting_was_held,
)
from src.models import Meeting, MeetingStatus, CompanyUser


@pytest.mark.asyncio
async def test_check_meeting_exists_found(mocker):
    session = mocker.Mock(spec=AsyncSession)
    mock_get_or_404 = mocker.patch("src.features_v1.validators.meeting_validators.meeting_crud.get_or_404", new_callable=AsyncMock)
    await check_meeting_exists(1, session)
    mock_get_or_404.assert_awaited_once_with(session, 1)


@pytest.mark.asyncio
async def test_check_meeting_exists_not_found(mocker):
    session = mocker.Mock(spec=AsyncSession)
    mocker.patch("src.features_v1.validators.meeting_validators.meeting_crud.get_or_404", new_callable=AsyncMock, side_effect=HTTPException(status_code=404))
    with pytest.raises(HTTPException) as exc:
        await check_meeting_exists(1, session)
    assert exc.value.status_code == 404


@pytest.mark.asyncio
async def test_check_result_meeting_unique_raises(mocker):
    session = mocker.Mock(spec=AsyncSession)
    owner = MagicMock(spec=CompanyUser)
    owner.id = 5
    mocker.patch("src.features_v1.validators.meeting_validators.result_meeting_crud.get_multi", new_callable=AsyncMock, return_value=[object()])
    with pytest.raises(HTTPException) as exc:
        await check_result_meeting_unique(1, owner, session)
    assert exc.value.status_code == 400


@pytest.mark.asyncio
async def test_check_result_meeting_unique_valid(mocker):
    session = mocker.Mock(spec=AsyncSession)
    owner = MagicMock(spec=CompanyUser)
    owner.id = 5
    mocker.patch("src.features_v1.validators.meeting_validators.result_meeting_crud.get_multi", new_callable=AsyncMock, return_value=[])
    await check_result_meeting_unique(1, owner, session)


def test_validate_meeting_was_held_raises():
    meeting = MagicMock(spec=Meeting)
    meeting.status = MeetingStatus.HELD
    with pytest.raises(HTTPException) as exc:
        validate_meeting_was_held(meeting)
    assert exc.value.status_code == 422
