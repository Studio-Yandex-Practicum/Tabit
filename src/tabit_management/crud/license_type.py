from src.crud import CRUDBase
from src.tabit_management.models import LicenseType


class CRUDLicenseType(CRUDBase):
    """CRUD операций для моделей лицензий компаний."""

    pass


license_type_crud = CRUDLicenseType(LicenseType)
