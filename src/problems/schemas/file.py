import os
from datetime import datetime

from pydantic import BaseModel, field_validator

allowed_file_extensions = ('.pdf', '.doc', '.docx')
allowed_size_file = 10 * 1024 * 1024


class BaseFileSchema(BaseModel):
    file_path: str
    entity_id: int
    created_at: datetime
    updated_at: datetime


    @field_validator('file_path')
    def validate_file(cls, path: str) -> str:
        match path:
            case _ if not any(
                    path.endswith(ext) for ext in allowed_file_extensions
            ):
                raise ValueError(
                    f'Файл должен иметь расширение: '
                    f'{", ".join(allowed_file_extensions)}'
                )
            case _ if os.path.getsize(path) > allowed_size_file:
                raise ValueError(
                    f'Размер файла не должен превышать '
                    f'{allowed_size_file / (1024 * 1024)} МБ'
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