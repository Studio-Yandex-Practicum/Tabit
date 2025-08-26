import json
from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.config.logging import logger
from src.crud.constants import DefaultConstants, TextErrorConstants
from src.crud.crud_base import CRUDBase
from src.models import ResearchInstance, ResearchType
from src.schemas.research import (
    ResearchInstanceCreateSchema,
    ResearchInstanceUpdateSchema,
    ResearchTypeCreateSchema,
    ResearchTypeUpdateSchema,
)


class CRUDResearchType(CRUDBase):
    """
    Класс для CRUD операций для типов однотипных опросов (research).
    """

    async def create_research_type(
        self,
        session: AsyncSession,
        research_type_in: ResearchTypeCreateSchema,
        company_id: int,
        created_by: UUID,
        auto_commit: bool = DefaultConstants.AUTO_COMMIT,
    ) -> ResearchType:
        """Создает новый тип опроса."""
        research_type_data = research_type_in.model_dump()
        # Преобразуем вопросы в JSON строку
        research_type_data['questions'] = json.dumps(
            research_type_data['questions'], ensure_ascii=False
        )
        research_type_data.update(
            {
                'company_id': company_id,
                'created_by': created_by,
            }
        )

        research_type_db = self.model(**research_type_data)
        try:
            session.add(research_type_db)
            if auto_commit:
                await session.commit()
                await session.refresh(research_type_db)
        except Exception as error:
            await session.rollback()
            logger.error(f'{TextErrorConstants.CREATE_SERVER_LOG} {self.model.__name__}: {error}')
            raise error
        return research_type_db

    async def update_research_type(
        self,
        session: AsyncSession,
        research_type_db: ResearchType,
        research_type_in: ResearchTypeUpdateSchema,
        auto_commit: bool = DefaultConstants.AUTO_COMMIT,
    ) -> ResearchType:
        """Обновляет тип опроса."""
        research_type_data = jsonable_encoder(research_type_db)
        update_data = research_type_in.model_dump(exclude_unset=True)

        # Если обновляются вопросы, преобразуем их в JSON
        if 'questions' in update_data:
            update_data['questions'] = json.dumps(update_data['questions'], ensure_ascii=False)

        for field in research_type_data:
            if field in update_data:
                setattr(research_type_db, field, update_data[field])

        research_type_db.updated_at = datetime.utcnow()

        try:
            session.add(research_type_db)
            if auto_commit:
                await session.commit()
                await session.refresh(research_type_db)
        except Exception as error:
            await session.rollback()
            logger.error(f'{TextErrorConstants.UPDATE_SERVER_LOG} {self.model.__name__}: {error}')
            raise error
        return research_type_db

    async def get_by_company(
        self,
        session: AsyncSession,
        company_id: int,
        active_only: bool = True,
    ) -> List[ResearchType]:
        """Получает все типы опросов для компании."""
        filters = {'company_id': company_id}
        if active_only:
            filters['is_active'] = True

        return await self.get_multi(session, filters=filters, order_by=['-created_at'])

    async def get_with_questions(
        self,
        session: AsyncSession,
        research_type_id: int,
    ) -> Optional[ResearchType]:
        """Получает тип опроса с расшифрованными вопросами."""
        research_type = await self.get(session, research_type_id)
        if research_type and research_type.questions:
            try:
                # Расшифровываем JSON с вопросами
                questions = json.loads(research_type.questions)
                # Создаем временный атрибут для удобства
                research_type.questions_decoded = questions
            except json.JSONDecodeError:
                logger.error(f'Ошибка декодирования JSON для типа опроса {research_type_id}')
                research_type.questions_decoded = []
        return research_type


