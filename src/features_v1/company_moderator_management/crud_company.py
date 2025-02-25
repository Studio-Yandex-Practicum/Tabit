"""Модуль CRUD для компании."""

from typing import Any, List

from fastapi.responses import FileResponse

from src.core.crud_base import CRUDBase
from src.models import Company


class CRUDCompany(CRUDBase):
    """CRUD операции для модели компании."""

    async def get_import(
        self,
        objects_in: List,
        file_name: str,
    ) -> Any:
        """
        Импортирует записи в файл .txt.
        Параметры метода:
            objects_in: список объектов для импорта
            file_name: имя импортируемого файла без расширения.
        """
        with open(f'{file_name}.txt', 'w') as file:
            count = 0
            table_titles = []
            for entity in objects_in:
                entity_string = []
                for key, value in entity.__dict__.items():
                    if key not in (
                        '_sa_instance_state',
                        'updated_at',
                        'created_at',
                        'hashed_password',
                    ):
                        entity_string.append(str(value))
                        table_titles.append(key)
                if count == 0:
                    file.write(f'{"  ".join(table_titles)}\n')
                file.write(f'{"  ".join(entity_string)}\n')
                count += 1
        return FileResponse(path=f'{file_name}.txt', filename=f'{file_name}.txt')


company_crud = CRUDCompany(Company)
