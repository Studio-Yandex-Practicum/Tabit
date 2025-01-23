from fastapi import APIRouter
from uuid import UUID

router = APIRouter()


@router.get('/{survey_id}/company/{company_id}/summary_report_conflict/')
async def get_summary_report_conflict(survey_id: UUID, company_id: UUID):
    """
    Получить сводный отчет по конфликтам для компании.
    """
    return {'survey_id': survey_id, 'company_id': company_id, 'conflict_score': 75}


@router.get('/{survey_id}/company/{company_id}/summary_report_trust/')
async def get_summary_report_trust(survey_id: UUID, company_id: UUID):
    """
    Получить сводный отчет по доверию для компании.
    """
    return {'survey_id': survey_id, 'company_id': company_id, 'trust_score': 85}


@router.get('/{survey_id}/company/{company_id}/summary_report_results/')
async def get_summary_report_results(survey_id: UUID, company_id: UUID):
    """
    Получить сводный отчет по общим результатам для компании.
    """
    return {
        'survey_id': survey_id,
        'company_id': company_id,
        'results': {'conflict_score': 75, 'trust_score': 85, 'engagement_score': 80},
    }


@router.get('/{survey_id}/company/{company_id}/personal_report/')
async def get_personal_report(survey_id: UUID, company_id: UUID):
    """
    Получить персональный отчет для компании.
    """
    return {
        'survey_id': survey_id,
        'company_id': company_id,
        'personal_reports': [
            {'user_id': 1, 'conflict_score': 70, 'trust_score': 90},
            {'user_id': 2, 'conflict_score': 60, 'trust_score': 80},
        ],
    }


@router.get('/{survey_id}/company/{company_id}/personal_report_conflict/')
async def get_personal_report_conflict(survey_id: UUID, company_id: UUID):
    """
    Получить персональный отчет по конфликтам для компании.
    """
    return {
        'survey_id': survey_id,
        'company_id': company_id,
        'personal_conflict_reports': [
            {'user_id': 1, 'conflict_score': 70},
            {'user_id': 2, 'conflict_score': 60},
        ],
    }


@router.get('/{survey_id}/company/{company_id}/personal_report_trust/')
async def get_personal_report_trust(survey_id: UUID, company_id: UUID):
    """
    Получить персональный отчет по доверию для компании.
    """
    return {
        'survey_id': survey_id,
        'company_id': company_id,
        'personal_trust_reports': [
            {'user_id': 1, 'trust_score': 90},
            {'user_id': 2, 'trust_score': 80},
        ],
    }


@router.get('/{survey_id}/company/{company_id}/personal_report_results/')
async def get_personal_report_results(survey_id: UUID, company_id: UUID):
    """
    Получить персональный отчет по общим результатам для компании.
    """
    return {
        'survey_id': survey_id,
        'company_id': company_id,
        'personal_results': [
            {'user_id': 1, 'conflict_score': 70, 'trust_score': 90},
            {'user_id': 2, 'conflict_score': 60, 'trust_score': 80},
        ],
    }
