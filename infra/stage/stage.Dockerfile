ARG PYTHON_VERSION=3.12-slim

FROM python:${PYTHON_VERSION}-slim

ARG POETRY_VERSION=1.7.1
ARG APP_PORT=8000
ARG APP_VERSION=1

WORKDIR /app

RUN pip install --no-cache-dir poetry==${POETRY_VERSION}

ENV POETRY_VIRTUALENVS_IN_PROJECT=true \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH" \
    APP_PORT=${APP_PORT} \
    APP_VERSION=${APP_VERSION}

COPY pyproject.toml poetry.lock /app/

RUN poetry install --no-root --all-extras --with dev --no-interaction

COPY . /app/

CMD ["sh", "-c", "poetry run uvicorn src.main:app_v${APP_VERSION} --host 0.0.0.0 --port ${APP_PORT}"]
