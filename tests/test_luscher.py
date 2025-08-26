from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from src.business_logic.luscher import (
    get_response_result,
    get_set_answer,
    get_status_luscher,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'mock_colors, mock_combination, expected',
    [
        (['+3+2'], {'+3+2': 'Ты молодец!'}, {'status': 'Воодушевлен', 'result': 'Ты молодец!'}),
    ],
)
async def test_get_response_result_single_group(mock_colors, mock_combination, expected):
    """
    Тест для проверки получения результата Luscher с одной группой цветов.
    """
    mock_session = AsyncMock()
    mock_cycle_id = 42
    with (
        patch('src.business_logic.luscher.get_set_answer', return_value=mock_colors),
        patch('src.business_logic.luscher.get_combination', return_value=mock_combination),
    ):
        result = await get_response_result(mock_session, mock_cycle_id)
    assert result == expected


@pytest.mark.parametrize(
    'groups, expected',
    [
        (['+3+2'], 'Воодушевлен'),
        (['+2'], 'В норме'),
        (['+1'], 'Низкий уровень стресса.'),
        (['+6+7'], 'Высокий уровень стресса.'),
    ],
)
def test_get_status_luscher_various_groups(groups, expected):
    """
    Тест для проверки получения статуса Luscher для различных групп цветов.
    """
    assert get_status_luscher(groups) == expected


def test_get_status_luscher_priority():
    """
    Тест для проверки приоритета групп цветов Luscher.
    """
    assert get_status_luscher(['+3+2', '+2', '+1']) == 'Воодушевлен'
    assert get_status_luscher(['+2', '+1', '+6+7']) == 'В норме'
    assert get_status_luscher(['+1', '+6+7']) == 'Низкий уровень стресса.'
    assert get_status_luscher(['+6+7', '+1']) == 'Высокий уровень стресса.'


@pytest.mark.asyncio
async def test_get_response_result_multiple_groups():
    """
    Тест для проверки получения результата Luscher с несколькими группами цветов.
    """
    mock_session = AsyncMock()
    mock_cycle_id = 42
    mock_groups = ['+3+2', '+1+4']
    mock_combination = {'+3+2': 'A', '+1+4': 'B'}

    with (
        patch('src.business_logic.luscher.get_set_answer', return_value=mock_groups),
        patch('src.business_logic.luscher.get_combination', return_value=mock_combination),
    ):
        result = await get_response_result(mock_session, mock_cycle_id)

    assert result == {'status': 'Воодушевлен', 'result': 'AB'}


@pytest.mark.asyncio
async def test_get_response_result_partial_combination_raises_key_error():
    """
    Тест для проверки обработки KeyError при отсутствии комбинации.
    """
    mock_session = AsyncMock()
    mock_cycle_id = 42
    mock_groups = ['+3+2', '+9+9']
    mock_combination = {'+3+2': 'X'}

    with (
        patch('src.business_logic.luscher.get_set_answer', return_value=mock_groups),
        patch('src.business_logic.luscher.get_combination', return_value=mock_combination),
    ):
        with pytest.raises(KeyError) as exc_info:
            await get_response_result(mock_session, mock_cycle_id)
        assert '+9+9' in str(exc_info.value)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    'groups, combination',
    [
        (['+1+2'], {}),
        (['+3+4'], {'+X+X': 'dummy'}),
    ],
)
async def test_get_response_result_with_missing_all_combinations(groups, combination):
    """
    Тест для проверки обработки KeyError при отсутствии всех комбинаций.
    """
    mock_session = AsyncMock()
    mock_cycle_id = 42

    with (
        patch('src.business_logic.luscher.get_set_answer', return_value=groups),
        patch('src.business_logic.luscher.get_combination', return_value=combination),
    ):
        with pytest.raises(KeyError):
            await get_response_result(mock_session, mock_cycle_id)


@pytest.mark.asyncio
async def test_get_response_result_calls_dependencies():
    """
    Тест для проверки вызовов зависимостей в get_response_result.
    """
    mock_session = AsyncMock()
    mock_cycle_id = 42

    with (
        patch(
            'src.business_logic.luscher.get_set_answer', new_callable=AsyncMock
        ) as mock_get_set_answer,
        patch(
            'src.business_logic.luscher.get_combination', new_callable=AsyncMock
        ) as mock_get_combination,
    ):
        mock_get_set_answer.return_value = ['+2']
        mock_get_combination.return_value = {'+2': 'Z'}

        result = await get_response_result(mock_session, mock_cycle_id)

        mock_get_set_answer.assert_awaited_once_with(mock_session, mock_cycle_id)
        mock_get_combination.assert_awaited_once()
        assert result == {'status': 'В норме', 'result': 'Z'}


@pytest.mark.asyncio
async def test_get_set_answer_returns_expected_groupings():
    """
    Тест для проверки структуры группировки ответов Luscher.
    """
    mock_session = AsyncMock()

    mock_color = MagicMock()
    mock_color.get_weight_from_color.side_effect = [3, 2, 1, 4, 5, 6, 7, 8]

    mock_luscher_second = MagicMock(
        selection_1=mock_color,
        selection_2=mock_color,
        selection_3=mock_color,
        selection_4=mock_color,
        selection_5=mock_color,
        selection_6=mock_color,
        selection_7=mock_color,
        selection_8=mock_color,
    )

    with patch(
        'src.business_logic.luscher.luscher_color_second_crud.get_by_cycle',
        return_value=mock_luscher_second,
    ):
        result = await get_set_answer(mock_session, 42)

    assert result == ['+3+2', 'х1х4', '=5=6', '-7-8']


@pytest.mark.asyncio
async def test_get_response_result_output_structure():
    """
    Тест для проверки структуры ответа get_response_result.
    """
    mock_session = AsyncMock()
    mock_cycle_id = 42
    mock_groups = ['+3+2']
    mock_combination = {'+3+2': 'abc'}

    with (
        patch('src.business_logic.luscher.get_set_answer', return_value=mock_groups),
        patch('src.business_logic.luscher.get_combination', return_value=mock_combination),
    ):
        result = await get_response_result(mock_session, mock_cycle_id)

    assert set(result.keys()) == {'status', 'result'}
    assert isinstance(result['status'], str)
    assert isinstance(result['result'], str)
    assert result['result']


def test_get_status_luscher_empty_list_raises():
    """
    Тест для проверки обработки пустого списка в get_status_luscher.
    """
    with pytest.raises(IndexError):
        get_status_luscher([])


@pytest.mark.asyncio
async def test_get_response_result_with_empty_group_list():
    """
    Тест для проверки обработки пустого списка в get_response_result.
    """
    mock_session = AsyncMock()
    mock_cycle_id = 42

    with (
        patch('src.business_logic.luscher.get_set_answer', return_value=[]),
        patch('src.business_logic.luscher.get_combination', return_value={}),
    ):
        with pytest.raises(IndexError):
            await get_response_result(mock_session, mock_cycle_id)
