from src.core.crud_base import CRUDBase
from src.models import Company


class CRUDAdminCompany(CRUDBase):
    """CRUD операций для модели компании от лица админа."""

    pass


admin_company_crud = CRUDAdminCompany(Company)
