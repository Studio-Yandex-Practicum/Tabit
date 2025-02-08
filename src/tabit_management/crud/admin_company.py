from src.crud import CRUDBase
from src.companies.models import Company


class CRUDAdminCompany(CRUDBase):
    """CRUD операций для модели компании от лица админа."""

    pass


admin_company_crud = CRUDAdminCompany(Company)
