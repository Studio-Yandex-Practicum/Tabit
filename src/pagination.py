from fastapi_pagination import Page
from pydantic import Field
from typing import Generic, Optional, Sequence, TypeVar

T = TypeVar("T")


class CustomPage(Page[T], Generic[T]):
    """Кастомная страница пагинации"""

    has_next: bool = Field(..., description="Наличие следующей страницы")
    has_previous: bool = Field(..., description="Наличие предыдущей страницы")

    @classmethod
    def create(
        cls, items: Sequence[T], total: int, page: int, size: int
    ) -> "CustomPage[T]":
        return cls(
            items=items,
            total=total,
            page=page,
            size=size,
            has_next=(page * size < total),
            has_previous=(page > 1),
        )


class BasePagination(Generic[T]):
    """
    Базовый класс для пагинации.
    Назначение:
        Реализация базового класса для пагинации необходима для унификации и
        стандартизации работы с пагинацией на уровне всего проекта.
        Это решит проблему дублирования кода и обеспечит единый подход
        к обработке пагинации во всех модулях,
        что упростит поддержку и расширение функциональности.
    Параметры:
        items (Sequence[T]): Список всех элементов.
        page (int): Номер текущей страницы (начинается с 1).
        page_size (int): Количество элементов на странице.
        total (Optional[int]): Общее количество элементов.
    """

    def __init__(
            self,
            items: Sequence[T],
            page: int,
            page_size: int,
            total: Optional[int]
    ):
        if page < 1:
            raise ValueError("Номер страницы должен быть больше 0.")
        if page_size < 1:
            raise ValueError("Размер страницы должен быть больше 0.")
        if total is not None:
            self.total = total
        else:
            self.total = len(items)
        self.items = items
        self.page = page
        self.page_size = page_size

    def get_page(self) -> int:
        """Возвращает номер текущей страницы."""
        return self.page

    def get_page_size(self) -> int:
        """Возвращает размер страницы (количество элементов на странице)."""
        return self.page_size

    def get_total(self) -> int:
        """Возвращает общее количество элементов."""
        return self.total

    def get_items(self) -> Sequence[T]:
        """Возвращает элементы для текущей страницы."""
        start = (self.page - 1) * self.page_size
        end = start + self.page_size
        return self.items[start:end]
    
    def to_page(self) -> Page[T]:
        """"Преобразует данные в формат Page."""
        return Page(
            items=self.get_items(),
            total=self.get_total(),
            page=self.get_page(),
            size=self.get_page_size(),
        )
