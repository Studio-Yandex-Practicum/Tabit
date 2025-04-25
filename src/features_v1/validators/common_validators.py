from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from src.crud import CRUDBase

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
