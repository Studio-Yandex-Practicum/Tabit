FROM python:3.12

WORKDIR /app

# Устанавливаем Poetry
RUN pip install --no-cache-dir poetry==1.5

# Настраиваем Poetry, чтобы виртуальное окружение создавалось ВНУТРИ проекта
ENV POETRY_VIRTUALENVS_IN_PROJECT=true
RUN poetry config virtualenvs.in-project true

# Устанавливаем переменные окружения для корректного поиска зависимостей
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONUNBUFFERED=1

# Копируем только файлы зависимостей (ускоряет сборку)
COPY pyproject.toml poetry.lock /app/

# Проверяем, есть ли проблемы с зависимостями, затем устанавливаем их
RUN poetry check && \
    if [ ! -d "/app/.venv" ]; then \
        poetry install --no-root --all-extras --with dev --no-interaction; \
    fi

# Копируем весь проект
COPY . /app/

ENV DATABASE_URL=postgresql+asyncpg://$POSTGRES_USER:$POSTGRES_PASSWORD@$DB_HOST:$PORT_BD_POSTGRES/$POSTGRES_DB

# Запускаем проект через poetry
CMD ["sh", "-c", "poetry env use python && poetry install --no-root --all-extras --with dev && poetry run python -m src.main"]
