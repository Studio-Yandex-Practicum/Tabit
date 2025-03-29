# Tabit

## Оглавление

1. [📌 О проекте](#о-проекте)
2. [🚀 Начало работы](#начало-работы)
   - [📦 Poetry](#poetry)
   - [🔄 Pre-commit](#pre-commit)
   - [🪟 Установка на Windows](#установка-на-windows)
3. [💾 Работа с базой данных](#работа-с-базой-данных)
   - [📊 ERD модель данных](#erd-модель-данных)
   - [🔍 DBeaver](#dbeaver)
   - [🔍 pgAdmin](#pgadmin)
4. [👨‍💻 Разработка](#разработка)
   - [🔄 Правила работы с git](#правила-работы-с-git)
   - [📝 Логирование](#логирование)
   - [🧹 Линтеры](#линтеры)
5. [🔄 CI/CD и деплой](#cicd-и-деплой)
   - [⚙️ GitHub Actions Workflows](#github-actions-workflows)
   - [🐳 Инфраструктура Docker](#инфраструктура-docker)
   - [🚀 Деплой на Stage](#деплой-на-stage)
6. [▶️ Запуск приложения](#запуск-приложения)
   - [💻 Из командной строки](#запуск-приложения-из-командной-строки)
   - [👤 Создание суперпользователя](#создать-автоматически-суперпользователя)
   - [🐞 Отладка CI/CD](#запуск-контейнеров-локально-для-отладки-cicd)
7. [📋 Справочник команд Makefile](#makefile-команды)
8. [🧪 Тестирование](#тестирование)
9. [❓ Часто встречающиеся ошибки](#часто-встречающиеся-ошибки)

## 📌 О проекте

**Tabit** — онлайн-сервис для HR-специалистов и собственников компаний, который помогает:
- 📊 Измерять эмоциональный климат в компании
- 🔍 Выявлять выгорающих сотрудников
- 💡 Обнаруживать внутренние проблемы компании
- 📈 Отслеживать ключевые показатели (текучесть кадров, уровень конфликтности и доверия)

> **Требования к окружению:** Python 3.12 или выше.

## 🚀 Начало работы

### 📦 Poetry

Poetry — это инструмент для управления зависимостями и виртуальными окружениями Python. В проекте Poetry является **обязательным** для разработки.

<details>
<summary><strong>🔽 Установка Poetry</strong></summary>

#### Установка Poetry

Следуйте [официальной инструкции](https://python-poetry.org/docs/#installation) или используйте один из способов:

**Через pip:**
```bash
pip install poetry==1.7.1  # Последняя стабильная версия 1.x
```

**Для UNIX-систем и WSL:**
```bash
curl -sSL https://install.python-poetry.org | python - --version 1.7.1
```

**Для Windows PowerShell:**
```pwsh
(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python - --version 1.7.1
```

> ⚠️ **Примечание:** Рекомендуется использовать версию 1.x, так как версия 2.x может иметь отличия в командах и работе.

#### Проверка установки

```bash
poetry --version
```

> ⚠️ **Примечание:** Если poetry не найден, добавьте путь установки в переменную PATH вашей системы.

#### Настройка Poetry для проекта

1. Настройте создание виртуального окружения в папке проекта:
   ```bash
   poetry config virtualenvs.in-project true
   ```

2. Установите зависимости проекта:
   ```bash
   poetry install
   ```

</details>

<details>
<summary><strong>🔽 Работа с Poetry</strong></summary>

#### Активация виртуального окружения

**В Poetry 1.x:**
```bash
poetry shell
```

**В Poetry 2.x:**
В версии 2.0.0 и выше команда `poetry shell` не доступна по умолчанию. Используйте один из следующих методов:

```bash
# Рекомендуемый способ: активация окружения
poetry env activate

# Альтернатива: установка плагина shell
poetry self add poetry-plugin-shell
poetry shell

# Или напрямую активируйте окружение
source .venv/bin/activate    # Linux/macOS
.venv\Scripts\activate.bat   # Windows cmd
.venv\Scripts\Activate.ps1   # Windows PowerShell
```

> 📘 Подробнее в документации: [Poetry: Activating the environment](https://python-poetry.org/docs/managing-environments/#activating-the-environment)

#### Запуск команд в виртуальном окружении
```bash
poetry run <команда>
```

Примеры:
```bash
poetry run python src/main.py
poetry run pytest
poetry run ruff format
```

#### Управление зависимостями

**Добавление основной зависимости:**
```bash
poetry add <имя_пакета>
```

**Добавление зависимости для разработки:**
```bash
poetry add <имя_пакета> --dev
```

**Обновление зависимостей:**
```bash
poetry update
```

</details>

### 🔄 Pre-commit

<details>
<summary><strong>🔽 Настройка pre-commit</strong></summary>

1. Проверьте, что pre-commit установлен:
   ```bash
   pre-commit --version
   ```

2. Настройте git hook:
   ```bash
   pre-commit install
   ```

После настройки при каждом коммите будет автоматически запускаться проверка линтером и форматирование кода.

</details>

### 🪟 Установка на Windows

<details>
<summary><strong>🔽 Способ 1: Установка с использованием WSL (рекомендуется)</strong></summary>

#### 1. Установка WSL
1. Откройте PowerShell от имени администратора и выполните:
   ```powershell
   wsl --install
   ```

2. Перезагрузите компьютер и завершите настройку Ubuntu.

3. Подробная инструкция доступна по ссылке: [Установка и настройка WSL](https://code.s3.yandex.net/backend-developer/learning-materials/Инструкция_по_установке_и_настройке_WSL.pdf)

#### 2. Установка необходимого ПО
1. Установите Docker Desktop:
   ```
   # Скачайте и установите с официального сайта:
   https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe
   ```

2. Установите VS Code с расширением Remote - WSL.

3. Установите Make в WSL:
   ```bash
   sudo apt update
   sudo apt install make
   ```

4. Установите Poetry в WSL:
   ```bash
   curl -sSL https://install.python-poetry.org | python3 - --version 1.7.1
   ```

   **Альтернативные способы установки Poetry:**

   **Через pip:**
   ```bash
   pip install poetry==1.7.1
   ```

   **Через apt (если pip недоступен):**
   ```bash
   sudo apt update
   sudo apt install python3-pip
   pip install poetry==1.7.1
   ```

   **Проверка установки:**
   ```bash
   poetry --version
   ```

   **Настройка Poetry:**
   ```bash
   poetry config virtualenvs.in-project true
   ```

#### 3. Клонирование и настройка проекта
1. Клонируйте репозиторий:
   ```bash
   git clone git@github.com:Studio-Yandex-Practicum/Tabit.git
   cd Tabit
   ```

2. Настройте Poetry:
   ```bash
   poetry config virtualenvs.in-project true
   poetry install
   ```

#### 4. Запуск проекта
1. Активируйте виртуальное окружение:
   ```bash
   source .venv/bin/activate
   # или
   poetry shell
   ```

2. Запустите приложение:
   ```bash
   make up                 # Запуск контейнера с БД

   # Если миграции уже существуют:
   make migration-apply    # Применение существующих миграций

   # Если это первая инициализация:
   make db-init            # Создание и применение начальных миграций

   make create-superuser   # Создание суперпользователя
   make fill-db            # Заполнение тестовыми данными
   make run                # Запуск приложения
   ```
</details>

<details>
<summary><strong>🔽 Способ 2: Установка на чистом Windows</strong></summary>

#### 1. Установка необходимого ПО
1. Установите Chocolatey (менеджер пакетов для Windows):
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force
   [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
   iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
   ```

2. Установите Make:
   ```powershell
   choco install make
   ```

3. Установите Docker Desktop:
   ```
   # Скачайте и установите с официального сайта:
   https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe
   ```

4. Установите Python:
   ```
   # Скачайте и установите с официального сайта:
   https://www.python.org/downloads/
   ```

5. Установите Poetry:
   Выберите один из способов:

   **Через pip:**
   ```powershell
   pip install poetry==1.7.1
   ```

   **Через PowerShell:**
   ```powershell
   (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python - --version 1.7.1
   ```

   **Проверка установки:**
   ```bash
   poetry --version
   ```

   **Настройка Poetry:**
   ```bash
   poetry config virtualenvs.in-project true
   ```

#### 2. Клонирование и настройка проекта
1. Клонируйте репозиторий:
   ```powershell
   git clone git@github.com:Studio-Yandex-Practicum/Tabit.git
   cd Tabit
   ```

2. Настройте Poetry:
   ```powershell
   poetry config virtualenvs.in-project true
   poetry install
   ```

#### 3. Запуск проекта
1. Активируйте виртуальное окружение:
   ```powershell
   .venv\Scripts\activate.bat   # для cmd
   .venv\Scripts\Activate.ps1   # для PowerShell
   ```

2. Запустите приложение:
   ```powershell
   make up                 # Запуск контейнера с БД

   # Если миграции уже существуют:
   make migration-apply    # Применение существующих миграций

   # Если это первая инициализация:
   make db-init            # Создание и применение начальных миграций

   make create-superuser   # Создание суперпользователя
   make fill-db            # Заполнение тестовыми данными
   make run                # Запуск приложения
   ```

> ⚠️ **Примечание:** На чистом Windows могут возникнуть проблемы совместимости. Если столкнетесь с ошибками, рекомендуется перейти на WSL.
</details>

## 💾 Работа с базой данных

### Настройка окружения

Для работы с базой данных создайте файл `.env` в корне проекта на уровне с директорией `src`.

> **Пример всех необходимых параметров можно найти в файле `.env.example`.**

#### Пример содержимого `.env`:
```ini
# Настройки БД
POSTGRES_USER=warlock                     # Имя пользователя БД
POSTGRES_PASSWORD=zTudS8LBSquBMwvS3ky5    # Пароль к БД
POSTGRES_DB=tabit                         # Название БД
DB_PORT=5432                              # Порт для подключения к БД
DB_TYPE=postgresql                        # Тип базы данных
DB_API=asyncpg                            # API для работы с БД
DB_HOST=localhost                         # Хост для подключения к БД
```

### 📊 ERD модель данных
Актуальная ER-диаграмма базы данных доступна [по ссылке](https://app.erdlab.io/designer/schema/1736745715-tabit)

### 🔍 DBeaver

<details>
<summary><strong>🔽 Подключение к БД через DBeaver</strong></summary>

1. Скачайте и установите [DBeaver](https://dbeaver.io/)
2. Создайте новое подключение (`Ctrl+Shift+N`)
3. Выберите PostgreSQL
4. Введите параметры подключения:
   - **Хост**: localhost
   - **Порт**: 5433 (или порт, указанный в `.env`)
   - **База данных**: tabit (или имя, указанное в `.env`)
   - **Пользователь**: warlock (или имя, указанное в `.env`)
   - **Пароль**: (указанный в `.env`)
5. Нажмите "Тест соединения", затем "Готово"

</details>

### 🔍 pgAdmin

<details>
<summary><strong>🔽 Работа с pgAdmin</strong></summary>

pgAdmin — веб-интерфейс для управления PostgreSQL. В проекте доступен через контейнер Docker по адресу http://localhost:5600/

#### Настройка pgAdmin

1. Добавьте в `.env` файл переменные:
   ```ini
   PGADMIN_DEFAULT_EMAIL=admin@email.com
   PGADMIN_DEFAULT_PASSWORD=admin
   ```

2. Запустите контейнер с pgAdmin:
   ```bash
   make up-pgadmin
   ```
   или
   ```bash
   docker compose -f infra/local/docker-compose.local.yaml --profile pgadmin up -d
   ```

3. Откройте в браузере http://localhost:5600/

> ⚠️ **Важно:** Инициализация pgAdmin может занять до 8 минут (особенно на HDD).

#### Управление pgAdmin

**Остановка контейнеров:**
```bash
make down-pgadmin
```
или
   ```bash
   docker compose -f infra/local/docker-compose.local.yaml --profile '*' down
   ```

**Удаление контейнеров и томов:**
```bash
make down-pgadmin-volumes
```
или
```bash
docker compose -f infra/local/docker-compose.local.yaml --profile '*' down -v
```

#### Дополнительные сведения о pgAdmin

Инструмент для взаимодействия с БД PostgreSQL, альтернатива DBeaver. Вариация в данном проекте работает через Docker-контейнер и доступна в браузере по ссылке http://localhost:5600/ или http://127.0.0.1:5600/.
Полная документация доступна по ссылке: https://www.pgadmin.org/docs/pgadmin4/8.14/index.html

В контейнер монтируются:
- `servers.json` - файл с данными для подключения к БД;
- `config_local.py` - настройки для pgAdmin. Заменяют параметры, описанные в `config.py` внутри контейнера (подробнее: https://www.pgadmin.org/docs/pgadmin4/latest/config_py.html#config-py);
- `.pgpass` - файл-пароль для подключения к БД;
- `create-admin-folder.sh` - bash-скрипт для создания внутри контейнера необходимой папки и переноса туда `.pgpass`.

#### Подготовка к запуску
Достаточно в файл с переменными окружения .env добавить две переменных: `PGADMIN_DEFAULT_EMAIL` и `PGADMIN_DEFAULT_PASSWORD`, почта и пароль автоматически создаваемого админа соответственно (см. `.env.example`).

#### Особенности работы с pgAdmin
- Полная инициализация pgAdmin может занимать много времени. На ноутбуке с HDD процесс занимал 8 минут. С SSD должно быть быстрее.
- В процессе инициализации для первого админа создаётся автоматическое подключение к БД, данные для подключения описаны в файле `servers.json`. Благодаря файлу `.pgpass` пропадает необходимость вводить пароль для подключения.
- Первый админ может создавать других пользователей с помощью User Management (меню в правом верхнем углу). Однако для таких пользователей подключение к БД нужно настраивать отдельно уже в интерфейсе системы.

</details>

## 👨‍💻 Разработка

### 🔄 Правила работы с git

<details>
<summary><strong>🔽 Git-процесс в проекте</strong></summary>

#### Основные ветки
- `master` — production-ready код, используется для CI/CD
- `dev` — предрелизная ветка с рабочим и выверенным кодом

#### Создание новых веток
- Новые ветки всегда создаются от ветки `dev`
- Названия веток:
  - `feature/название-функционала` — для нового функционала
  - `bugfix/название-багфикса` — для исправления ошибок

#### Процесс работы
1. Создайте новую ветку от `dev`
2. Внесите необходимые изменения
3. Отправьте ветку в репозиторий
4. Откройте Pull Request в ветку `dev`
5. Добавьте ссылку на PR в соответствующую задачу в Kaiten

</details>

### 📝 Логирование

<details>
<summary><strong>🔽 Система логирования</strong></summary>

В проекте доступны два типа логирования:
- Автоматическое логирование запросов через middleware
- Ручное логирование через функцию `logger`

#### Использование логирования

1. Импортируйте логгер:
   ```python
   from src.logger import logger
   ```

2. Добавьте логи нужного уровня:
   ```python
   logger.trace('Трассировочное сообщение')
   logger.debug('Отладочное сообщение')
   logger.info('Информационное сообщение')
   logger.success('Сообщение об успехе')
   logger.warning('Предупреждение')
   logger.error('Сообщение об ошибке')
   logger.critical('Критическая ошибка')
   ```

#### Настройка уровня логирования

Уровень логирования задается в `.env` переменной `LOG_LEVEL`. Доступные уровни:
- TRACE
- DEBUG
- INFO
- SUCCESS
- WARNING
- ERROR
- CRITICAL

</details>

### 🧹 Линтеры

<details>
<summary><strong>🔽 Проверка качества кода</strong></summary>

В проекте используется [Ruff](https://github.com/astral-sh/ruff) для форматирования и проверки кода.

#### Основные настройки

- **Максимальная длина строки:** 99 символов
- **Исключены из проверки:** директории "alembic"
- **Проверки:** "E" (ошибки), "F" (предупреждения), "I" (импорты)
- **Стиль строк:** одинарные кавычки
- **Импорты:** с учетом внутренних модулей `src`

#### Запуск проверки

```bash
poetry run ruff check .
```

#### Автоматическое форматирование

```bash
poetry run ruff format .
```

</details>

## 🔄 CI/CD и деплой

### ⚙️ GitHub Actions Workflows

В проекте настроены следующие автоматизированные процессы:

| Workflow                 | Описание                              | Триггер                     |
|--------------------------|---------------------------------------|-----------------------------|
| **build_and_push.yaml**  | Сборка и публикация образа Docker     | При необходимости           |
| **pytest.yaml**          | Запуск тестов                         | Push в репозиторий          |
| **ruff.yml**             | Проверка кода линтерами               | Push, Pull Request          |
| **stage_deploy.yaml**    | Деплой на Stage-окружение             | Push в определенную ветку   |

### 🐳 Инфраструктура Docker

<details>
<summary><strong>🔽 Конфигурации Docker</strong></summary>

#### Локальное окружение

1. **Только база данных**
   ```bash
   make up              # Запуск
   ```

2. **База данных с pgAdmin**
   ```bash
   make up-pgadmin      # Запуск
   ```

3. **Полное окружение**
   ```bash
   make up-dc           # Запуск
   ```

4. **Общие команды**
   ```bash
   make logs            # Просмотр логов
   make down            # Остановка
   make clean-volumes   # Остановка и полный сброс данных
   ```

#### Stage окружение

Конфигурация для Stage расположена в директории `infra/stage`:
- `docker-compose.stage.yaml` — конфигурация Docker Compose
- `stage.Dockerfile` — Dockerfile для сборки образа
- `tabit.service` — Systemd-сервис для запуска на сервере

</details>

### 🚀 Деплой на Stage

<details>
<summary><strong>🔽 Процесс деплоя</strong></summary>

Деплой на Stage-окружение выполняется через GitHub Action workflow `stage_deploy.yaml`:

1. Сборка Docker-образа
2. Публикация образа в GitHub Container Registry
3. Подключение к stage-серверу по SSH
4. Загрузка конфигурационных файлов
5. Запуск/перезапуск приложения через Systemd

#### Настройка секретов

Для работы деплоя необходимы следующие секреты в репозитории GitHub:
- `STAGE_HOST` — хост stage-сервера
- `STAGE_SSH_KEY` — приватный SSH-ключ
- `STAGE_SSH_USER` — пользователь для SSH
- `STAGE_SSH_PASSWORD` — пароль для SSH (если используется)

</details>

## ▶️ Запуск приложения

### 💻 Запуск приложения из командной строки

```bash
python src/main.py [опции]
```

#### Поддерживаемые опции:
- `--reload` или `-r` — отслеживание изменений в коде
- `--host` или `-h` — указание хоста (по умолчанию 127.0.0.1)
- `--port` или `-p` — указание порта (по умолчанию 8000)
- `--create-superuser` или `-c` — создание суперпользователя

#### Пример:
```bash
python src/main.py -r -h 127.0.0.1 -p 1234
```

### 👤 Создать автоматически суперпользователя

1. Заполните `.env` параметрами (примеры из .env.example):
```ini
FIRST_SUPERUSER_EMAIL=yandex@yandex.ru    # Почта
FIRST_SUPERUSER_PASSWORD=Password123      # Пароль (Латинские символов в обоих регистрах, числа, минимальная длина 8 символов)
FIRST_SUPERUSER_NAME=Ип                   # Имя
FIRST_SUPERUSER_SURNAME=Ман               # Фамилия
```

2. Запустите:
```bash
python src/main.py -c
```
или
```bash
make create-superuser
```

### 🐞 Запуск контейнеров локально для отладки CI/CD

<details>
<summary><strong>🔽 Локальное тестирование CI/CD</strong></summary>

#### 1. Настройка окружения
Создайте файл `.env` в корне проекта с необходимыми переменными (см. `.env.example`)

#### 2. Запуск контейнеров
```bash
make up-dc
```

#### 3. Проверка логов
```bash
make logs
```

#### 4. Применение миграций
```bash
make migration-apply-dc
```

#### 5. Остановка контейнеров
```bash
make down
```

#### Особенности отладки CI/CD
- Корректно завершает работу всех сервисов.
- Очищает используемые контейнеры, но сохраняет данные в volume-ах.

После этих шагов можно быть уверенным, что CI/CD собирает проект корректно.

</details>

## 📋 Makefile команды

<details>
<summary><strong>🔽 Docker Compose команды</strong></summary>

| Команда                          | Описание                                     |
|----------------------------------|----------------------------------------------|
| `make up`                        | Запуск контейнера с БД                       |
| `make up-pgadmin`                | Запуск контейнеров с БД и pgAdmin            |
| `make up-dc`                     | Запуск полного окружения в контейнерах       |
| `make logs`                      | Вывод логов всех контейнеров                 |
| `make down`                      | Остановка и удаление контейнеров             |
| `make clean-volumes`             | Остановка контейнеров и удаление томов       |

</details>

<details>
<summary><strong>🔽 Миграции и база данных</strong></summary>

| Команда                          | Описание                                     |
|----------------------------------|----------------------------------------------|
| `make migration-init`            | Создание первичной миграции с автогенерацией |
| `make migration-auto m='commit'` | Создание миграции с указанным именем         |
| `make migration-empty m='commit'`| Создание пустой миграции                     |
| `make migration-apply`           | Применение всех миграций                     |
| `make migration-apply-dc`        | Выполнение миграций в контейнере             |
| `make migration-rollback`        | Откат последней миграции                     |
| `make db-reset`                  | Сброс базы и применение миграций             |
| `make db-init`                   | Запуск контейнеров и создание структуры БД   |

</details>

<details>
<summary><strong>🔽 Запуск и тестовые данные</strong></summary>

| Команда                          | Описание                                     |
|----------------------------------|----------------------------------------------|
| `make run`                       | Запуск приложения с Uvicorn на порту 8000    |
| `make create-superuser`          | Создание суперпользователя                   |
| `make fill-db`                   | Заполнение БД всеми тестовыми данными        |
| `make fill-companies`            | Создание тестовых компаний                   |
| `make fill-company-users`        | Создание тестовых пользователей компаний     |
| `make fill-tabit-admin-users`    | Создание тестовых администраторов            |
| `make fill-company-departments`  | Создание тестовых отделов                    |
| `make fill-license-type`         | Создание тестовых типов лицензий             |
| `make fill-problems`             | Создание тестовых проблем                    |
| `make fill-message-feeds`        | Создание тестовых лент сообщений             |
| `make fill-voting-feeds`         | Создание тестовых вариантов голосования      |
| `make fill-tasks`                | Создание тестовых задач                      |

</details>

## 🧪 Тестирование

Тесты используют базу данных PostgreSQL, которая **автоматически** разворачивается в контейнере перед запуском тестов и удаляется после их выполнения. **Не нужно запускать контейнер вручную — `pytest` сделает это сам!**

<details>
<summary><strong>🔽 Как запустить тесты?</strong></summary>

1. **Добавьте переменные тестовой базы данных в `.env` (если их нет)**:
   ```ini
   TEST_POSTGRES_USER=test_user
   TEST_POSTGRES_PASSWORD=test_password
   TEST_POSTGRES_HOST=localhost
   TEST_POSTGRES_PORT=5433
   TEST_POSTGRES_DB=test_db
   ```
   📌 Эти переменные используются для автоматического подключения к тестовой БД в контейнере.

2. Убедитесь, что у вас установлен `pytest`:
   ```bash
   poetry add pytest --dev
   ```
3. Запустите тесты:
   ```bash
   pytest -v
   ```
4. Если хотите **остановить тестирование при первой ошибке**, используйте флаг `-x`:
   ```bash
   pytest -x -v
   ```
   Это ускоряет отладку, останавливая тесты сразу при первой неудаче.
5. **Запуск только последних упавших тестов (`--lf`)**:
   ```bash
   pytest --lf -v
   ```
   📌 Эта команда запустит **только тесты, которые упали в последнем запуске**.
6. **Запуск тестов в том же порядке, начиная с упавших (`--ff`)**:
   ```bash
   pytest --ff -v
   ```
   📌 Эта команда запустит тесты **в том же порядке, что и в предыдущем запуске**, начиная с упавших.

</details>

<details>
<summary><strong>🔽 Что делать, если контейнер завис?</strong></summary>

Если тесты не запускаются из-за проблем с контейнером, удалите его вручную:
```bash
docker-compose -f infra/docker-compose.test-db.yaml down -v
```
Эта команда **остановит и полностью удалит контейнер с тестовой базой, включая все его данные**. После этого можно запустить тесты заново.

</details>

<details>
<summary><strong>🔽 Как работают тесты?</strong></summary>

1. **Перед запуском тестов `pytest` сам поднимает контейнер с PostgreSQL**:
   - Контейнер создаёт отдельную тестовую БД, чтобы не затронуть основную.
   - После поднятия контейнера происходит ожидание готовности БД.

2. **При запуске тестов `pytest` загружает переменные окружения из `pytest.ini`**, включая параметры подключения к тестовой БД.

3. **После завершения тестов контейнер с БД автоматически удаляется**.

📌 **Важно**: тестовая БД создаётся в отдельном контейнере и не влияет на основную базу данных.
Теперь тесты полностью автоматизированы и изолированы! 🚀

</details>

## ❓ Часто встречающиеся ошибки

<details>
<summary><strong>🔽 Конфликт портов PostgreSQL в WSL и Docker</strong></summary>

При использовании PostgreSQL одновременно в WSL и Docker-контейнерах может возникнуть конфликт портов, если оба сервиса пытаются использовать порт 5432 (по умолчанию для PostgreSQL).

#### Симптомы:
- Ошибка при запуске контейнера: `Bind for 0.0.0.0:5432 failed: port is already allocated`
- Невозможно подключиться к базе данных
- Невозможно применить миграции в контейнере с БД
- Сервис PostgreSQL в WSL или Docker не запускается

#### Решение:

1. **Проверка занятых портов:**
   ```bash
   sudo netstat -tuln | grep 5432
   ```

2. **Вариант 1: Остановить PostgreSQL в WSL**
   Если PostgreSQL в WSL не нужен, остановите его:
   ```bash
   sudo service postgresql stop
   ```

3. **Вариант 2: Изменить порт в Docker**
   Если нужно использовать оба сервиса, измените порт для Docker-контейнера:
   - В файле `.env` измените значение `DB_PORT` на свободный порт (например, 5433)
   - Перезапустите контейнеры

4. **Вариант 3: Изменить порт в WSL**
   Если нужно использовать PostgreSQL в WSL, измените его порт:
   - Откройте конфигурационный файл PostgreSQL:
     ```bash
     sudo nano /etc/postgresql/<версия>/main/postgresql.conf
     ```
   - Найдите строку `port = 5432` и измените на свободный порт
   - Перезапустите PostgreSQL:
     ```bash
     sudo service postgresql restart
     ```

#### Профилактика:
- Всегда проверяйте занятые порты перед запуском контейнеров
- Используйте разные порты для WSL и Docker, если оба сервиса нужны одновременно
- Убедитесь, что в `.env` указан правильный порт для подключения к базе данных

</details>

<details>
<summary><strong>🔽 Конфликт имён контейнеров Docker</strong></summary>

При обновлени репозитория или работе с несколькими его копиями может возникнуть пересечение имён контейнеров при запуске

#### Симптомы:
Сообщение в консоли:

```bash
Error response from daemon: Conflict. The container name "/postgres_local" is already in use by container...
```

#### Решение:
1. **Прорерить запущенные контейнеры**

```bash
docker ps
```

2. **Если обнаружены лишние контейнеры - остановить и удалить их вручную**
Пример:
```bash
docker stop postgres_local
docker remove  postgres_local
```

3.  **Если обнаруженные контейнеры нужны - изменить название контейнеров в текущем локальном запуске чепез .env**
Пример:
```ini
APP_CONTAINER_NAME=tabit_new
DB_CONTAINER_NAME=postgres_new
PGADMIN_CONTAINER_NAME=pgadmin_new
```

4. **Предпринять новую попытку запуска**

</details>
