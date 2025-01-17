import typer

from .base_runner import seed_all
from src.database import async_session

app = typer.Typer()


@app.command()
def seed_all_data():
    """
    Генерация тестовых данных для всех сущностей.
    """

    async def run():
        async with async_session() as session:
            await seed_all(session)

    typer.echo('Начинаем генерацию всех тестовых данных...')
    typer.run(run)
    typer.echo('Генерация завершена!')


if __name__ == '__main__':
    app()
