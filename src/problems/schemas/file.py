import os
from datetime import datetime

from pydantic import BaseModel, field_validator

ALLOWED_FILE_EXTENSIONS = ('.pdf', '.doc', '.docx')
ALLOWED_SIZE_FILE = 10 * 1024 * 1024  # 10Mb


class BaseFileSchema(BaseModel):
    file_path: str
    entity_id: int
    created_at: datetime
    updated_at: datetime

    @field_validator('file_path')
    def validate_file(cls, path: str) -> str:
        match path:
            case _ if not any(path.endswith(ext) for ext in ALLOWED_FILE_EXTENSIONS):
                raise ValueError(
                    f'Файл должен иметь расширение: {", ".join(ALLOWED_FILE_EXTENSIONS)}'
                )
            case _ if os.path.getsize(path) > ALLOWED_SIZE_FILE:
                raise ValueError(
                    f'Размер файла не должен превышать {ALLOWED_SIZE_FILE / (1024 * 1024)} МБ'
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
