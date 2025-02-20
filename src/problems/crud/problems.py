from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.constants import TEXT_ERROR_NOT_FOUND
from src.crud import CRUDBase
from src.problems.crud.association_utils import create_associations
from src.problems.models import AssociationUserProblem, Problem
from src.problems.schemas.problem import ProblemCreateSchema, ProblemUpdateSchema


# TODO Надо доработать CRUD на получение и обновление проблем со списком участников
class CRUDProblem(CRUDBase):
    """CRUD операции для модели проблемы."""

    async def create_with_members(
        self, session: AsyncSession, problem_data: dict, members: list[UUID]
    ) -> Problem:
        """Создание встречи с участниками.

        Назначение:
            Создает новую встречу и добавляет участников через ассоциативную таблицу.
            Выполняет все операции в рамках одной транзакции.
        Параметры:
            session: Асинхронная сессия SQLAlchemy.
            problem_data: Словарь с данными для создания встречи.
            members: Список UUID участников встречи.
        Возвращаемое значение:
            Созданный объект встречи с обновленными данными.
        """
        try:
            problem_data['members'] = members
            problem_model = ProblemCreateSchema(**problem_data)
            created_problem = await self.create(session, problem_model)

            # Создаем ассоциации участников с встречей
            await create_associations(
                session=session,
                association_model=AssociationUserProblem,
                left_ids=members,
                right_id=created_problem.id,
                status=True,  # (Затычка, чтобы проверить создание проблемы со списком участников)
            )

            await session.commit()
            await session.refresh(created_problem)
            return created_problem

        except Exception as e:
            await session.rollback()
            raise e

    async def update_problem(
        self, session: AsyncSession, problem_id: int, problem_update: ProblemUpdateSchema
    ) -> Problem:
        """Обновление проблемы.

        Назначение:
            Обновляет данные проблемы в базе данных по её ID.
            Перед обновлением проверяет существование проблемы.
        Параметры:
            session: Асинхронная сессия SQLAlchemy.
            problem_id: ID проблемы для обновления.
            problem_update: Схема с данными для обновления проблемы.
        Возвращаемое значение:
            Обновленный объект проблемы.
        """
        db_obj = await self.get_or_404(session, problem_id)
        return await self.update(session, db_obj, problem_update)

    async def delete_problem(self, session: AsyncSession, problem_id: int) -> None:
        """Удаление проблемы.

        Назначение:
            Удаляет проблему из базы данных по её ID.
            Перед удалением проверяет существование проблемы.
        Параметры:
            session: Асинхронная сессия SQLAlchemy.
            problem_id: ID проблемы для удаления.
        Возвращаемое значение:
            None
        """
        db_obj = await self.get_or_404(session, problem_id)
        await self.remove(session, db_obj)

    async def get_with_owner(self, session: AsyncSession, problem_id: int) -> Problem:
        """
        Функция получения объекта Problem со связанным с ним объектом пользователя UserTabit.
        Возвращает объект модели Problem.

        problem_id: path-параметр, соответствующий id запрашиваемой проблемы
        """
        problem = await session.execute(
            select(self.model)
            .where(self.model.id == problem_id)
            .options(selectinload(self.model.owner))
        )
        problem = problem.scalar_one_or_none()
        if not problem:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=TEXT_ERROR_NOT_FOUND)
        return problem


problem_crud = CRUDProblem(Problem)
