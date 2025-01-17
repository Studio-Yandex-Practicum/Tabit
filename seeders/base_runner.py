from sqlalchemy.ext.asyncio import AsyncSession

from seeders.user_seeder import UserSeeder


async def seed_all(session: AsyncSession):
    """
    Генерация тестовых данных для всех сущностей.
    :param session: асинхронная сессия SQLAlchemy
    """
    # Генерация пользователей
    user_seeder = UserSeeder()
    await user_seeder.run(session)

    # TODO: Добавить генерацию других сущностей и логи
    print('Все тестовые данные успешно сгенерированы!')
