from sqladmin import ModelView

from src.models.company import Company, Department


class CompanyAdmin(ModelView, model=Company):
    name = 'Компания'
    name_plural = 'Компании'
    icon = 'fa-solid fa-building'

    column_list = [
        Company.id,
        Company.name,
        Company.slug,
        Company.is_active,
        Company.created_at,
        Company.updated_at,
    ]
    column_searchable_list = [Company.name, Company.slug]
    column_sortable_list = [Company.id, Company.name, Company.is_active]


class DepartmentAdmin(ModelView, model=Department):
    name = 'Департамент'
    name_plural = 'Департаменты'
    icon = 'fa-solid fa-users'

    column_list = [
        Department.id,
        Department.name,
        Department.slug,
        Department.company_id,
    ]
    column_searchable_list = [Department.name, Department.slug]
    column_sortable_list = [Department.id, Department.name]
