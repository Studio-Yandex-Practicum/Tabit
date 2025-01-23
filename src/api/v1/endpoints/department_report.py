from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_depends import get_async_session

router = APIRouter()


@router.get(
    '/survey/{survey_id}/company/{company_id}/department_report',
    summary='Общий отчет по отделу',
)
async def get_department_report(
    survey_id: int,
    company_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Возвращает общий отчет по тестированию сотрудников отдела.
    """
    # TODO: Реализовать проверку существования survey_id и company_id
    # TODO: Реализовать логику получения данных из базы

    return {
        'status': 'success',
        'data': {
            'survey_id': survey_id,
            'company_id': company_id,
            'report_type': 'department',
            'content': 'Общий отчет по отделу',
        },
    }


@router.get(
    '/survey/{survey_id}/company/{company_id}/department_report_conflict',
    summary='Отчет по конфликтности сотрудников отдела',
)
async def get_department_report_conflict(
    survey_id: int,
    company_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Возвращает отчет по конфликтности сотрудников отдела.
    """

    return {
        'status': 'success',
        'data': {
            'survey_id': survey_id,
            'company_id': company_id,
            'report_type': 'conflict',
            'content': 'Отчет по конфликтности сотрудников отдела',
        },
    }


@router.get(
    '/survey/{survey_id}/company/{company_id}/department_report_trust',
    summary='Отчет по доверию сотрудников отдела',
)
async def get_department_report_trust(
    survey_id: int,
    company_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Возвращает отчет по доверию сотрудников отдела.
    """

    return {
        'status': 'success',
        'data': {
            'survey_id': survey_id,
            'company_id': company_id,
            'report_type': 'trust',
            'content': 'Отчет по доверию сотрудников отдела',
        },
    }


@router.get(
    '/survey/{survey_id}/company/{company_id}/department_report_results',
    summary='Общий результат тестирования отдела',
)
async def get_department_report_results(
    survey_id: int,
    company_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Возвращает общий результат тестирования отдела.
    """

    return {
        'status': 'success',
        'data': {
            'survey_id': survey_id,
            'company_id': company_id,
            'report_type': 'results',
            'content': 'Общий результат тестирования отдела',
        },
    }
