class BaseSeeder:
    """
    Базовый класс для всех асинхронных сидеров.
    """

    def __init__(self, count):
        """
        Инициализация сидера.
        :param count: количество записей для генерации
        """
        self.count = count

    async def run(self, session):
        """
        Метод, который должен быть реализован в каждом дочернем классе.
        :param session: асинхронная сессия SQLAlchemy
        """
        raise NotImplementedError('Метод "run" должен быть реализован в дочернем классе')
