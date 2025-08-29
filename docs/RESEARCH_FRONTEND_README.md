# Research (Однотипные опросы) - Frontend Integration

## Обзор

Этот документ описывает, как интегрировать однотипные опросы (Research) в фронтенд приложение Tabit. Модуль позволяет создавать, отображать и проходить опросы с различными типами вопросов.

## Основные компоненты

### Типы вопросов

- **Radio** - выбор одного варианта из списка
- **Checkbox** - выбор нескольких вариантов
- **Text** - однострочный текстовый ввод
- **Textarea** - многострочный текстовый ввод

## API интеграция

### Базовый URL
```
/api/v1/{company_slug}/research
```

### Аутентификация
Все запросы должны содержать Bearer токен в заголовке Authorization:
```javascript
headers: {
  'Authorization': `Bearer ${token}`,
  'Content-Type': 'application/json'
}
```

## Основные функции

### 1. Получение списка типов опросов

```javascript
async function getResearchTypes(companySlug, activeOnly = true) {
  try {
    const response = await fetch(
      `/api/v1/${companySlug}/research/types?active_only=${activeOnly}`,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
        }
      }
    );

    if (!response.ok) {
      throw new Error('Ошибка получения опросов');
    }

    return await response.json();
  } catch (error) {
    console.error('Ошибка:', error);
    throw error;
  }
}
```

### 2. Создание типа опроса (только для модераторов)

```javascript
async function createResearchType(companySlug, researchData) {
  try {
    const response = await fetch(
      `/api/v1/${companySlug}/research/types`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(researchData)
      }
    );

    if (!response.ok) {
      throw new Error('Ошибка создания опроса');
    }

    return await response.json();
  } catch (error) {
    console.error('Ошибка:', error);
    throw error;
  }
}

// Пример данных для создания опроса
const researchData = {
  title: "Опрос удовлетворенности",
  description: "Оцените качество наших услуг",
  questions: [
    {
      id: "satisfaction",
      text: "Вы удовлетворены качеством обслуживания?",
      type: "radio",
      required: true,
      options: [
        { id: "yes", text: "Да", value: "yes" },
        { id: "no", text: "Нет", value: "no" },
        { id: "maybe", text: "Надо подумать", value: "maybe" }
      ]
    },
    {
      id: "improvements",
      text: "Что бы вы хотели добавить?",
      type: "checkbox",
      required: true,
      options: [
        { id: "manager", text: "Личный менеджер", value: "manager" },
        { id: "discounts", text: "Персональные скидки", value: "discounts" },
        { id: "other", text: "Ещё что-нибудь", value: "other" }
      ]
    },
    {
      id: "feedback",
      text: "Оставьте честный отзыв",
      type: "textarea",
      required: true,
      placeholder: "Начните писать ваш ответ здесь",
      max_length: 1000
    }
  ],
  is_active: true
};
```

### 3. Создание экземпляра опроса

```javascript
async function createResearchInstance(companySlug, researchTypeId, userId) {
  try {
    const response = await fetch(
      `/api/v1/${companySlug}/research/instances`,
      {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          research_type_id: researchTypeId,
          user_id: userId
        })
      }
    );

    if (!response.ok) {
      throw new Error('Ошибка создания экземпляра опроса');
    }

    return await response.json();
  } catch (error) {
    console.error('Ошибка:', error);
    throw error;
  }
}
```

### 4. Сохранение ответов

```javascript
async function saveAnswers(companySlug, instanceId, answers, status = 'COMPLETED') {
  try {
    const response = await fetch(
      `/api/v1/${companySlug}/research/instances/${instanceId}`,
      {
        method: 'PATCH',
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          answers: answers,
          status: status
        })
      }
    );

    if (!response.ok) {
      throw new Error('Ошибка сохранения ответов');
    }

    return await response.json();
  } catch (error) {
    console.error('Ошибка:', error);
    throw error;
  }
}

// Пример ответов
const answers = {
  "satisfaction": "yes",
  "improvements": ["manager", "discounts"],
  "feedback": "Отличный сервис! Все очень понравилось."
};
```
