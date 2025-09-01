from .company import CompanyAdmin, DepartmentAdmin
from .user import CompanyUserAdmin, TabitAdminUserAdmin
from .tag import UserTagAdmin
from .license_type import LicenseTypeAdmin


all_admin_views = [
    CompanyAdmin,
    CompanyUserAdmin,
    DepartmentAdmin,
    LicenseTypeAdmin,
    TabitAdminUserAdmin,
    UserTagAdmin,
]
