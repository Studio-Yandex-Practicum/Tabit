from sqladmin import ModelView

from src.models.license_type import LicenseType


class LicenseTypeAdmin(ModelView, model=LicenseType):
    name = 'Лицензия'
    name_plural = 'Лицензии'
    icon = 'fa-file-contract'

    column_list = [
        LicenseType.id,
        LicenseType.name,
        LicenseType.license_term,
        LicenseType.max_admins_count,
        LicenseType.created_at,
        LicenseType.updated_at,
    ]
    column_searchable_list = [
        LicenseType.name,
    ]
    column_sortable_list = [LicenseType.id, LicenseType.name]
