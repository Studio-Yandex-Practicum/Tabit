# Tabit
Онлайн сервис для HR и собственников компаний который помогает:
- измерять эмоциональный климат в компании;
- увидеть выгорающих сотрудников;
- узнать о внутренних проблемах компании;
- отслеживать основные показатели компании (текучесть кадров, уровень конфликтности и доверия в коллективе и др.);


## Правила работы с git (как делать коммиты и pull request-ы)<a id="git"></a>:



1. Две основные ветки: `master` и `dev`

2. Ветка `dev` — “предрелизная”. Т.е. здесь должен быть рабочий и выверенный код

3. Создавая новую ветку, наследуйтесь от ветки `dev`

4. В `master` находится только production-ready код (CI/CD)

5. Правила именования веток

- весь новый функционал — `feature/название-функционала`

- исправление ошибок — `bugfix/название-багфикса`

6. Пушим свою ветку в репозиторий и открываем Pull Request

7. ВАЖНО! К таске из Kaiten оставляем ссылку на свой Pull Request



## Poetry (инструмент для работы с виртуальным окружением и сборки пакетов)<a id="poetry"></a>:




Poetry - это инструмент для управления зависимостями и виртуальными окружениями, также может использоваться для сборки пакетов. В этом проекте Poetry необходим для дальнейшей разработки приложения, его установка <b>обязательна</b>.<br>



<details>

<summary>

Как скачать и установить?

</summary>



### Установка:



