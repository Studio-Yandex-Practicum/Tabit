from enum import Enum

from fastapi import APIRouter

from src.models.enum import (
    CompanyUserRole,
    MeetingResultEngagementEnum,
    MeetingResultEnum,
    MeetingResultSolutionEnum,
    MeetingStatus,
    ProblemColor,
    ProblemStatus,
    ProblemType,
    TaskStatus,
)

router = APIRouter(prefix='/enums', tags=['enums'])


def enum_to_list(enum_class: type[Enum]):
    return [{'key': item.name, 'value': item.value} for item in enum_class]


@router.get('/problem-color')
async def get_problem_colors():
    return enum_to_list(ProblemColor)


@router.get('/problem-type')
async def get_problem_types():
    return enum_to_list(ProblemType)


@router.get('/problem-status')
async def get_problem_statuses():
    return enum_to_list(ProblemStatus)


@router.get('/meeting-status')
async def get_meeting_statuses():
    return enum_to_list(MeetingStatus)


@router.get('/meeting-result')
async def get_meeting_results():
    return enum_to_list(MeetingResultEnum)


@router.get('/task-status')
async def get_task_statuses():
    return enum_to_list(TaskStatus)


@router.get('/company-user-role')
async def get_company_user_roles():
    return enum_to_list(CompanyUserRole)


@router.get('/meeting-result-engagement')
async def get_meeting_result_engagements():
    return enum_to_list(MeetingResultEngagementEnum)


@router.get('/meeting-result-solution')
async def get_meeting_result_solutions():
    return enum_to_list(MeetingResultSolutionEnum)
