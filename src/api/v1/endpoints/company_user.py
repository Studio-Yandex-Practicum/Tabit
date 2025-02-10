from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_depends import get_async_session
from src.companies.schemas.company import (CompanyResponseForUserSchema, UserCompanyUpdateSchema,
                                           CompanyFeedbackCreateShema)
from src.companies.crud import company_crud, feedback_crud
from src.users.crud.user import user_crud


router = APIRouter()


@router.get('/{company_slug}/{uuid}/', response_model=CompanyResponseForUserSchema)
async def get_company_user(
    company_slug: str, uuid: UUID, session: AsyncSession = Depends(get_async_session)
):
    """
    Личный кабинет пользователя.
    """
    company = await company_crud.get_by_slug(session=session, obj_slug=company_slug)
    tabit_user = await company_crud.get_user_company_by_id_and_slug(
        session=session, uuid=uuid, company_id=company.id
    )
    # TODO: Реализовать проверку(валидацию) на существовании компании.
    return tabit_user


@router.patch('/{company_slug}/{uuid}/', response_model=CompanyResponseForUserSchema)
async def patch_company_user(
    company_slug: str, uuid: UUID,
    obj_in: UserCompanyUpdateSchema,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Редактирование профиля пользователя компании.
    """
    user_db = await user_crud.get(session=session, obj_id=uuid)
    update_user_db = await user_crud.update(session=session, db_obj=user_db, obj_in=obj_in)
    # TODO: Реализовать проверку(валидацию) на существовании компании.
    # TODO: Реализовать проверку(валидацию), есть ли пользователь в БД.
    return update_user_db


@router.post('/{company_slug}/feedback/', response_model=dict)
async def post_feedback(
    company_slug: str,
    question: CompanyFeedbackCreateShema,
    session: AsyncSession = Depends(get_async_session)
):
    """
    Задать вопрос в разделе 'Помощь'.
    """
    # TODO: Реализовать сохранение данных обратной связи в базу данных.
    # На данном этапе нету модели Feedback, до конца не понятно, как это будет выглядеть
    # в конечном итоге. Постарался реализовать примерное сохранение данных с "заглушками"
    # модели,схемы и объекта feedback_crud класса CRUDFeedback.
    await feedback_crud.create(session=session, obj_in=question)
    return {'message': f'Обратная связь отправлена для компании {company_slug}'}
