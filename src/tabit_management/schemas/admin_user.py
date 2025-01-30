from uuid import UUID

from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate


# TODO: Все схемы в этом файле нужно описать нормально, сейчас это заглушки.
class AdminReadSchema(BaseUser[UUID]):
    pass


class AdminCreateSchema(BaseUserCreate):
    pass


class AdminUpdateSchema(BaseUserUpdate):
    pass
