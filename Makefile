# Определение всех целей, которые могут быть вызваны через make
.PHONY: help \
	up down logs up-pgadmin up-dc clean-volumes \
	migration-init migration-auto migration-empty migration-apply \
	db-reset db-init create-superuser fill-db fill-companies fill-company-users \
	fill-tabit-admin-users fill-company-departments  fill-license-type \
	run up-dc migrate-dc

# Определение переменной с именем файла окружения
ENV_FILE = .env

# Подключение переменных окружения из указанного файла
include $(ENV_FILE)

# Установка порта приложения по умолчанию, если он не задан
ifndef APP_PORT
	APP_PORT = 8000
endif

# Фикс для Windows окружений, где переменная PWD не определена. Расчитываем путь до корня проекта от infra/local
ifndef PWD
	export PWD=../..
endif

# Определение базовой команды для работы с Docker Compose
# Используется локальный конфиг и файл окружения
DOCKER_COMPOSE = docker compose -f infra/local/docker-compose.local.yaml --env-file $(ENV_FILE)

# Помощь и общее

help: ## Показать меню помощи
	@echo "Использование: make [цель]"
	@echo ""
	@echo "Доступные цели:"
	@awk 'BEGIN {FS = ":.*?## "}; /^[a-zA-Z_-]+:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort


# Минимальный набор для работы: БД в Docker-контейнере

up: ## Запуск контейнероа с локальной БД в фоновом режиме
	@echo "Запуск локальной БД в Docker..."
	$(DOCKER_COMPOSE) up -d

up-pgadmin: ## Запуск контейнеров с локальной БД и pgAdmin в фоновом режиме
	@echo "Запуск pgAdmin..."
	$(DOCKER_COMPOSE) --profile pgadmin up -d

down: ## Остановка всех контейнеров Docker
	@echo "Остановка всех контейнеров Docker..."
	$(DOCKER_COMPOSE) --profile "*" down

clean-volumes: ## Остановка всех контейнеров и удаление томов
	@echo "Остановка контейнеров и очистка БД и других вольюмов..."
	$(DOCKER_COMPOSE) --profile "*" down -v

logs: ## Показать логи всех контейнеров
	@echo "Отображение логов контейнеров (Ctrl+C для выхода)..."
	$(DOCKER_COMPOSE) logs -f

#Работа с миграциями

## Создание первичной миграции (если все миграции были удалены)
migration-init:
	@echo "Создание первичной миграции..."
	poetry run alembic revision --autogenerate -m "initial migration"

## Команда создания автогенерируемой миграции с возможностью передачи коммита
## через флаг m='...' для составления названия миграции
## Пример: make migration-auto m="сообщение"
migration-auto:
	@echo "Создание автоматической миграции с сообщением $(m)..."
	poetry run alembic revision --autogenerate -m "$(m)"

## Команда создания пустой миграции с возможностью передачи коммита
## через флаг m='...' для составления названия миграции
## Пример: make empty-migration m="сообщение"
migration-empty:
	@echo "Создание автоматической миграции с сообщением $(m)..."
	poetry run alembic revision -m "$(m)"

## Команда для применения миграций
migration-apply:
	@echo "Применяем миграцю..."
	poetry run alembic upgrade head

## Полный сброс базы данных и реинициализация
db-reset: clean-volumes up apply-migration

## Полный процесс инициализации базы данных
db-init: up init-migration apply-migration

# Заполнение БД данными

create-superuser: ## Создаст в базе данных суперпользователя.
	@echo "Создание суперпользователя..."
	python src/main.py -c

fill-db: ## Заполнение базы данных всеми тестовыми данными
	poetry run python fake_data_factories/fill_db.py

fill-companies: ## Заполнение базы данных данными компаний
	poetry run python fake_data_factories/company_factories.py

fill-company-users: ## Заполнение базы данных пользователями компаний
	poetry run python fake_data_factories/company_user_factories.py

fill-tabit-admin-users: ## Заполнение базы данных администраторами
	poetry run python fake_data_factories/tabit_user_factories.py

fill-company-departments: ## Заполнение базы данных данными отделов
	poetry run python fake_data_factories/department_factories.py

fill-license-type: ## Заполнение базы данных типами лицензий
	poetry run python fake_data_factories/license_type_factories.py


# Запуск приложения с uvicorn вне контейнера

run: ## Запуск всех контейнеров, включая приложение в Docker
	@echo "Запускаем приложение локально..."
	poetry run uvicorn src.main:app_v1 --port $(APP_PORT) --reload

# Docker с запуском приложения в контейнере

up-dc: ## Запуск всех контейнеров, включая приложение в Docker
	@echo "Запуск всех контейнеров, включая приложение..."
	$(DOCKER_COMPOSE) --profile app_dc --profile pgadmin up -d --build

# Команда для выполнения миграций Alembic в контейнере
migrate-dc:
	@echo "Применяем миграции через контейнер придожения.."
	$(DOCKER_COMPOSE) exec app poetry run alembic upgrade head
