from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def main_page():
    """
    Представление главной страницы.

    Заглушка для главной страницы сайта...
    """

    return "Main page"
