ARG PYTHON_VERSION=3.12

FROM python:${PYTHON_VERSION}-slim

ARG POETRY_VERSION=2.1.3
ARG APP_PORT=8000
ARG APP_VERSION=1

WORKDIR /app

RUN pip install --no-cache-dir poetry==${POETRY_VERSION}

ENV POETRY_VIRTUALENVS_IN_PROJECT=true \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH=/app \
    APP_PORT=${APP_PORT} \
    APP_VERSION=${APP_VERSION}

COPY pyproject.toml poetry.lock /app/

RUN poetry install --no-root --all-extras --with dev --no-interaction

COPY . /app/

# Копируем для заполнения тестовыми данными в контейнере
# TODO: в проде удалить это и из .dockerignore
# =====================================================================┐
COPY fake_data_factories/ ./fake_data_factories/
# =====================================================================┘

ENTRYPOINT ["/usr/local/bin/poetry", "run"]
CMD ["uvicorn", "src.main:app_v1", "--host", "0.0.0.0", "--port", "8000"]
