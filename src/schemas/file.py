import os
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

ALLOWED_FILE_EXTENSIONS = ('.pdf', '.doc', '.docx')
ALLOWED_SIZE_FILE = 10 * 1024 * 1024  # 10Mb


class FileBaseSchema(BaseModel):
    """Базовая схема файла.

    Определяет базовые поля файла.
    Поля:
        file_path: Путь к файлу.
        entity_id: ID связанной сущности.
        created_at: Время создания.
        updated_at: Время обновления.
    """

    file_path: Annotated[
        str,
        StringConstraints(pattern=r'.*\.(pdf|doc|docx)$', min_length=1),
        Field(...),
    ]
    entity_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(extra='forbid')

    @field_validator('file_path', mode='after')
    @classmethod
    def validate_file_size_and_existence(cls, path: str) -> str:
        """Проверяет размер и существование файла."""
        if not os.path.exists(path):
            raise ValueError(f'Файла по адресу {path} не существует')
        if os.path.getsize(path) > ALLOWED_SIZE_FILE:
            raise ValueError(
                f'Размер файла не должен превышать ' f'{ALLOWED_SIZE_FILE / (1024 * 1024)} МБ'
            )
        return path


class FileCreateSchema(FileBaseSchema):
    """Схема для создания файла.

    Наследуется от базовой схемы без изменений.
    """


class FileUpdateSchema(FileBaseSchema):
    """Схема для обновления файла.

    Наследуется от базовой схемы без изменений.
    """


class FileResponseSchema(FileBaseSchema):
    """Схема файла для ответа.

    Определяет данные файла из БД.
    Поля:
        id: Идентификатор файла.
        file_path: Путь к файлу.
        entity_id: ID связанной сущности.
        created_at: Время создания.
        updated_at: Время обновления.
    """

    id: int

    model_config = ConfigDict(from_attributes=True, extra='forbid')
