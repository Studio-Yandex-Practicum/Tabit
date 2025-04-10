import base64

import aiofiles
from fastapi import HTTPException, status

from src.utils.constants import BASE64_STARTSWITH, Directory, TextError
from src.utils.directory import create_folder


async def base64image(str_base64: str, name: str, directory: str = Directory.WAIF) -> str:
    """
    По переданным данным создаст файл-картинку. Сохранить её и вернет путь до неё.

    Параметры:
        - str_base64: строка, содержащая закодированную в base64 картинку;
        - name: строка, содержащие будущее название файла (без расширения);
        - directory: строка, содержащая название директории для хранения файла.
    """
    if not (isinstance(str_base64, str) and str_base64.startswith(BASE64_STARTSWITH)):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=TextError.BASE64_TYPE,
        )
    try:
        format_image, image_str = str_base64.split(';base64,')
        extension = format_image.split('/')[-1]
        name_file = f'{name}.{extension}'
        value_image_file = base64.b64decode(image_str)
        path_directory = f'{Directory.MEDIA}/{directory}'
        await create_folder(path_directory)
        path_file = f'{path_directory}/{name_file}'
        async with aiofiles.open(path_file, 'wb') as file:
            await file.write(value_image_file)
    except Exception as error:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=TextError.BASE64_FATAL.format(
                image=directory,
                error_class=error.__class__.__name__,
                error_text=error,
            ),
        )
    return path_file
