from sqladmin import ModelView

from src.models.tag import UserTag


class UserTagAdmin(ModelView, model=UserTag):
    name = 'Тэг'
    name_plural = 'Тэги'
    icon = 'fa-solid fa-tag'

    column_list = [
        UserTag.id,
        UserTag.name,
        UserTag.company_id,
        UserTag.created_at,
        UserTag.updated_at,
    ]
    column_searchable_list = [
        UserTag.name,
    ]
    column_sortable_list = [UserTag.id, UserTag.name]
