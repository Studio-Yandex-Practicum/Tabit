from datetime import datetime
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest

from src.crud.crud_research import research_instance_crud, research_type_crud
from src.models import ResearchInstance, ResearchType
from src.schemas.research import (
    QuestionOption,
    QuestionSchema,
    ResearchInstanceCreateSchema,
    ResearchInstanceUpdateSchema,
    ResearchTypeCreateSchema,
)


class TestResearchSchemas:
    """Тесты для схем Research."""

    def test_question_option_schema(self):
        """Тест схемы варианта ответа."""
        option = QuestionOption(id='opt1', text='Да', value='yes')
        assert option.id == 'opt1'
        assert option.text == 'Да'
        assert option.value == 'yes'

    def test_question_schema_radio(self):
        """Тест схемы вопроса типа radio."""
        question = QuestionSchema(
            id='q1',
            text='Вы удовлетворены?',
            type='radio',
            required=True,
            options=[
                QuestionOption(id='opt1', text='Да', value='yes'),
                QuestionOption(id='opt2', text='Нет', value='no'),
            ],
        )
        assert question.type == 'radio'
        assert len(question.options) == 2

    def test_question_schema_text(self):
        """Тест схемы вопроса типа text."""
        question = QuestionSchema(
            id='q2',
            text='Ваше имя:',
            type='text',
            required=True,
            placeholder='Введите имя',
            max_length=100,
        )
        assert question.type == 'text'
        assert question.placeholder == 'Введите имя'
        assert question.max_length == 100

    def test_research_type_create_schema(self):
        """Тест схемы создания типа опроса."""
        research_data = ResearchTypeCreateSchema(
            title='Тестовый опрос',
            description='Описание теста',
            questions=[
                QuestionSchema(
                    id='q1',
                    text='Вопрос?',
                    type='radio',
                    required=True,
                    options=[QuestionOption(id='opt1', text='Да', value='yes')],
                )
            ],
            is_active=True,
        )
        assert research_data.title == 'Тестовый опрос'
        assert len(research_data.questions) == 1

    def test_research_instance_create_schema(self):
        """Тест схемы создания экземпляра опроса."""
        user_id = uuid4()
        instance_data = ResearchInstanceCreateSchema(research_type_id=1, user_id=user_id)
        assert instance_data.research_type_id == 1
        assert instance_data.user_id == user_id

    def test_research_instance_update_schema(self):
        """Тест схемы обновления экземпляра опроса."""
        update_data = ResearchInstanceUpdateSchema(answers={'q1': 'yes'}, status='COMPLETED')
        assert update_data.answers == {'q1': 'yes'}
        assert update_data.status == 'COMPLETED'


