from unittest.mock import AsyncMock, MagicMock

import pytest
from fastapi import HTTPException, status

from src.features_v1.constants import TextError
from src.features_v1.validators import problem_validators


@pytest.mark.asyncio
async def test_check_company_problem_wrong_company_raises():
    session = AsyncMock()
    problem = MagicMock(company_id=2)
    problem_validators.problem_crud.get_or_404 = AsyncMock(return_value=problem)
    company = MagicMock(id=3)
    problem_validators.company_crud.get_or_404 = AsyncMock(return_value=company)

    with pytest.raises(HTTPException) as exc:
        await problem_validators.check_company_problem(1, 123, session)
    assert exc.value.status_code == status.HTTP_403_FORBIDDEN
    assert exc.value.detail == TextError.WRONG_PROBLEM


@pytest.mark.asyncio
async def test_check_message_feed_and_problem_invalid_feed():
    session = AsyncMock()
    message_feed = MagicMock(problem_id=99)
    problem_id = 42
    problem_validators.message_feed_crud.get_or_404 = AsyncMock(return_value=message_feed)

    with pytest.raises(HTTPException) as exc:
        await problem_validators.check_message_feed_and_problem(1, problem_id, session)
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == TextError.WRONG_MESSAGE_FEED


@pytest.mark.asyncio
async def test_check_problem_exists_not_found():
    session = AsyncMock()
    problem_validators.problem_crud.get_or_404 = AsyncMock(
        side_effect=HTTPException(status_code=404)
    )

    with pytest.raises(HTTPException) as exc:
        await problem_validators.check_problem_exists(42, session)
    assert exc.value.status_code == status.HTTP_404_NOT_FOUND
    assert exc.value.detail == TextError.PROBLEM_NOT_FOUND
