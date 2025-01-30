from uuid import UUID

from fastapi_users.schemas import BaseUser, BaseUserCreate, BaseUserUpdate


# TODO: Все схемы в этом файле нужно описать нормально, сейчас это заглушки.
class UserReadSchema(BaseUser[UUID]):
    pass


class UserCreateSchema(BaseUserCreate):
    pass


class UserUpdateSchema(BaseUserUpdate):
    pass
