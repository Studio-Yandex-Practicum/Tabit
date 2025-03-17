from typing import Generic, TypeVar, Sequence, Optional

T = TypeVar("T")


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

    def has_next(self) -> bool:
        """Проверяет наличие следующей страницы."""
        return self.page * self.page_size < self.total

    def has_previous(self) -> bool:
        """Проверяет наличие предыдущей страницы."""
        return self.page > 1
