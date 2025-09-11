# Определение всех целей, которые могут быть вызваны через make
.PHONY: help up up-dc up-pgadmin down clean-volumes logs run migration-init migration-auto \
migration-empty migration-apply migration-apply-dc migration-rollback db-reset db-init \
create-superuser fill-db fill-companies fill-company-users fill-tabit-admin-users \
fill-company-departments fill-license-type fill-problems fill-message-feeds \
fill-voting-feeds fill-voting-by-user fill-tasks fill-tags fill-comments fill-meetings \
fill-meetings-results

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
TEST_DOCKER_COMPOSE = docker compose -f infra/docker-compose.test-db.yaml --env-file $(ENV_FILE)

# Основные команды
help: ## Показать меню помощи
	@echo "Использование: make [цель]"
	@echo ""
	@echo "Основные категории команд:"
	@echo ""
	@echo "\033[1mУправление Docker контейнерами:\033[0m"
	@awk 'BEGIN {FS = ":.*?## "}; /^(up|up-dc|up-pgadmin|down|clean-volumes|logs):.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort
	@echo ""
	@echo "\033[1mЛокальный запуск приложения:\033[0m"
	@awk 'BEGIN {FS = ":.*?## "}; /^run:.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort
	@echo ""
	@echo "\033[1mУправление миграциями:\033[0m"
	@awk 'BEGIN {FS = ":.*?## "}; /^migration-.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort
	@echo ""
	@echo "\033[1mУправление базой данных:\033[0m"
	@awk 'BEGIN {FS = ":.*?## "}; /^(db-reset|db-init):.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort
	@echo ""
	@echo "\033[1mГенерация тестовых данных:\033[0m"
	@awk 'BEGIN {FS = ":.*?## "}; /^(create-superuser|fill-.*):.*?## / {printf "\033[36m%-30s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST) | sort

# Управление Docker контейнерами

# Запуск контейнеров
up: ## Запуск контейнера с локальной БД в фоновом режиме
	@echo "Запуск локальной БД в Docker..."
	$(DOCKER_COMPOSE) up -d

up-dc: ## Запуск всех контейнеров, включая приложение в Docker
	@echo "Запуск всех контейнеров, включая приложение..."
	$(DOCKER_COMPOSE) --profile app_up up -d --build

up-pgadmin: ## Запуск контейнеров с локальной БД и pgAdmin в фоновом режиме
	@echo "Запуск pgAdmin..."
	$(DOCKER_COMPOSE) --profile pgadmin up -d

# Остановка и очистка контейнеров
down: ## Остановка всех контейнеров Docker
	@echo "Остановка всех контейнеров Docker..."
	$(DOCKER_COMPOSE) --profile "*" down
	$(TEST_DOCKER_COMPOSE) down

clean-volumes: ## Остановка всех контейнеров и удаление томов
	@echo "Остановка контейнеров и очистка БД и других вольюмов..."
	$(DOCKER_COMPOSE) --profile "*" down -v
	$(TEST_DOCKER_COMPOSE) down -v

# Мониторинг контейнеров
logs: ## Показать логи всех контейнеров
	@echo "Отображение логов контейнеров (Ctrl+C для выхода)..."
	$(DOCKER_COMPOSE) logs -f

# Локальный запуск приложения
run: ## Запуск приложения локально
	@echo "Запускаем приложение локально..."
	poetry run uvicorn src.main:app_v${APP_VERSION} --port $(APP_PORT) --reload

# Управление миграциями

# Создание миграций
migration-init: ## Создание первичной миграции
	@echo "Создание первичной миграции..."
	poetry run alembic revision --autogenerate -m "initial migration"

migration-auto: ## Создание автогенерируемой миграции
	@echo "Создание автоматической миграции с сообщением $(m)..."
	poetry run alembic revision --autogenerate -m "$(m)"

migration-empty: ## Создание пустой миграции
	@echo "Создание пустой миграции с сообщением $(m)..."
	poetry run alembic revision -m "$(m)"

# Применение миграций
migration-apply: ## Применение миграций локально
	@echo "Применяем миграции..."
	poetry run alembic upgrade head

migration-apply-dc: ## Применение миграций через контейнер
	@echo "Применяем миграции через контейнер приложения..."
	$(DOCKER_COMPOSE) exec app /usr/local/bin/poetry run alembic upgrade head

# Откат миграций
migration-rollback: ## Откатить последнюю миграцию
	@echo "Откат последней миграции..."
	$(DOCKER_COMPOSE) exec app /usr/local/bin/poetry run alembic downgrade -1
	@echo "Миграция успешно откачена"

# Управление базой данных
db-reset: ## Полный сброс базы данных и реинициализация
	make clean-volumes up
	sleep 3
	make migration-apply

db-init: ## Полный процесс инициализации базы данных (работает только при отсутствии файлов миграций)
	make up
	sleep 3
	make migration-init migration-apply

# Генерация тестовых данных
create-superuser: ## Создание суперпользователя
	@echo "Создание суперпользователя..."
	python src/main.py -c

create-superuser-dc: ## Создание суперпользователя
	@echo "Создание суперпользователя..."
	$(DOCKER_COMPOSE) exec app /usr/local/bin/poetry run python src/main.py -c

fill-db: ## Заполнение базы данных всеми тестовыми данными
	poetry run python fake_data_factories/fill_db.py

fill-db-dc: ## Заполнение базы данных всеми тестовыми данными через контейнер
	$(DOCKER_COMPOSE) exec app /usr/local/bin/poetry run python fake_data_factories/fill_db.py

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

fill-problems: ## Заполнение базы данных тестовыми проблемами
	poetry run python fake_data_factories/problem_factory.py

fill-meetings: ## Заполнение базы данных тестовыми встречами
	poetry run python fake_data_factories/meeting_factory.py

fill-meetings-results: ## Заполнение базы данных результатами тестовых встреч
	poetry run python fake_data_factories/meeting_result_factory.py

fill-message-feeds: ## Заполнение базы данных тестовыми лентами сообщений
	poetry run python fake_data_factories/message_feed_factory.py

fill-voting-feeds: ## Заполнение базы данных тестовыми вариантами голосования
	poetry run python fake_data_factories/voting_feed_factory.py

fill-voting-by-user: ## Заполнение базы данных тестовыми выборами пользователя вариантов голосования
	poetry run python fake_data_factories/voting_by_user_factory.py

fill-tasks: ## Заполнение базы данных тестовыми задачами
	poetry run python fake_data_factories/task_factory.py

fill-tags: ## Заполнение базы данных тестовыми тэгами
	poetry run python fake_data_factories/tag_factories.py

fill-comments: ## Заполнение базы данных тестовыми комментариями
	poetry run python fake_data_factories/comment_feed_factory.py
