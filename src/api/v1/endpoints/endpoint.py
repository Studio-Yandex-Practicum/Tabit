from fastapi import APIRouter
from src.logger import logger

router = APIRouter()


@router.get('/')
async def main_page() -> str:
    """
    Представление главной страницы сайта

    Пока здесь ничего нет - в работе...
    """
    logger.info('Main Page')

    return 'Main page'
