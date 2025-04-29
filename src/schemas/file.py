import os
from datetime import datetime
from typing import Annotated

from pydantic import BaseModel, ConfigDict, Field, StringConstraints, field_validator

ALLOWED_FILE_EXTENSIONS = ('.pdf', '.doc', '.docx')
ALLOWED_SIZE_FILE = 10 * 1024 * 1024  # 10Mb


class FileBaseSchema(BaseModel):
    """
    Базовая схема файла.

    Определяет общие поля для схем файлов.

    Атрибуты:
        file_path (str): Путь к файлу, должен соответствовать расширениям .pdf, .doc или .docx.
        entity_id (int): Идентификатор связанной сущности.
        created_at (datetime): Время создания файла.
        updated_at (datetime): Время последнего обновления файла.

    Валидаторы:
        validate_file_size_and_existence: Проверяет существование файла и
            его размер (максимум 10 МБ).
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
    """
    Схема для создания файла.

    Используется для добавления нового файла через API.

    Атрибуты:
        file_path (str): Путь к файлу, должен соответствовать расширениям .pdf, .doc или .docx.
        entity_id (int): Идентификатор связанной сущности.
        created_at (datetime): Время создания файла.
        updated_at (datetime): Время последнего обновления файла.

    Валидаторы:
        validate_file_size_and_existence: Проверяет существование файла и
            его размер (максимум 10 МБ).
    """


class FileUpdateSchema(FileBaseSchema):
    """
    Схема для обновления файла.

    Используется для изменения данных файла через API.

    Атрибуты:
        file_path (str): Путь к файлу, должен соответствовать расширениям .pdf, .doc или .docx.
        entity_id (int): Идентификатор связанной сущности.
        created_at (datetime): Время создания файла.
        updated_at (datetime): Время последнего обновления файла.

    Валидаторы:
        validate_file_size_and_existence: Проверяет существование файла и
            его размер (максимум 10 МБ).
    """


class FileResponseSchema(FileBaseSchema):
    """
    Схема файла для ответа.

    Используется для возврата данных о файле из базы данных через API.

    Атрибуты:
        id (int): Идентификатор файла.
        file_path (str): Путь к файлу, должен соответствовать расширениям .pdf, .doc или .docx.
        entity_id (int): Идентификатор связанной сущности.
        created_at (datetime): Время создания файла.
        updated_at (datetime): Время последнего обновления файла.

    Валидаторы:
        validate_file_size_and_existence: Проверяет существование файла и
            его размер (максимум 10 МБ).
    """

    id: int

    model_config = ConfigDict(from_attributes=True, extra='forbid')
