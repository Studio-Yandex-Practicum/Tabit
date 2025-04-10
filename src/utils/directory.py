import os


async def create_folder(directory: str):
    """Если папка не создана - создаст её."""
    if not os.path.isdir(directory):
        os.mkdir(directory)