Установите poetry, не ниже версии 1.5.0 следуя [инструкции с официального сайта](https://python-poetry.org/docs/#installation).

<details>

<summary>

Команды для установки:

</summary>



Если у Вас уже установлен менеджер пакетов pip, то можно установить командой:


```bash
>  *pip install poetry==1.5.0*
```



Если по каким-то причинам через pip не устанавливается,

то для UNIX-систем и Bash on Windows вводим в консоль следующую команду:



```bash
>  *curl -sSL https://install.python-poetry.org | python -*
```



Для WINDOWS PowerShell:



```pwsh
>  *(Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | python -*
```



</details>

<br>

После установки перезапустите оболочку и введите команду



```bash
> poetry --version
```



Если установка прошла успешно, вы получите ответ в формате



> Poetry (version 1.5.0)



P.S.: Если при попытке проверить версию возникает ошибка об отсутствии исполняемого файла

(poetry), необходимо после установки добавить его в Path Вашей системы

(пути указаны по ссылке на официальную инструкцию по установке чуть выше.)



Для дальнейшей работы введите команду:



```bash
> poetry config virtualenvs.in-project true
```



Выполнение данной команды необходимо для создания виртуального окружения в

папке проекта.



После предыдущей команды создаём виртуальное окружение нашего проекта с

помощью команды:



```bash
> poetry install
```



Результатом выполнения команды станет создание в корне проекта папки .venv.

Зависимости для создания окружения берутся из файлов poetry.lock (приоритетнее)

и pyproject.toml



Для добавления новой зависимости в окружение необходимо выполнить команду



```bash
> poetry add <package_name>
```



_Пример использования:_



```bash
> poetry add starlette
```



Также poetry позволяет разделять зависимости необходимые для разработки, от

основных.

Для добавления зависимости необходимой для разработки и тестирования необходимо

добавить флаг ***--dev***



```bash
> poetry add <package_name> --dev
```



_Пример использования:_



```bash
> poetry add pytest --dev
```



</details>



<details>

<summary>

Порядок работы после настройки

</summary>



<br>



Чтобы активировать виртуальное окружение, введите команду:



```bash
> poetry shell
```



Существует возможность запуска скриптов и команд с помощью команды без

активации окружения:



```bash
> poetry run <script_name>.py
```



_Примеры:_



```bash
> poetry run python script_name>.py

>

> poetry run pytest

>

> poetry run black
```



Порядок работы в оболочке не меняется. Пример команды для Win:



```bash
> python src\run_bot.py
```



Доступен стандартный метод работы с активацией окружения в терминале с помощью команд:



Для WINDOWS:



```pwsh
> source .venv/Scripts/activate
```



Для UNIX:



```bash
> source .venv/bin/activate
```



</details>



В этом разделе представлены наиболее часто используемые команды.

Подробнее: https://python-poetry.org/docs/cli/



#### Активировать виртуальное окружение

```bash

poetry  shell

```



#### Добавить зависимость

```bash

poetry  add <package_name>

```



#### Обновить зависимости

```bash

poetry  update

```

## 3.3. Pre-commit (инструмент автоматического запуска различных проверок перед выполнением коммита)<a id="pre-commit"></a>:



<details>

<summary>

Настройка pre-commit

</summary>

<br>

1. Убедиться, что pre-comit установлен:



```bash

pre-commit  --version

```

2. Настроить git hook скрипт:



```bash

pre-commit install

```



Далее при каждом коммите у вас будет происходить автоматическая проверка
линтером, а так же будет происходить автоматическое приведение к единому стилю.

</details>


# Makefile команды

Для разворачивания контейнера с БД на локальном компьютере нужно настроить файл `.env`. Он должен находиться в корне проекта на одном уровне с директорией `src`.

### 1. `make up`
Запускает контейнеры Docker в фоновом режиме с помощью Docker Compose. Используется для поднятия всех необходимых сервисов.

### 2. `make down`
Останавливает и удаляет контейнеры Docker, остановив все запущенные сервисы.

### 3. `make logs`
Выводит логи всех контейнеров Docker, чтобы наблюдать за их состоянием в реальном времени.

### 4. `make init-migrations`
Создает новую миграцию для базы данных с автогенерацией изменений с помощью Alembic.

### 5. `make auto-migration m='commit_text'`
Создает новую миграцию для базы данных с автогенерацией изменений с помощью Alembic. Имя файла миграции составляется из вычисляемого id и переданного commit, формат: id_commit_text.py

### 6. `make empty-migration m='commit_text'`
Создает пустую миграцию для базы данных с помощью Alembic. Имя файла миграции составляется из вычисляемого id и переданного commit, формат: id_commit_text.py

### 7. `make apply-migrations`
Применяет все миграции базы данных, чтобы привести её в актуальное состояние.

### 8. `make drop-db`
Удаляет базу данных PostgreSQL и создает её заново, используя команды psql в контейнере Docker.

### 9. `make reset-db`
Сбрасывает базу данных (с помощью команды `drop-db`) и применяет все миграции для восстановления структуры.

### 10. `make init-db`
Запускает контейнеры Docker, создает миграцию и применяет её, инициализируя базу данных для первого запуска.

### 11. `make run`
Запускает приложение с использованием Uvicorn на порту 8000 с флагом `--reload` для автообновления при изменении кода.

### 10. `make create-superuser`
Создаст в базе данных суперпользователя, согласно настройкам в `.env`.

### 11. `make create-superuser`
Заполнит базу данных фейковыми-сгенерированными объектами: компаний, работников компаний и работников платформы в кол-ве 5 объектов для каждой сущности. По умолчанию пользователи привязываются к первой из созданных компаний в процессе выполнения скрипта.

### 12. `fill-companies`
Заполнит таблицу компаний в бд 5 фейковыми-сгенерированными компаниями.

### 13. `make fill-company-users`
Заполнит таблицу сотрудников компаний в бд 5 фейковыми-сгенерированными сотрудниками, один из которых будет админом. Для этих пользователей в процессе выполнения скрипта создается компания, к которой привязываются создаваемые сотрудники.

### 14. `make fill-tabit-admin-users`
Заполнит таблицу сотрудников платформы Tabit в бд 5 фейковыми-сгенерированными сотрудниками.

### 15. `make fill-company-departments`
Заполняет базу данных 1 компанией и 5 департаментами связанными с этой компанией.

<details>

<summary>Инструкция по установке Make на Windows</summary>

Для установки Make и работы с проектом на Windows, выполните следующие шаги:

1. **Проверить наличие WSL в системе:**
   Следуй инструкциям:
   [Инструкция по установке и настройке WSL](https://code.s3.yandex.net/backend-developer/learning-materials/Инструкция_по_установке_и_настройке_WSL.pdf)

2. **Установить Docker Desktop:**
   Скачайте и установите Docker Desktop для Windows:
   [Скачать Docker Desktop](https://desktop.docker.com/win/main/amd64/Docker%20Desktop%20Installer.exe?utm_source=docker&utm_medium=webreferral&utm_campaign=dd-smartbutton&utm_location=module&_gl=1*1n1mv4y*_ga*MTA0MDU1NzU4NC4xNzAxODkwMjk5*_ga_XJWPQMJYHQ*MTcwNjgxNDkxNS41LjEuMTcwNjgxNDkxOS41Ni4wLjA)

3. **Установить Chocolatey:**
   Откройте Windows Shell от имени администратора и вставьте в консоль следующий код:
   ```powershell
   Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))
   ```

4. **Установить VS Code (или PyCharm):**
Если у вас нет установленного VS Code, скачайте и установите его: скачайте и установите его: [Скачать VS Code](https://code.visualstudio.com/)
Если нет Python, скачайте и установите: [Скачать Python](https://www.python.org/)

5. Клонировать репозиторий: После установки программ, клонируйте репозиторий:
    ```
    git clone git@github.com:Studio-Yandex-Practicum/adaptive_hockey_federation.git
    ```
6. Открыть консоль WSL: В VS Code или другой IDE, откройте консоль и выберите "wsl" вместо PowerShell.
7. Установить Make: В консоли WSL введите команду:
    ```bash
    choco install make
    ```
8. Перезагрузить компьютер: (или поменять местами шаги 4 и 5)
9. Установить Poetry: Для установки Poetry, следуйте инструкциям: [Установка Poetry](https://python-poetry.org/docs/#installing-with-pipx)
Рекомендуется установить Poetry глобально.
10. Настроить Poetry: Введите команду:
    ```bash
    poetry config virtualenvs.in-project true
    ```
11. Установить зависимости: Установите все зависимости и создайте виртуальное окружение:
    ```bash
    poetry install
    ```
12. Активировать виртуальное окружение: Введите команду:
    ```bash
    poetry shell
    ```
13. Работа с Make: Убедитесь, что Docker запущен, и по очереди вводите команды:
    ```bash
    make start-db
    make init-app
    make fill-test-db
    make run
    ```

</details>

## DBeaver
Подключится и проверить БД можно через [DBeaver](https://dbeaver.io/). Создайте новое подключение `Ctrl+Shift+N`. В открывшемся окне выберите PostgresSQL (возможно понадобится установить драйвер), в новом окне заполните поля (варианты взяты из `.env.example`, нужно указать свои из `.env`):
- Хост: localhost
- Порт: 5433
- База данных: 'tabit'
- Пользователь: 'warlock'
- Пароль: 'zTudS8LBSquBMwvS3ky5'

После нажмите `Тест соединения`, и если нет ошибок, нажмите `Готово`. Пользоваться.

## Логирование
Логирование реализовано в двух режимах:
- логирование всех запосов через middleware;
- логирование через функцию logger.

Для логирования необходимо импортировать logger:
```
from src.logger import logger
```
Добавление лога:
```
logger.trace("A trace message.")
logger.debug("A debug message.")
logger.info("An info message.")
logger.success("A success message.")
logger.warning("A warning message.")
logger.error("An error message.")
logger.critical("A critical message.")
```
Уровень логирования задается в .env файле. Подробности в .env.example

## ERD модель данных
Актуальная версия доступна по [ссылке](https://app.erdlab.io/designer/schema/1736745715-tabit)

## Запуск приложения из командной строки.
Точка входа в приложение находится в файле `main.py` в директории `src`.<br>
Запускается по средствам unicorn.
Для запуска приложения необходимо выполнить команду, находясь в корне приложения:
```
python src/main.py
```
Запуск приложения поддерживает флаги:
- `--reload` или `-r` - запустит unicorn с флагом --reload, чтоб отслеживало изменения в коде и перезапускало сервер (удобно для разработки);
- `--host` или `-h` - указывает хост при запуске;
- `--port` или `-p` - указывает порт при запуске.<br>
Например:
```
python src/main.py -r -h 127.0.0.1 -p 1234
```
*Также поддерживается флаг `--create-superuser` или `-c`. Подробнее смотрите "Создать автоматически суперпользователя."*

## Создать автоматически суперпользователя.
Для создания автоматически суперпользователя, заполните `.env` согласно `.env.example`.

- FIRST_SUPERUSER_EMAIL=yandex@yandex.ru  # Почта суперпользователя.
- FIRST_SUPERUSER_PASSWORD=password123  # Пароль суперпользователя.
- FIRST_SUPERUSER_NAME=Ип  # Имя суперпользователя.
- FIRST_SUPERUSER_SURNAME=Ман  # Фамилия суперпользователя.

Теперь можно создать суперпользователя запустив файл `main.py` с флагом `-c`


## Запуск контейнеров локально для отладки CI/CD

Если необходимо проверить, что бэкенд и база данных собираются и работают корректно, можно запустить контейнеры локально с помощью Docker Compose.

### 1. Настроить `.env`
Перед запуском убедитесь, что в корне проекта находится файл `.env`, содержащий все необходимые переменные окружения. Пример `.env` можно найти в `.env.example`.

### 2. Запустить контейнеры
Выполните команду:

```
docker-compose -f infra/local/docker-compose.local.yaml up -d --build
```

- Флаг `-d` запускает контейнеры в фоновом режиме.
- Флаг `--build` пересобирает образы, если были изменения в `Dockerfile`.

### 3. Проверить логи
Если что-то пошло не так, можно посмотреть логи контейнеров:

```
docker-compose -f infra/local/docker-compose.local.yaml logs -f
```

### 4. Остановить контейнеры
Когда тестирование завершено, можно остановить и удалить контейнеры:

```
docker-compose -f infra/local/docker-compose.local.yaml down
```

После этих шагов можно быть уверенным, что CI/CD собирает проект корректно.
```
