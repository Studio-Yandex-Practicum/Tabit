from fastapi import Depends
from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_depends import get_async_session


class ResourceOwnershipService:
    """
    Сервис для проверки владения ресурсами (ABAC компонент)

    Тип: ABAC
    Роли: Company User (применяется для проверки владения)
          Company Moderator (обычно имеет доступ ко всем ресурсам без проверки)

    Реализует бизнес-логику проверки прав на ресурсы на основе атрибутов.
    Этот класс является единственным местом в системе, где происходит
    проверка владения ресурсами на основе бизнес-правил.
    """

    def __init__(self, session: AsyncSession):
        self.session = session

    async def check_task_ownership(self, task_id: int | str, user_id: int | str) -> bool:
        """
        Проверяет, является ли пользователь владельцем задачи или исполнителем

        Тип: ABAC
        Роли: Company User

        Параметры:
        - task_id: ID задачи
        - user_id: ID пользователя

        Возвращает:
        - True, если пользователь создал задачу или является исполнителем
        - False в противном случае
        """
        from src.problems.models.task_models import AssociationUserTask, Task

        # Проверяем, является ли пользователь владельцем задачи
        owner_query = select(exists().where((Task.id == task_id) & (Task.owner_id == user_id)))
        owner_result = await self.session.execute(owner_query)
        if owner_result.scalar_one():
            return True

        # Проверяем, является ли пользователь исполнителем задачи
        executor_query = select(
            exists().where(
                (AssociationUserTask.task_id == task_id) & (AssociationUserTask.user_id == user_id)
            )
        )
        executor_result = await self.session.execute(executor_query)
        return executor_result.scalar_one()

    async def check_comment_ownership(self, comment_id: int | str, user_id: int | str) -> bool:
        """
        Проверяет, является ли пользователь автором комментария

        Тип: ABAC
        Роли: Company User

        Параметры:
        - comment_id: ID комментария
        - user_id: ID пользователя

        Возвращает:
        - True, если пользователь создал комментарий
        - False в противном случае
        """
        from src.problems.models.message_models import CommentFeed

        # Проверяем, является ли пользователь автором комментария
        query = select(
            exists().where((CommentFeed.id == comment_id) & (CommentFeed.owner_id == user_id))
        )

        result = await self.session.execute(query)
        return result.scalar_one()

    async def check_problem_ownership(self, problem_id: int | str, user_id: int | str) -> bool:
        """
        Проверяет, имеет ли пользователь права на управление проблемой

        Тип: ABAC
        Роли: Company User

        Параметры:
        - problem_id: ID проблемы
        - user_id: ID пользователя

        Возвращает:
        - True, если пользователь создал проблему или имеет права на управление
        - False в противном случае
        """
        from src.problems.models.problem_models import AssociationUserProblem, Problem

        # Проверяем, является ли пользователь владельцем проблемы
        owner_query = select(
            exists().where((Problem.id == problem_id) & (Problem.owner_id == user_id))
        )
        owner_result = await self.session.execute(owner_query)
        if owner_result.scalar_one():
            return True

        # Проверяем, является ли пользователь участником проблемы
        member_query = select(
            exists().where(
                (AssociationUserProblem.problem_id == problem_id)
                & (AssociationUserProblem.user_id == user_id)
            )
        )
        member_result = await self.session.execute(member_query)
        return member_result.scalar_one()

    async def check_message_ownership(self, message_id: int | str, user_id: int | str) -> bool:
        """
        Проверяет, является ли пользователь автором сообщения

        Тип: ABAC
        Роли: Company User

        Параметры:
        - message_id: ID сообщения
        - user_id: ID пользователя

        Возвращает:
        - True, если пользователь создал сообщение
        - False в противном случае
        """
        from src.problems.models.message_models import MessageFeed

        # Проверяем, является ли пользователь автором сообщения
        query = select(
            exists().where((MessageFeed.id == message_id) & (MessageFeed.owner_id == user_id))
        )

        result = await self.session.execute(query)
        return result.scalar_one()

    async def check_voting_ownership(self, voting_id: int | str, user_id: int | str) -> bool:
        """
        Проверяет, голосовал ли пользователь за вариант

        Тип: ABAC
        Роли: Company User

        Параметры:
        - voting_id: ID голосования
        - user_id: ID пользователя

        Возвращает:
        - True, если пользователь голосовал
        - False в противном случае
        """
        from src.problems.models.message_models import VotingByUser

        # Проверяем, голосовал ли пользователь за этот вариант
        query = select(
            exists().where(
                (VotingByUser.voting_id == voting_id) & (VotingByUser.user_id == user_id)
            )
        )

        result = await self.session.execute(query)
        return result.scalar_one()

    async def check_resource_ownership(
        self, resource_type: str, resource_id: int | str, user_id: int | str
    ) -> bool:
        """
        Универсальный метод для проверки владения ресурсом

        Тип: ABAC
        Роли: Company User (применяется для проверки владения)
              Company Moderator (обычно имеет доступ без проверки)

        Параметры:
        - resource_type: тип ресурса (task, comment, problem, message, voting)
        - resource_id: ID ресурса
        - user_id: ID пользователя

        Возвращает:
        - True, если пользователь имеет права на ресурс
        - False в противном случае

        Примечание: Этот метод является единственной точкой входа для проверки
        владения ресурсами во всей системе. Он делегирует проверку специализированным
        методам в зависимости от типа ресурса.
        """
        if resource_type == 'task':
            return await self.check_task_ownership(resource_id, user_id)
        elif resource_type == 'comment':
            return await self.check_comment_ownership(resource_id, user_id)
        elif resource_type == 'problem':
            return await self.check_problem_ownership(resource_id, user_id)
        elif resource_type == 'message':
            return await self.check_message_ownership(resource_id, user_id)
        elif resource_type == 'voting':
            return await self.check_voting_ownership(resource_id, user_id)
        else:
            # Неизвестный тип ресурса
            return False


# Фабрика для получения сервиса проверки владения ресурсами
def get_ownership_service(
    session: AsyncSession = Depends(get_async_session),
) -> ResourceOwnershipService:
    """
    Фабрика для создания сервиса проверки владения ресурсами

    Тип: ABAC

    Параметры:
    - session: асинхронная сессия SQLAlchemy

    Возвращает:
    - Экземпляр ResourceOwnershipService
    """
    return ResourceOwnershipService(session)
