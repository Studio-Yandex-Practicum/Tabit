from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.auth.dependencies import (
    current_company_moderator,
    current_user_tabit,
)
from src.core.database.db_depends import get_async_session
from src.crud.crud_company import company_crud
from src.crud.crud_research import research_instance_crud, research_type_crud
from src.models import CompanyUser
from src.schemas.research import (
    ResearchInstanceCreateSchema,
    ResearchInstanceResponseSchema,
    ResearchInstanceUpdateSchema,
    ResearchInstanceWithTypeSchema,
    ResearchResultsSchema,
    ResearchTypeCreateSchema,
    ResearchTypeResponseSchema,
    ResearchTypeUpdateSchema,
)

router = APIRouter(prefix='/{company_slug}/research')


# =============================================================================
# ЭНДПОИНТЫ ДЛЯ ТИПОВ ОПРОСОВ (только модераторы и админы)
# =============================================================================


@router.post(
    '/types',
    response_model=ResearchTypeResponseSchema,
    dependencies=[Depends(current_company_moderator)],
    summary='Создать новый тип однотипного опроса',
    description='Создает новый тип опроса для компании. Доступно только модераторам.',
    status_code=status.HTTP_201_CREATED,
)
async def create_research_type(
    company_slug: str,
    research_type: ResearchTypeCreateSchema,
    current_user: CompanyUser = Depends(current_company_moderator),
    session: AsyncSession = Depends(get_async_session),
) -> ResearchTypeResponseSchema:
    """Создает новый тип однотипного опроса."""
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)

    return await research_type_crud.create_research_type(
        session=session,
        research_type_in=research_type,
        company_id=company.id,
        created_by=current_user.id,
    )


@router.get(
    '/types',
    response_model=List[ResearchTypeResponseSchema],
    dependencies=[Depends(current_user_tabit)],
    summary='Получить все типы опросов компании',
    description='Получает список всех типов опросов для компании.',
    status_code=status.HTTP_200_OK,
)
async def get_research_types(
    company_slug: str,
    active_only: bool = True,
    session: AsyncSession = Depends(get_async_session),
) -> List[ResearchTypeResponseSchema]:
    """Получает все типы опросов для компании."""
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)

    return await research_type_crud.get_by_company(
        session=session,
        company_id=company.id,
        active_only=active_only,
    )


@router.get(
    '/types/{research_type_id}',
    response_model=ResearchTypeResponseSchema,
    dependencies=[Depends(current_user_tabit)],
    summary='Получить тип опроса по ID',
    description='Получает конкретный тип опроса по его ID.',
    status_code=status.HTTP_200_OK,
)
async def get_research_type(
    company_slug: str,
    research_type_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> ResearchTypeResponseSchema:
    """Получает тип опроса по ID."""
    await company_crud.get_by_slug(session, company_slug, raise_404=True)

    research_type = await research_type_crud.get_or_404(session, research_type_id)

    # Проверяем, что тип опроса принадлежит компании
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)
    if research_type.company_id != company.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Тип опроса не найден',
        )

    return research_type


@router.patch(
    '/types/{research_type_id}',
    response_model=ResearchTypeResponseSchema,
    dependencies=[Depends(current_company_moderator)],
    summary='Обновить тип опроса',
    description='Обновляет существующий тип опроса. Доступно только модераторам.',
    status_code=status.HTTP_200_OK,
)
async def update_research_type(
    company_slug: str,
    research_type_id: int,
    research_type_update: ResearchTypeUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
) -> ResearchTypeResponseSchema:
    """Обновляет тип опроса."""
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)

    research_type = await research_type_crud.get_or_404(session, research_type_id)

    # Проверяем, что тип опроса принадлежит компании
    if research_type.company_id != company.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Тип опроса не найден',
        )

    return await research_type_crud.update_research_type(
        session=session,
        research_type_db=research_type,
        research_type_in=research_type_update,
    )


@router.delete(
    '/types/{research_type_id}',
    dependencies=[Depends(current_company_moderator)],
    summary='Удалить тип опроса',
    description='Удаляет тип опроса. Доступно только модераторам.',
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_research_type(
    company_slug: str,
    research_type_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> None:
    """Удаляет тип опроса."""
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)

    research_type = await research_type_crud.get_or_404(session, research_type_id)

    # Проверяем, что тип опроса принадлежит компании
    if research_type.company_id != company.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Тип опроса не найден',
        )

    await research_type_crud.remove(session, research_type)


# =============================================================================
# ЭНДПОИНТЫ ДЛЯ ЭКЗЕМПЛЯРОВ ОПРОСОВ
# =============================================================================


@router.post(
    '/instances',
    response_model=ResearchInstanceResponseSchema,
    dependencies=[Depends(current_user_tabit)],
    summary='Создать экземпляр опроса',
    description='Создает новый экземпляр опроса для пользователя.',
    status_code=status.HTTP_201_CREATED,
)
async def create_research_instance(
    company_slug: str,
    instance: ResearchInstanceCreateSchema,
    current_user: CompanyUser = Depends(current_user_tabit),
    session: AsyncSession = Depends(get_async_session),
) -> ResearchInstanceResponseSchema:
    """Создает экземпляр опроса."""
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)

    # Проверяем, что тип опроса принадлежит компании
    research_type = await research_type_crud.get_or_404(session, instance.research_type_id)
    if research_type.company_id != company.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Тип опроса не найден',
        )

    # Проверяем, что пользователь принадлежит компании
    if current_user.company_id != company.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Доступ запрещен',
        )

    # Проверяем, что тип опроса активен
    if not research_type.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail='Тип опроса неактивен',
        )

    return await research_instance_crud.create_instance(session=session, instance_in=instance)


