.PHONY: up down logs init-migrations apply-migrations reset-db init-db run clean-volumes

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

# Полный сброс базы данных
reset-db: clean-volumes up apply-migrations
	@echo "Database reset and migrations applied."

# Удаление Docker volumes (очистка данных базы)
clean-volumes:
	docker compose -f infra/docker-compose.local.yaml down -v
	@echo "Docker volumes removed. Database data reset."

# Полный процесс инициализации базы данных
init-db: up init-migrations apply-migrations
	@echo "Database initialized and migrations applied."

# Запуск приложения с uvicorn
run:
	poetry run uvicorn src.main:app_v1 --port 8000 --reload
