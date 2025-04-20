ARG PYTHON_VERSION=3.12-slim

FROM python:${PYTHON_VERSION}

WORKDIR /app

RUN pip install --no-cache-dir poetry==1.7.1

ENV POETRY_VIRTUALENVS_IN_PROJECT=true \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

COPY pyproject.toml poetry.lock /app/

RUN poetry install --no-root --all-extras --with dev --no-interaction

COPY . /app/

CMD ["/usr/local/bin/poetry", "run", "uvicorn", "src.main:app_v1", "--host", "0.0.0.0", "--port", "8000"]
