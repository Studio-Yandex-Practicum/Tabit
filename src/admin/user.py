from sqladmin import ModelView

from src.models.user import CompanyUser, TabitAdminUser


class CompanyUserAdmin(ModelView, model=CompanyUser):
    name = 'Сотрудник'
    name_plural = 'Сотрудники'
    icon = 'fa-solid fa-user-tie'

    column_list = [
        CompanyUser.id,
        CompanyUser.name,
        CompanyUser.surname,
        CompanyUser.email,
        CompanyUser.role,
        CompanyUser.company_id,
        CompanyUser.current_department_id,
        CompanyUser.is_active,
        CompanyUser.is_superuser,
        CompanyUser.is_verified,
        CompanyUser.created_at,
    ]

    column_searchable_list = [
        CompanyUser.name,
        CompanyUser.surname,
        CompanyUser.email,
        CompanyUser.telegram_username,
    ]

    column_sortable_list = [
        CompanyUser.id,
        CompanyUser.name,
        CompanyUser.surname,
        CompanyUser.role,
        CompanyUser.company_id,
        CompanyUser.current_department_id,
        CompanyUser.is_active,
        CompanyUser.is_superuser,
        CompanyUser.is_verified,
    ]


class TabitAdminUserAdmin(ModelView, model=TabitAdminUser):
    name = 'Админ сервиса'
    name_plural = 'Админы сервиса'
    icon = 'fa-solid fa-shield-halved'

    column_list = [
        TabitAdminUser.id,
        TabitAdminUser.name,
        TabitAdminUser.surname,
        TabitAdminUser.email,
        TabitAdminUser.is_active,
        TabitAdminUser.is_superuser,
        TabitAdminUser.is_verified,
        TabitAdminUser.created_at,
    ]

    column_searchable_list = [
        TabitAdminUser.name,
        TabitAdminUser.surname,
        TabitAdminUser.email,
    ]

    column_sortable_list = [
        TabitAdminUser.id,
        TabitAdminUser.name,
        TabitAdminUser.surname,
        TabitAdminUser.is_active,
        TabitAdminUser.is_superuser,
        TabitAdminUser.is_verified,
    ]
