# Research (Однотипные опросы) - Backend API

## Обзор

Модуль Research предоставляет API для создания и управления однотипными опросами в системе Tabit. Опросы могут содержать различные типы вопросов: radio, checkbox, text, textarea.

## Структура

### Модели

- **ResearchType** - тип опроса с определением структуры вопросов
- **ResearchInstance** - экземпляр опроса для конкретного пользователя

### Основные компоненты

- `src/models/research.py` - модели данных
- `src/schemas/research.py` - Pydantic схемы для валидации
- `src/crud/crud_research.py` - CRUD операции
- `src/features_v1/company_research_management/endpoints.py` - API эндпоинты

## API Endpoints

### Типы опросов (Research Types)

#### Создание типа опроса
```http
POST /api/v1/{company_slug}/research/types
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Опрос удовлетворенности",
  "description": "Опрос для оценки качества обслуживания",
  "questions": [
    {
      "id": "q1",
      "text": "Вы удовлетворены качеством обслуживания?",
      "type": "radio",
      "required": true,
      "options": [
        {"id": "opt1", "text": "Да", "value": "yes"},
        {"id": "opt2", "text": "Нет", "value": "no"},
        {"id": "opt3", "text": "Надо подумать", "value": "maybe"}
      ]
    },
    {
      "id": "q2",
      "text": "Что бы вы хотели добавить?",
      "type": "checkbox",
      "required": true,
      "options": [
        {"id": "opt4", "text": "Личный менеджер", "value": "manager"},
        {"id": "opt5", "text": "Персональные скидки", "value": "discounts"},
        {"id": "opt6", "text": "Ещё что-нибудь", "value": "other"}
      ]
    },
    {
      "id": "q3",
      "text": "Оставьте честный отзыв",
      "type": "textarea",
      "required": true,
      "placeholder": "Начните писать ваш ответ здесь",
      "max_length": 1000
    }
  ],
  "is_active": true
}
```

#### Получение типов опросов
```http
GET /api/v1/{company_slug}/research/types?active_only=true
Authorization: Bearer {token}
```

#### Получение типа опроса по ID
```http
GET /api/v1/{company_slug}/research/types/{research_type_id}
Authorization: Bearer {token}
```

#### Обновление типа опроса
```http
PATCH /api/v1/{company_slug}/research/types/{research_type_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "title": "Обновленный заголовок",
  "is_active": false
}
```

#### Удаление типа опроса
```http
DELETE /api/v1/{company_slug}/research/types/{research_type_id}
Authorization: Bearer {token}
```

### Экземпляры опросов (Research Instances)

#### Создание экземпляра опроса
```http
POST /api/v1/{company_slug}/research/instances
Authorization: Bearer {token}
Content-Type: application/json

{
  "research_type_id": 1,
  "user_id": "uuid-пользователя"
}
```

#### Получение экземпляров пользователя
```http
GET /api/v1/{company_slug}/research/instances
Authorization: Bearer {token}
```

#### Получение экземпляра по ID
```http
GET /api/v1/{company_slug}/research/instances/{instance_id}
Authorization: Bearer {token}
```

#### Обновление экземпляра (сохранение ответов)
```http
PATCH /api/v1/{company_slug}/research/instances/{instance_id}
Authorization: Bearer {token}
Content-Type: application/json

{
  "answers": {
    "q1": "yes",
    "q2": ["manager", "discounts"],
    "q3": "Отличный сервис, все понравилось!"
  },
  "status": "COMPLETED"
}
```

### Статистика

#### Получение статистики по типу опроса
```http
GET /api/v1/{company_slug}/research/types/{research_type_id}/statistics
Authorization: Bearer {token}
```

## Права доступа

- **Создание/редактирование/удаление типов опросов**: только модераторы и админы компании
- **Просмотр типов опросов**: все авторизованные пользователи компании
- **Создание/редактирование экземпляров**: пользователи могут работать только со своими опросами
- **Просмотр статистики**: только модераторы и админы компании

## Типы вопросов

### Radio (Один выбор)
```json
{
  "id": "q1",
  "text": "Вопрос с одним вариантом ответа?",
  "type": "radio",
  "required": true,
  "options": [
    {"id": "opt1", "text": "Да", "value": "yes"},
    {"id": "opt2", "text": "Нет", "value": "no"}
  ]
}
```

### Checkbox (Множественный выбор)
```json
{
  "id": "q2",
  "text": "Что вам нравится?",
  "type": "checkbox",
  "required": true,
  "options": [
    {"id": "opt1", "text": "Качество", "value": "quality"},
    {"id": "opt2", "text": "Скорость", "value": "speed"},
    {"id": "opt3", "text": "Цена", "value": "price"}
  ]
}
```

### Text (Однострочный текст)
```json
{
  "id": "q3",
  "text": "Ваше имя:",
  "type": "text",
  "required": true,
  "placeholder": "Введите ваше имя",
  "max_length": 100
}
```

### Textarea (Многострочный текст)
```json
{
  "id": "q4",
  "text": "Ваши предложения:",
  "type": "textarea",
  "required": false,
  "placeholder": "Опишите ваши предложения",
  "max_length": 1000
}
```

## Примеры использования

### Создание опроса с разными типами вопросов

```python
from src.schemas.research import ResearchTypeCreateSchema, QuestionSchema, QuestionOption

# Создаем опрос
research_data = ResearchTypeCreateSchema(
    title="Опрос качества услуг",
    description="Опрос для оценки качества предоставляемых услуг",
    questions=[
        QuestionSchema(
            id="satisfaction",
            text="Вы удовлетворены качеством услуг?",
            type="radio",
            required=True,
            options=[
                QuestionOption(id="yes", text="Да", value="yes"),
                QuestionOption(id="no", text="Нет", value="no"),
                QuestionOption(id="maybe", text="Затрудняюсь ответить", value="maybe")
            ]
        ),
        QuestionSchema(
            id="improvements",
            text="Что можно улучшить?",
            type="checkbox",
            required=False,
            options=[
                QuestionOption(id="speed", text="Скорость работы", value="speed"),
                QuestionOption(id="quality", text="Качество", value="quality"),
                QuestionOption(id="price", text="Цены", value="price")
            ]
        ),
        QuestionSchema(
            id="comments",
            text="Дополнительные комментарии",
            type="textarea",
            required=False,
            placeholder="Оставьте ваши комментарии",
            max_length=500
        )
    ]
)
```

### Обработка ответов

```python
from src.schemas.research import ResearchInstanceUpdateSchema

# Сохраняем ответы пользователя
answers_data = ResearchInstanceUpdateSchema(
    answers={
        "satisfaction": "yes",
        "improvements": ["speed", "quality"],
        "comments": "Все отлично, но можно работать быстрее"
    },
    status="COMPLETED"
)
```

## Миграции

Для создания таблиц в базе данных выполните:

```bash
alembic upgrade head
```

## Тестирование

Модуль включает в себя тесты для проверки всех основных функций. Запустите тесты командой:

```bash
pytest tests/test_research.py -v
```

## Логирование

Все операции логируются с использованием стандартного логгера системы. Ошибки и важные события записываются в лог-файлы.

## Безопасность

- Все эндпоинты защищены аутентификацией
- Проверка прав доступа на уровне компании
- Валидация входных данных через Pydantic схемы
- SQL-инъекции предотвращены через ORM
