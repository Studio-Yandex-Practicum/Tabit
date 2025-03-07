.PHONY: up down up-pgadmin down-pgadmin logs init-migrations apply-migrations reset-db init-db run clean-volumes

# Docker Compose команды
up:
	docker compose -f infra/docker-compose.local-db.yaml up -d

down:
	docker compose -f infra/docker-compose.local-db.yaml down

up-pgadmin:
	docker compose -f infra/docker-compose.local-with-pgadmin.yaml up -d

down-pgadmin:
	docker compose -f infra/docker-compose.local-with-pgadmin.yaml down

logs:
	docker compose -f infra/docker-compose.local-db.yaml logs -f

# Команда для остановки контейнеров и удаления volumes, связанных с конфигурацией
down-pgadmin-volumes:
	docker compose -f infra/docker-compose.local-with-pgadmin.yaml down -v

# Команда для создания миграции
init-migrations:
	poetry run alembic revision --autogenerate -m "initial migration"

# Команда создания автогенерируемой миграции с возможностью передачи коммита
# через флаг m='...' для составления названия миграции
auto-migration:
	poetry run alembic revision --autogenerate -m "$(m)"

# Команда создания пустой миграции с возможностью передачи коммита
# через флаг m='...' для составления названия миграции
empty-migration:
	poetry run alembic revision -m "$(m)"

# Команда для применения миграций
apply-migrations:
	poetry run alembic upgrade head

# Полный сброс базы данных
reset-db: clean-volumes up apply-migrations
	@echo "Database reset and migrations applied."

# Удаление Docker volumes (очистка данных базы)
clean-volumes:
	docker compose -f infra/docker-compose.local-db.yaml down -v
	@echo "Docker volumes removed. Database data reset."

# Полный процесс инициализации базы данных
init-db: up init-migrations apply-migrations
	@echo "Database initialized and migrations applied."

# Запуск приложения с uvicorn
run:
	poetry run uvicorn src.main:app_v1 --port 8000 --reload

# Создаст в базе данных суперпользователя.
create-superuser:
	python src/main.py -c

fill-db:
	poetry run python fake_data_factories/fill_db.py

fill-companies:
	poetry run python fake_data_factories/company_factories.py

fill-company-users:
	poetry run python fake_data_factories/company_user_factories.py

fill-tabit-admin-users:
	poetry run python fake_data_factories/tabit_user_factories.py

fill-company-departments:
	poetry run python fake_data_factories/department_factories.py

fill-license-type:
	poetry run python fake_data_factories/license_type_factories.py

# Команды для полного запуска в Docker
up-dc:
	docker-compose -f infra/local/docker-compose.local.yaml up -d --build

down-dc:
	docker-compose -f infra/local/docker-compose.local.yaml down

logs-dc:
	docker-compose -f infra/local/docker-compose.local.yaml logs -f

# Команда для выполнения миграций Alembic в контейнере
migrate-dc:
	docker-compose -f infra/local/docker-compose.local.yaml exec app poetry run alembic upgrade head
