from src.crud import CRUDBase
from src.problems.models import Problem


class CRUDProblem(CRUDBase):
    """CRUD операции для модели проблемы."""

    pass


problem_crud = CRUDProblem(Problem)
