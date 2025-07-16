"""Логика получения ответа на тест Люшера по сохраненным в базу данных ответов."""

import os
from csv import DictReader
from pathlib import Path

import aiofiles
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud.crud_surveys import luscher_color_second_crud


async def get_combination() -> dict[str, str]:
    """Вернет словарь

    где:
    - ключ это группа цветов, например '+3+7',
    - значение это текст с состоянием, которое соответствует группе цветов.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    filename = Path(script_dir) / 'csv' / 'luscher.csv'

    async with aiofiles.open(filename, 'r', encoding='utf-8') as file:
        content = await file.read()
        return {row['combination']: row['result'] for row in DictReader(content.splitlines())}


async def get_set_answer(session: AsyncSession, cycle_for_user: int) -> list[str]:
    """Вернет список групп цветов по весам, согласно ответам испытуемого.

    Упрощенная версия: обрабатывается только второй набор ответов на тест Люшера.
    """
    # TODO: реализовать полную версию формирования групп цветов,
    # основываясь на двух наборах ответа.
    # luscher_first = await luscher_color_first_crud.get_by_cycle(session, cycle_for_user)
    luscher_second = await luscher_color_second_crud.get_by_cycle(session, cycle_for_user)
    set_answer: dict[str, list[tuple[int, ...]]] = {
        '+': [
            (
                luscher_second.selection_1.get_weight_from_color(),
                luscher_second.selection_2.get_weight_from_color(),
            ),
        ],
        'х': [
            (
                luscher_second.selection_3.get_weight_from_color(),
                luscher_second.selection_4.get_weight_from_color(),
            ),
        ],
        '=': [
            (
                luscher_second.selection_5.get_weight_from_color(),
                luscher_second.selection_6.get_weight_from_color(),
            ),
        ],
        '-': [
            (
                luscher_second.selection_7.get_weight_from_color(),
                luscher_second.selection_8.get_weight_from_color(),
            ),
        ],
    }
    return [
        key + key.join(map(str, value))
        for key, set_value in set_answer.items()
        for value in set_value
    ]


def get_status_luscher(set_answer: list[str]) -> str:
    """По первой группе цветов вернет общий статус испытуемого."""
    check = set_answer[0]
    if check in (
        '+3',
        '+2+1',
        '+2+3',
        '+3+1',
        '+3+2',
        '+3+4',
        '+3+5',
        '+4+3',
        '+4+5',
        '+5+3',
        '+5+4',
    ):
        return 'Воодушевлен'
    elif check in ('+2', '+1+2', '+1+3', '+4+1', '+4+2'):
        return 'В норме'
    elif check in ('+1', '+4', '+1+5', '+1+6', '+2+4', '+2+5', '+2+6', '+5+1', '+5+2'):
        return 'Низкий уровень стресса.'
    else:
        return 'Высокий уровень стресса.'


async def get_response_result(session, cycle_for_user):
    """Формирует словарь для ответа эндпоинта."""
    colors_by_groups = await get_set_answer(session, cycle_for_user)
    combination = await get_combination()
    return {
        'status': get_status_luscher(colors_by_groups),
        'result': ''.join(combination[group] for group in colors_by_groups),
    }
