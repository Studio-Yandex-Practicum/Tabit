FROM python:3.12

WORKDIR /app

RUN pip install --no-cache-dir poetry==1.5

ENV POETRY_VIRTUALENVS_IN_PROJECT=true \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.venv/bin:$PATH"

COPY ../pyproject.toml ../poetry.lock /app/

RUN poetry install --no-root --all-extras --with dev --no-interaction

COPY . /app/

# CMD ["poetry", "run", "uvicorn", "src.main:app_v1", "--host", "0.0.0.0", "--port", "8000", "--reload"]
# CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
CMD ["python", "src/main.py", "-r", "-h", "0.0.0.0", "-p", "8000"]
