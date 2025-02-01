FROM python:3.12

WORKDIR /app

RUN pip install --no-cache-dir poetry==1.5

COPY pyproject.toml poetry.lock /app/

RUN poetry install --no-root --no-dev

COPY . /app/

CMD ["poetry", "run", "uvicorn", "src.main:app_v1", "--host", "0.0.0.0", "--port", "8000"]
