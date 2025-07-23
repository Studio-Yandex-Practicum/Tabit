from typing import List

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
from src.schemas import EnumItemSchema

router = APIRouter(prefix='/enums', tags=['enums'])


@router.get('/problem-color', response_model=List[EnumItemSchema])
async def get_problem_colors():
    return ProblemColor.to_list()


@router.get('/problem-type', response_model=List[EnumItemSchema])
async def get_problem_types():
    return ProblemType.to_list()


@router.get('/problem-status', response_model=List[EnumItemSchema])
async def get_problem_statuses():
    return ProblemStatus.to_list()


@router.get('/meeting-status', response_model=List[EnumItemSchema])
async def get_meeting_statuses():
    return MeetingStatus.to_list()


@router.get('/meeting-result', response_model=List[EnumItemSchema])
async def get_meeting_results():
    return MeetingResultEnum.to_list()


@router.get('/task-status', response_model=List[EnumItemSchema])
async def get_task_statuses():
    return TaskStatus.to_list()


@router.get('/company-user-role', response_model=List[EnumItemSchema])
async def get_company_user_roles():
    return CompanyUserRole.to_list()


@router.get('/meeting-result-engagement', response_model=List[EnumItemSchema])
async def get_meeting_result_engagements():
    return MeetingResultEngagementEnum.to_list()


@router.get('/meeting-result-solution', response_model=List[EnumItemSchema])
async def get_meeting_result_solutions():
    return MeetingResultSolutionEnum.to_list()
