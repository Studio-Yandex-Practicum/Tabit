.PHONY: up down logs init-migrations apply-migrations drop-db reset-db init-db run

# Docker Compose команды
up:
	docker compose -f infra/docker-compose.local.yaml up -d

down:
	docker compose -f infra/docker-compose.local.yaml down

logs:
	docker compose -f infra/docker-compose.local.yaml logs -f

# Команда для создания миграции
init-migrations:
	poetry run alembic revision --autogenerate -m "initial migration"

# Команда для применения миграций
apply-migrations:
	poetry run alembic upgrade head

# Удаление базы данных (только с использованием psql)
drop-db:
	docker exec -i postgres_local psql -U $(POSTGRES_USER) -d postgres -c "DROP DATABASE IF EXISTS $(POSTGRES_DB);"
	docker exec -i postgres_local psql -U $(POSTGRES_USER) postgres -c "CREATE DATABASE $(POSTGRES_DB);"

# Полный сброс базы данных
reset-db: drop-db apply-migrations
	@echo "Database reset and migrations applied."

# Полный процесс инициализации базы данных
init-db: up init-migrations apply-migrations
	@echo "Database initialized and migrations applied." logs

# Запуск приложения с uvicorn
run:
	poetry run uvicorn src.main:app_v1 --port 8000 --reload
