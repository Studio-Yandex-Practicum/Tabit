"""Модуль роутеров для обратной связи пользователям."""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth.dependencies import current_user_tabit
from src.core.database.db_depends import get_async_session
from src.crud import company_crud
from src.features_v1.validators import validate_user_from_company
from src.models import CompanyUser
from src.services.email_service.email_schema import EmailCreateSchema

router = APIRouter()


@router.post(
    '/',
    summary='Задать вопрос для обратной связи',
    response_model=dict[str, str],
)
async def post_feedback(
    company_slug: str,
    question: EmailCreateSchema,
    session: AsyncSession = Depends(get_async_session),
    user: CompanyUser = Depends(current_user_tabit),
) -> dict[str, str]:
    """
    Задать вопрос в разделе 'Помощь'.
    """
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    validate_user_from_company(user, company)
    # TODO: Подключить почту.
    return {'message': f'Обратная связь отправлена для компании {company_slug}'}
