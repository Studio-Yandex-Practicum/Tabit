from fastapi import HTTPException, status as status_
from fastapi.encoders import jsonable_encoder
from sqlalchemy import and_, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.constants import TextError as ErrorText
from src.companies.models import Company
from src.constants import TextError
from src.crud import CRUDBaseWithAssociations
from src.logger import logger
from src.problems.models import AssociationUserProblem, Problem
from src.problems.models.enums import StatusProblem
from src.problems.schemas.problem import ProblemCreateSchema, ProblemUpdateSchema
from src.users.models import UserTabit


class CRUDProblem(CRUDBaseWithAssociations):
    """CRUD операции для модели проблемы."""

    async def create_problem_with_members(
        self,
        session: AsyncSession,
        problem_in: ProblemCreateSchema,
        owner: UserTabit,
        company: Company,
    ) -> Problem:
        """
        Для создания записи в таблице Проблемы.

        Параметры:
            session: Асинхронная сессия SQLAlchemy.
            problem_in: данные для изменения в виде схемы.
            owner: экземпляр модели пользователя, автор проблемы.
            company: экземпляр модели компании, в которой возникла проблема.
        Возвращает:
            Экземпляр модели проблемы после создания.
        """
        problem_data = problem_in.model_dump()
        members = problem_data.pop('members') if 'members' in problem_data else []
        default_data = {
            'owner_id': owner.id,
            'company_id': company.id,
            'status': StatusProblem.NEW,
        }
        problem_data.update(default_data)
        problem_db = self.model(**problem_data)
        try:
            session.add(problem_db)
            await session.flush()
            members.append(owner.id)
            members = set(members)
            associations_data = [
                self.associations_model(
                    left_id=member,
                    right_id=problem_db.id,
                    status=(True if member == owner.id else False),
                )
                for member in members
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
        """
        Для изменения записи в таблице Проблемы.

        Параметры:
            session: Асинхронная сессия SQLAlchemy.
            problem_db: экземпляр модели проблемы.
            problem_in: данные для изменения в виде схемы.
        Возвращает:
            Экземпляр модели проблемы после изменения.
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
                        )
                        for member in add_rows
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
        user: UserTabit,
        status: bool = True,
    ) -> Problem:
        """
        Для изменения статуса участника решения проблемы.

        Изменит поле status в связной модели.

        Параметры:
            session: Асинхронная сессия SQLAlchemy.
            problem: экземпляр модели проблемы.
            user: экземпляр модели пользователя.
            status: какой присвоить статус участнику.
        Возвращает:
            Экземпляр модели проблемы после изменения.
        """
        # TODO: Есть ли необходимость проверять, что статус уже True? Это лишние запросы.
        association_row = await session.execute(
            select(self.associations_model).where(
                self.associations_model.right_id == problem.id,
                self.associations_model.left_id == user.id,
            )
        )
        associations_data = association_row.scalars().first()

        if associations_data:
            associations_data.status = status
        else:
            raise HTTPException(
                status_code=status_.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=ErrorText.NOT_IS_MEMBERS,
            )

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

    async def get_all_open_problem_from_association_by_user_id(
        self,
        session: AsyncSession,
        user: UserTabit,
    ) -> list[AssociationUserProblem]:
        """
        Получить записи из связной таблице по id пользователя, где пользователь уже подтвердил
        своё участие, а проблем ещё не закрыта.

        Параметры:
            session: Асинхронная сессия SQLAlchemy.
            user: экземпляр модели пользователя.
        Возвращает:
            Список записей из связной модели.
        """
        query = and_(
            self.associations_model.left_id == user.id,
            self.associations_model.status == True,  # noqa: E712
            self.model.status != StatusProblem.COMPLETED,
        )
        request = select(self.associations_model).join(self.model).where(query)
        association_rows = await session.execute(request)
        return association_rows.scalars().all()  # type: ignore


problem_crud = CRUDProblem(Problem, AssociationUserProblem)
