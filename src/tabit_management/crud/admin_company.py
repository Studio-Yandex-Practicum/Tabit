from src.models import Company
from src.core.crud_base import CRUDBase


class CRUDAdminCompany(CRUDBase):
    """CRUD операций для модели компании от лица админа."""

    pass


admin_company_crud = CRUDAdminCompany(Company)
