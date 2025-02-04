from src.crud import CRUDBase
from src.companies.models import Company


class CRUDCompany(CRUDBase):
    """CRUD операций для модели компании."""

    pass


company_crud = CRUDCompany(Company)
