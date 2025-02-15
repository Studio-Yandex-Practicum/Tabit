FROM python:3.12

WORKDIR /app

# Устанавливаем Poetry
RUN pip install --no-cache-dir poetry==1.5

# Настраиваем Poetry
ENV POETRY_VIRTUALENVS_IN_PROJECT=true \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

# Копируем файлы зависимостей перед установкой
COPY pyproject.toml poetry.lock /app/

# Устанавливаем зависимости (включая dev, если нужен)
RUN poetry install --no-root --all-extras --with dev --no-interaction

# Копируем исходный код
COPY . /app/

# Запускаем сервер
CMD ["poetry", "run", "uvicorn", "src.main:app_v1", "--host", "0.0.0.0", "--port", "8000", "--reload"]