@router.get(
    '/instances',
    response_model=List[ResearchInstanceWithTypeSchema],
    dependencies=[Depends(current_user_tabit)],
    summary='Получить экземпляры опросов пользователя',
    description='Получает все экземпляры опросов для текущего пользователя.',
    status_code=status.HTTP_200_OK,
)
async def get_user_research_instances(
    company_slug: str,
    current_user: CompanyUser = Depends(current_user_tabit),
    session: AsyncSession = Depends(get_async_session),
) -> List[ResearchInstanceWithTypeSchema]:
    """Получает экземпляры опросов пользователя."""
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)

    # Проверяем, что пользователь принадлежит компании
    if current_user.company_id != company.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Доступ запрещен',
        )

    instances = await research_instance_crud.get_by_user(
        session=session,
        user_id=current_user.id,
        company_id=company.id,
    )

    # Добавляем информацию о типах опросов
    result = []
    for instance in instances:
        research_type = await research_type_crud.get_or_404(session, instance.research_type_id)
        instance.research_type = research_type
        result.append(instance)

    return result


@router.get(
    '/instances/{instance_id}',
    response_model=ResearchInstanceWithTypeSchema,
    dependencies=[Depends(current_user_tabit)],
    summary='Получить экземпляр опроса по ID',
    description='Получает конкретный экземпляр опроса по его ID.',
    status_code=status.HTTP_200_OK,
)
async def get_research_instance(
    company_slug: str,
    instance_id: int,
    current_user: CompanyUser = Depends(current_user_tabit),
    session: AsyncSession = Depends(get_async_session),
) -> ResearchInstanceWithTypeSchema:
    """Получает экземпляр опроса по ID."""
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)

    instance = await research_instance_crud.get_or_404(session, instance_id)

    # Проверяем, что экземпляр принадлежит пользователю или пользователь - модератор
    if instance.user_id != current_user.id and current_user.role != 'Модератор':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Доступ запрещен',
        )

    # Проверяем, что экземпляр принадлежит компании
    research_type = await research_type_crud.get_or_404(session, instance.research_type_id)
    if research_type.company_id != company.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Экземпляр опроса не найден',
        )

    # Добавляем информацию о типе опроса
    instance.research_type = research_type

    return instance


@router.patch(
    '/instances/{instance_id}',
    response_model=ResearchInstanceResponseSchema,
    dependencies=[Depends(current_user_tabit)],
    summary='Обновить экземпляр опроса',
    description='Обновляет экземпляр опроса (например, сохраняет ответы).',
    status_code=status.HTTP_200_OK,
)
async def update_research_instance(
    company_slug: str,
    instance_id: int,
    instance_update: ResearchInstanceUpdateSchema,
    current_user: CompanyUser = Depends(current_user_tabit),
    session: AsyncSession = Depends(get_async_session),
) -> ResearchInstanceResponseSchema:
    """Обновляет экземпляр опроса."""
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)

    instance = await research_instance_crud.get_or_404(session, instance_id)

    # Проверяем, что экземпляр принадлежит пользователю или пользователь - модератор
    if instance.user_id != current_user.id and current_user.role != 'Модератор':
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Доступ запрещен',
        )

    # Проверяем, что экземпляр принадлежит компании
    research_type = await research_type_crud.get_or_404(session, instance.research_type_id)
    if research_type.company_id != company.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Экземпляр опроса не найден',
        )

    return await research_instance_crud.update_instance(
        session=session,
        instance_db=instance,
        instance_in=instance_update,
    )


# =============================================================================
# ЭНДПОИНТЫ ДЛЯ СТАТИСТИКИ (только модераторы и админы)
# =============================================================================


@router.get(
    '/types/{research_type_id}/statistics',
    response_model=ResearchResultsSchema,
    dependencies=[Depends(current_company_moderator)],
    summary='Получить статистику по типу опроса',
    description='Получает статистику ответов по конкретному типу опроса.',
    status_code=status.HTTP_200_OK,
)
async def get_research_statistics(
    company_slug: str,
    research_type_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> ResearchResultsSchema:
    """Получает статистику по типу опроса."""
    company = await company_crud.get_by_slug(session, company_slug, raise_404=True)

    research_type = await research_type_crud.get_or_404(session, research_type_id)

    # Проверяем, что тип опроса принадлежит компании
    if research_type.company_id != company.id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail='Тип опроса не найден',
        )

    # Получаем базовую статистику
    stats = await research_instance_crud.get_statistics(
        session=session, research_type_id=research_type_id
    )

    # Формируем полный ответ
    return ResearchResultsSchema(
        research_type_id=research_type_id,
        research_type_title=research_type.title,
        total_responses=stats['total_responses'],
        completed_responses=stats['completed_responses'],
        in_progress_responses=stats['in_progress_responses'],
        average_completion_time=stats['average_completion_time'],
        question_statistics=[],  # TODO: Добавить детальную статистику по вопросам
    )
