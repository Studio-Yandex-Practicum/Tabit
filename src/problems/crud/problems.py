from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import CRUDBase, CRUDBaseWithAssociations
from src.problems.crud.association_utils import create_associations
from src.problems.models import AssociationUserProblem, Problem
from src.problems.schemas.problem import ProblemCreateSchema, ProblemUpdateSchema
from src.constants import TextError
from src.problems.schemas.problem import ProblemCreateSchema
from src.users.models import UserTabit
from src.companies.models import Company
from src.logger import logger
from src.problems.models.enums import ColorProblem, StatusProblem, TypeProblem
from src.problems.models.association_models import AssociationUserProblem
from sqlalchemy import delete, select, Table
from src.constants import (
    DEFAULT_AUTO_COMMIT,
    DEFAULT_LIMIT,
    DEFAULT_SKIP,
    TextError,
)
from src.crud import ModelType
from fastapi.encoders import jsonable_encoder

from typing import Any


class CRUDProblem(CRUDBaseWithAssociations):
    """CRUD операции для модели проблемы."""

    async def create_problem_with_members(
        self,
        session: AsyncSession,
        problem_in: ProblemCreateSchema,
        owner: UserTabit,
        company: Company,
    ):
        problem_data = problem_in.model_dump()
        members = problem_data.pop('members') if 'members' in problem_data else None
        default_data = {
            'owner_id': owner.id,
            'company_id': company.id,
            'status': StatusProblem.NEW
        }
        problem_data.update(default_data)
        problem_db = self.model(**problem_data)
        try:
            session.add(problem_db)
            await session.flush()
            if members:
                members.append(owner.id)
                members = set(members)
                associations_data = [
                    self.associations_model(
                        left_id=member,
                        right_id=problem_db.id,
                        status=(True if member == owner.id else False),
                    ) for member in members
                ]
                session.add_all(associations_data)
            await session.commit()
            await session.refresh(problem_db)
        except Exception as error:
            await session.rollback()
            logger.error(f'{TextError.SERVER_CREATE_LOG} {self.model.__name__}: {error}')
            raise error
        return problem_db

    async def update_problem(
        self,
        session: AsyncSession,
        problem_db: Problem,
        problem_in: ProblemUpdateSchema,
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
        problem_data = jsonable_encoder(problem_db)
        problem_update_data = problem_in.model_dump(exclude_unset=True)
        members = problem_update_data.pop('members') if 'members' in problem_update_data else None

        for field in problem_data:
            if field in problem_update_data:
                setattr(problem_db, field, problem_update_data[field])

        try:
            session.add(problem_db)
            await session.flush()

            if members is not None:
                if problem_db.owner_id:
                    members.append(problem_db.owner_id)
                members = set(members)

                add_rows, delete_rows = self.get_data_associations_for_updata(
                    problem_data['members'],
                    members,
                )

                if add_rows:
                    associations_data = [
                        self.associations_model(
                            left_id=member,
                            right_id=problem_db.id,
                            status=False,
                        ) for member in add_rows
                    ]
                    session.add_all(associations_data)

                await session.execute(
                    delete(self.associations_model).where(
                        self.associations_model.right_id == problem_db.id,
                        self.associations_model.left_id.in_(delete_rows),
                    )
                )

            await session.commit()
            await session.refresh(problem_db)

        except Exception as error:
            await session.rollback()
            logger.error(f'{TextError.SERVER_UPDATE_LOG} {self.model.__name__}: {error}')
            raise error

        return problem_db

    async def edit_status_field_associations(
        self,
        session: AsyncSession,
        problem: Problem,
        user: UserTabit
    ) -> Problem:
        # TODO: Есть ли необходимость проверять, что статус уже True?
        association_row = await session.execute(
            select(self.associations_model).where(
                self.associations_model.right_id == problem.id,
                self.associations_model.left_id == user.id,
            )
        )
        associations_data = association_row.scalars().first()
        associations_data.status = True  # type: ignore

        try:
            session.add(associations_data)
            await session.commit()
            await session.refresh(problem)
        except Exception as error:
            await session.rollback()
            logger.error(
                f'{TextError.SERVER_UPDATE_LOG} {self.associations_model.__name__}: {error}'
            )
            raise error

        return problem


problem_crud = CRUDProblem(Problem, AssociationUserProblem)
