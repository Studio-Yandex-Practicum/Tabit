from .endpoint import router as main_page_router  # noqa
from .department import router as department_router  # noqa
from .companies import router as companies_router  # noqa: F401

__all__ = [
    'main_page_router',
    'department_router',
    'companies_router',
]
