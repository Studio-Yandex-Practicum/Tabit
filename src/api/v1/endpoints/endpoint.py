from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def main_page() -> str:
    """
    Представление главной страницы сайта

    Пока здесь ничего нет - в работе...
    """
    return "Main page"
