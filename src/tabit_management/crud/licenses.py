from src.crud import CRUDBase
from src.tabit_management.models import LicenseType


class CRUDLicenseType(CRUDBase):
    """CRUD операций для модели компании."""

    pass


license_type_crud = CRUDLicenseType(LicenseType)