class TestResearchCRUD:
    """Тесты для CRUD операций Research."""

    @pytest.mark.asyncio
    async def test_create_research_type(self):
        """Тест создания типа опроса."""
        mock_session = AsyncMock()

        research_data = ResearchTypeCreateSchema(
            title='Тестовый опрос',
            description='Описание',
            questions=[
                QuestionSchema(
                    id='q1',
                    text='Вопрос?',
                    type='radio',
                    required=True,
                    options=[QuestionOption(id='opt1', text='Да', value='yes')],
                )
            ],
        )

        company_id = 1
        created_by = uuid4()

        # Мокаем создание объекта
        mock_research_type = ResearchType(
            id=1,
            company_id=company_id,
            title=research_data.title,
            description=research_data.description,
            questions='[{"id": "q1", "text": "Вопрос?", "type": "radio"}]',
            is_active=True,
            created_by=created_by,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow(),
        )

        with patch.object(research_type_crud, 'model', return_value=mock_research_type):
            result = await research_type_crud.create_research_type(
                mock_session, research_data, company_id, created_by
            )

            assert result.title == 'Тестовый опрос'
            assert result.company_id == company_id
            assert result.created_by == created_by

    @pytest.mark.asyncio
    async def test_get_research_types_by_company(self):
        """Тест получения типов опросов по компании."""
        mock_session = AsyncMock()
        company_id = 1

        # Мокаем результат запроса
        mock_types = [
            ResearchType(
                id=1, company_id=company_id, title='Опрос 1', questions='[]', is_active=True
            ),
            ResearchType(
                id=2, company_id=company_id, title='Опрос 2', questions='[]', is_active=True
            ),
        ]

        with patch.object(research_type_crud, 'get_multi', return_value=mock_types):
            result = await research_type_crud.get_by_company(
                mock_session, company_id, active_only=True
            )

            assert len(result) == 2
            assert result[0].company_id == company_id
            assert result[1].company_id == company_id

    @pytest.mark.asyncio
    async def test_create_research_instance(self):
        """Тест создания экземпляра опроса."""
        mock_session = AsyncMock()

        instance_data = ResearchInstanceCreateSchema(research_type_id=1, user_id=uuid4())

        mock_instance = ResearchInstance(
            id=1,
            research_type_id=instance_data.research_type_id,
            user_id=instance_data.user_id,
            status='IN_PROGRESS',
            started_at=datetime.utcnow(),
        )

        with patch.object(research_instance_crud, 'model', return_value=mock_instance):
            result = await research_instance_crud.create_instance(mock_session, instance_data)

            assert result.research_type_id == instance_data.research_type_id
            assert result.user_id == instance_data.user_id
            assert result.status == 'IN_PROGRESS'

    @pytest.mark.asyncio
    async def test_update_research_instance(self):
        """Тест обновления экземпляра опроса."""
        mock_session = AsyncMock()

        # Создаем существующий экземпляр
        existing_instance = ResearchInstance(
            id=1,
            research_type_id=1,
            user_id=uuid4(),
            status='IN_PROGRESS',
            started_at=datetime.utcnow(),
        )

        update_data = ResearchInstanceUpdateSchema(answers={'q1': 'yes'}, status='COMPLETED')

        with patch.object(research_instance_crud, 'get_multi', return_value=[existing_instance]):
            result = await research_instance_crud.update_instance(
                mock_session, existing_instance, update_data
            )

            assert result.answers == '{"q1": "yes"}'
            assert result.status == 'COMPLETED'
            assert result.completed_at is not None


class TestResearchValidation:
    """Тесты валидации данных Research."""

    def test_question_validation_radio_without_options(self):
        """Тест валидации radio вопроса без вариантов ответа."""
        with pytest.raises(ValueError, match='должен содержать варианты ответов'):
            QuestionSchema(
                id='q1',
                text='Вопрос?',
                type='radio',
                required=True,
                options=[],  # Пустой список вариантов
            )

    def test_question_validation_text_with_options(self):
        """Тест валидации text вопроса с вариантами ответа."""
        with pytest.raises(ValueError, match='не должен содержать варианты ответов'):
            QuestionSchema(
                id='q1',
                text='Вопрос?',
                type='text',
                required=True,
                options=[  # Варианты для text вопроса
                    QuestionOption(id='opt1', text='Вариант', value='option')
                ],
            )

    def test_unique_question_ids(self):
        """Тест валидации уникальности ID вопросов."""
        with pytest.raises(ValueError, match='ID вопросов должны быть уникальными'):
            ResearchTypeCreateSchema(
                title='Тест',
                questions=[
                    QuestionSchema(
                        id='q1',  # Дублирующийся ID
                        text='Вопрос 1',
                        type='radio',
                        options=[QuestionOption(id='opt1', text='Да', value='yes')],
                    ),
                    QuestionSchema(
                        id='q1',  # Дублирующийся ID
                        text='Вопрос 2',
                        type='text',
                    ),
                ],
            )

    def test_empty_questions_list(self):
        """Тест валидации пустого списка вопросов."""
        with pytest.raises(ValueError, match='не может быть пустым'):
            ResearchTypeCreateSchema(
                title='Тест',
                questions=[],  # Пустой список вопросов
            )


class TestResearchModels:
    """Тесты для моделей Research."""

    def test_research_type_repr(self):
        """Тест строкового представления ResearchType."""
        research_type = ResearchType(
            id=1, company_id=1, title='Тестовый опрос', questions='[]', is_active=True
        )

        repr_str = repr(research_type)
        assert 'ResearchType' in repr_str
        assert 'id=1' in repr_str
        assert "title='Тестовый опрос'" in repr_str

    def test_research_instance_repr(self):
        """Тест строкового представления ResearchInstance."""
        instance = ResearchInstance(
            id=1, research_type_id=1, user_id=uuid4(), status='IN_PROGRESS'
        )

        repr_str = repr(instance)
        assert 'ResearchInstance' in repr_str
        assert 'id=1' in repr_str
        assert "status='IN_PROGRESS'" in repr_str


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
