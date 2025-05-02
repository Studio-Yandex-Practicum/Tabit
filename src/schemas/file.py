import os
from datetime import datetime

from pydantic import BaseModel, field_validator

from src.schemas.constants import ValidationConstants


class BaseFileSchema(BaseModel):
    file_path: str
    entity_id: int
    created_at: datetime
    updated_at: datetime

    @field_validator('file_path')
    def validate_file(cls, path: str) -> str:
        match path:
            case _ if not any(
                path.endswith(ext) for ext in ValidationConstants.ALLOWED_FILE_EXTENSIONS
            ):
                raise ValueError(
                    'Файл должен иметь расширение: '
                    f'{", ".join(ValidationConstants.ALLOWED_FILE_EXTENSIONS)}'
                )
            case _ if os.path.getsize(path) > ValidationConstants.ALLOWED_FILE_SIZE:
                raise ValueError(
                    'Размер файла не должен превышать '
                    f'{ValidationConstants.ALLOWED_FILE_SIZE / (1024 * 1024)} МБ'
                )
            case _ if not os.path.exists(path):
                raise ValueError(f'Файла по адресу {path} не существует')
            case _:
                return path


class FileCreateSchema(BaseFileSchema):
    pass


class FileUpdateSchema(BaseFileSchema):
    pass


class FileResponseSchema(BaseFileSchema):
    id: int