class CRUDResearchInstance(CRUDBase):
    """
    Класс для CRUD операций для экземпляров однотипных опросов (research).
    """

    async def create_instance(
        self,
        session: AsyncSession,
        instance_in: ResearchInstanceCreateSchema,
        auto_commit: bool = DefaultConstants.AUTO_COMMIT,
    ) -> ResearchInstance:
        """Создает новый экземпляр опроса."""
        instance_data = instance_in.model_dump()
        instance_db = self.model(**instance_data)
        try:
            session.add(instance_db)
            if auto_commit:
                await session.commit()
                await session.refresh(instance_db)
        except Exception as error:
            await session.rollback()
            logger.error(f'{TextErrorConstants.CREATE_SERVER_LOG} {self.model.__name__}: {error}')
            raise error
        return instance_db

    async def update_instance(
        self,
        session: AsyncSession,
        instance_db: ResearchInstance,
        instance_in: ResearchInstanceUpdateSchema,
        auto_commit: bool = DefaultConstants.AUTO_COMMIT,
    ) -> ResearchInstance:
        """Обновляет экземпляр опроса."""
        instance_data = jsonable_encoder(instance_db)
        update_data = instance_in.model_dump(exclude_unset=True)

        # Если обновляются ответы, преобразуем их в JSON
        if 'answers' in update_data:
            update_data['answers'] = json.dumps(update_data['answers'], ensure_ascii=False)

        # Если статус меняется на завершенный, устанавливаем время завершения
        if update_data.get('status') == 'COMPLETED' and not instance_db.completed_at:
            update_data['completed_at'] = datetime.utcnow()

        for field in instance_data:
            if field in update_data:
                setattr(instance_db, field, update_data[field])

        try:
            session.add(instance_db)
            if auto_commit:
                await session.commit()
                await session.refresh(instance_db)
        except Exception as error:
            await session.rollback()
            logger.error(f'{TextErrorConstants.UPDATE_SERVER_LOG} {self.model.__name__}: {error}')
            raise error
        return instance_db

    async def get_by_user(
        self,
        session: AsyncSession,
        user_id: UUID,
        company_id: Optional[int] = None,
    ) -> List[ResearchInstance]:
        """Получает все экземпляры опросов для пользователя."""
        filters = {'user_id': user_id}
        if company_id:
            # Добавляем фильтр по компании через связь с типом опроса
            query = (
                select(ResearchInstance)
                .join(ResearchType)
                .where(
                    and_(
                        ResearchInstance.user_id == user_id, ResearchType.company_id == company_id
                    )
                )
            )
            result = await session.execute(query)
            return result.scalars().all()

        return await self.get_multi(session, filters=filters, order_by=['-started_at'])

    async def get_by_research_type(
        self,
        session: AsyncSession,
        research_type_id: int,
    ) -> List[ResearchInstance]:
        """Получает все экземпляры для конкретного типа опроса."""
        return await self.get_multi(
            session, filters={'research_type_id': research_type_id}, order_by=['-started_at']
        )

    async def get_with_answers(
        self,
        session: AsyncSession,
        instance_id: int,
    ) -> Optional[ResearchInstance]:
        """Получает экземпляр опроса с расшифрованными ответами."""
        instance = await self.get(session, instance_id)
        if instance and instance.answers:
            try:
                # Расшифровываем JSON с ответами
                answers = json.loads(instance.answers)
                # Создаем временный атрибут для удобства
                instance.answers_decoded = answers
            except json.JSONDecodeError:
                logger.error(f'Ошибка декодирования JSON для экземпляра {instance_id}')
                instance.answers_decoded = {}
        return instance

    async def get_statistics(
        self,
        session: AsyncSession,
        research_type_id: int,
    ) -> Dict[str, Any]:
        """Получает статистику по типу опроса."""
        # Общее количество ответов
        total_query = select(func.count(ResearchInstance.id)).where(
            ResearchInstance.research_type_id == research_type_id
        )
        total_result = await session.execute(total_query)
        total_responses = total_result.scalar()

        # Завершенные ответы
        completed_query = select(func.count(ResearchInstance.id)).where(
            and_(
                ResearchInstance.research_type_id == research_type_id,
                ResearchInstance.status == 'COMPLETED',
            )
        )
        completed_result = await session.execute(completed_query)
        completed_responses = completed_result.scalar()

        # В процессе
        in_progress_query = select(func.count(ResearchInstance.id)).where(
            and_(
                ResearchInstance.research_type_id == research_type_id,
                ResearchInstance.status == 'IN_PROGRESS',
            )
        )
        in_progress_result = await session.execute(in_progress_query)
        in_progress_responses = in_progress_result.scalar()

        # Среднее время завершения
        avg_time_query = select(
            func.avg(
                func.extract('epoch', ResearchInstance.completed_at - ResearchInstance.started_at)
            )
        ).where(
            and_(
                ResearchInstance.research_type_id == research_type_id,
                ResearchInstance.status == 'COMPLETED',
                ResearchInstance.completed_at.isnot(None),
            )
        )
        avg_time_result = await session.execute(avg_time_query)
        average_completion_time = avg_time_result.scalar()

        return {
            'total_responses': total_responses or 0,
            'completed_responses': completed_responses or 0,
            'in_progress_responses': in_progress_responses or 0,
            'average_completion_time': average_completion_time,
        }


# Создаем экземпляры CRUD классов
research_type_crud = CRUDResearchType(ResearchType)
research_instance_crud = CRUDResearchInstance(ResearchInstance)
