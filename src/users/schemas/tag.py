from datetime import date

from pydantic import BaseModel, ConfigDict, Field

from src.constants import LENGTH_NAME_USER, MIN_LENGTH_NAME
from src.users.constants import title_company_id_tag, title_name_tag


class TagUserUpdateSchema(BaseModel):
    """
    Параметры:
        name: Имя тега
    """

    name: str = Field(
        ...,
        min_length=MIN_LENGTH_NAME,
        max_length=LENGTH_NAME_USER,
        title=title_name_tag,
    )

    model_config = ConfigDict(
        title="Схема изменения тэгов",
        description="Схема для частичного изменения тэгов пользователей"
    )


class TagUserCreateSchema(TagUserUpdateSchema):
    """
    Параметры:
        company_id: Идентификатор компании, в которой будет использоваться тэг.
    """

    company_id: int = Field(
        ...,
        title=title_company_id_tag,
    )

    model_config = ConfigDict(
        title="Схема создания тэгов",
        description="Схема для создания тэгов пользователей"
    )


class TagUserResponseSchema(BaseModel):
    """
    Параметры:
        id: Идентефикатор тэга.
        name: Имя тега.
        company_id: Идентификатор компании, в которой будет использоваться тэг.
        created_at: Дата создания тэга.
        updated_at: Дата изменения тэга.
    """

    id: int
    name: str
    company_id: int
    created_at: date
    updated_at: date

    model_config = ConfigDict(
        from_attributes=True,
        title="Схема тэгов",
        description="Схема тэгов пользователей для ответов"
    )
