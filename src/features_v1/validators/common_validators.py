from uuid import UUID

from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import CRUDBase
from src.features_v1.constants import TextError
from src.models import CompanyUser

async def validator_check_object_exists(
    session: AsyncSession,
    model_crud: CRUDBase,
    object_id: int | UUID | None = None,
    object_slug: str | None = None,
):
    """Проверит наличие и вернет объект из таблицы по id или slug."""
    object_model = (
        await model_crud.get_or_404(session, object_id)
        if object_id
        else (await model_crud.get_by_slug(session, object_slug, raise_404=True))
    )
    return object_model


def validate_owner_object(user: CompanyUser, row_model):
    """
    Валидатор, проверит что у переданной модели автор переданный пользователь.
    Иначе ошибка 403
    """
    if user.id != row_model.owner.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=TextError.FORBIDDEN_OWNER,
        )