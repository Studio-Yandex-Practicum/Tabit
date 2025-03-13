from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.problems.models import Meeting, Problem


class TestMeetingsPost:
    """
    Тесты post запросов к эндпоинту meetings.
    """

    async def create_problem(self, async_session, company, owner, name='Test Problem'):
        """
        Зосдание записи Problem в бд.
        """
        problem = Problem(
            name=name,
            description='Some description',
            company_id=company.id,
            color=1,
            type='A',
            status='Новая',
            owner_id=owner.id,
        )
        async_session.add(problem)
        await async_session.commit()
        await async_session.refresh(problem)
        return problem.id

    def build_meeting_data(
        self,
        problem_id,
        owner_id,
        date_meeting,
        title='Test Meeting',
        only_required=True,
        members=[],
    ):
        """
        Генерация данных для встречи.
        """
        data = {
            'title': title,
            'date_meeting': date_meeting,
            'status': 'Новая',
            'problem_id': problem_id,
            'owner_id': str(owner_id),
        }
        if not only_required:
            data['description'] = 'Discuss problem'
            data['place'] = 'Conference Room'
            data['members'] = members
        return data

    @pytest.mark.asyncio
    async def test_create_meeting_whth_all_fields(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        employee_of_company,
        company_for_test,
    ):
        """
        Тест пост запроса на создание встречи со вмеми полями.
        """
        owner = await employee_of_company()
        members = [str((await employee_of_company()).id) for _ in range(3)]
        company = await company_for_test()
        date_meeting = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        problem_id = await self.create_problem(async_session, company, owner)
        meeting_data = self.build_meeting_data(
            problem_id=problem_id,
            owner_id=owner.id,
            date_meeting=date_meeting,
            only_required=False,
            members=members,
        )
        response_meeting = await client.post(
            f'/api/v1/{company.slug}/problems/{problem_id}/meetings', json=meeting_data
        )
        assert response_meeting.status_code == 201

    @pytest.mark.asyncio
    async def test_create_meeting_with_required_fields(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        employee_of_company,
        company_for_test,
    ):
        """
        Тест пост запроса на создание встречи только с обязательными полями.
        """
        owner = await employee_of_company()
        company = await company_for_test()
        date_meeting = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        problem_id = await self.create_problem(async_session, company, owner)
        meeting_data = self.build_meeting_data(
            problem_id=problem_id,
            owner_id=owner.id,
            date_meeting=date_meeting,
        )
        response_meeting = await client.post(
            f'/api/v1/{company.slug}/problems/{problem_id}/meetings', json=meeting_data
        )
        assert response_meeting.status_code == 201

    @pytest.mark.asyncio
    async def test_create_meeting_with_unique_name(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        employee_of_company,
        company_for_test,
    ):
        """
        Тест пост запроса на проверку уникальности имени.
        """
        owner = await employee_of_company()
        company = await company_for_test()
        date_meeting = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        second_date_meeting = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        problem_id = await self.create_problem(async_session, company, owner)
        second_problem = await self.create_problem(
            async_session, company, owner, name='Test Second Problem'
        )
        variants = (
            (problem_id, date_meeting, 201),
            (second_problem, second_date_meeting, 400),
        )
        for problem_id, date, status in variants:
            meeting_data = self.build_meeting_data(
                problem_id=problem_id,
                owner_id=owner.id,
                date_meeting=date,
            )
            response_meeting = await client.post(
                f'/api/v1/{company.slug}/problems/{problem_id}/meetings', json=meeting_data
            )
            assert response_meeting.status_code == status

    @pytest.mark.asyncio
    async def test_create_meeting_with_current_date(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        employee_of_company,
        company_for_test,
    ):
        """
        Тест пост запроса на создание встречи со вмеми полями.
        """
        owner = await employee_of_company()
        company = await company_for_test()
        date_meeting = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        past_date_meeting = (datetime.now() - timedelta(days=7)).strftime('%Y-%m-%d')
        problem_id = await self.create_problem(async_session, company, owner)
        second_problem_id = await self.create_problem(
            async_session, company, owner, name='Test Second Problem'
        )
        variants = (
            (problem_id, date_meeting, 201),
            (second_problem_id, date_meeting, 400),
            (second_problem_id, past_date_meeting, 422),
        )
        for problem_id, date, status in variants:
            meeting_data = self.build_meeting_data(
                problem_id=problem_id,
                owner_id=owner.id,
                date_meeting=date,
            )
            response_meeting = await client.post(
                f'/api/v1/{company.slug}/problems/{problem_id}/meetings', json=meeting_data
            )
            assert response_meeting.status_code == status

    @pytest.mark.asyncio
    async def test_create_no_company_no_problems(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        employee_of_company,
        company_for_test,
    ):
        """
        Тест пост запроса на создание встречи c несуществующей компанией или проблемой.
        """
        owner = await employee_of_company()
        company = await company_for_test()
        problem_id = await self.create_problem(async_session, company, owner)
        date_meeting = (datetime.now() + timedelta(days=7)).strftime('%Y-%m-%d')
        variants = (
            (problem_id, 'No-way-company', 404),
            (problem_id + 1, company.slug, 404),
        )
        for problem_id, company_slug, status in variants:
            meeting_data = self.build_meeting_data(
                problem_id=problem_id,
                owner_id=owner.id,
                date_meeting=date_meeting,
            )
            response_meeting = await client.post(
                f'/api/v1/{company_slug}/problems/{problem_id}/meetings', json=meeting_data
            )
            assert response_meeting.status_code == status


class TestMeetingsGet:
    """
    Тесты get запросов к эндпоинту meetings.
    """

    async def create_problem(self, async_session, company, owner, name='Test Problem'):
        problem = Problem(
            name=name,
            description='Some description',
            company_id=company.id,
            color=1,
            type='A',
            status='Новая',
            owner_id=owner.id,
        )
        async_session.add(problem)
        await async_session.commit()
        await async_session.refresh(problem)
        return problem.id

    async def create_meeting(self, async_session, problem_id, owner, title='Test Meeting'):
        date_meeting = (datetime.now() + timedelta(days=7)).date()
        meeting = Meeting(
            title=title,
            date_meeting=date_meeting,
            description='Discuss problem',
            status='Новая',
            place='Conference Room',
            problem_id=problem_id,
            owner_id=owner.id,
        )
        async_session.add(meeting)
        await async_session.commit()
        await async_session.refresh(meeting)
        return meeting.id

    @pytest.mark.asyncio
    async def test_get_all_meetings_by_problem(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        employee_of_company,
        company_for_test,
    ):
        """
        Проверка получения списка встреч по проблеме.
        """
        owner = await employee_of_company()
        company = await company_for_test()
        problem_id = await self.create_problem(async_session, company, owner)
        for i in range(3):
            await self.create_meeting(async_session, problem_id, owner, title=f'Meeting {i + 1}')
        response = await client.get(f'/api/v1/{company.slug}/problems/{problem_id}/meetings')
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, list)
        assert len(response_data) == 3

    @pytest.mark.asyncio
    async def test_get_single_meeting_info(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        employee_of_company,
        company_for_test,
    ):
        """
        Проверка получения информации о конкретной встрече.
        """
        owner = await employee_of_company()
        company = await company_for_test()
        problem_id = await self.create_problem(async_session, company, owner)
        meeting_id = await self.create_meeting(async_session, problem_id, owner)

        response = await client.get(
            f'/api/v1/{company.slug}/problems/{problem_id}/meetings/{meeting_id}'
        )

        assert response.status_code == 200
        # response_data = response.json()
        # meeting = await async_session.get(Meeting, meeting_id)
        # assert response_data['id'] == meeting_id
        # assert response_data['title'] == meeting.title
        # assert response_data['description'] == meeting.description
        # assert response_data['date_meeting'] == meeting.date_meeting.strftime('%Y-%m-%d')
        # assert response_data['status'] == meeting.status
        # # assert response_data['place'] == meeting.place
        # # assert response_data['created_at'] == meeting.created_at.isoformat()
        # # assert response_data['updated_at'] == meeting.updated_at.isoformat()

    @pytest.mark.asyncio
    async def test_get_meetings_standard_response(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        employee_of_company,
        company_for_test,
    ):
        """
        Проверка корректного ответа на стандартный запрос если нет встреч.
        """
        owner = await employee_of_company()
        company = await company_for_test()
        problem_id = await self.create_problem(async_session, company, owner)
        response = await client.get(f'/api/v1/{company.slug}/problems/{problem_id}/meetings')
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, list)
        assert len(response_data) == 0
        await self.create_meeting(async_session, problem_id, owner)
        response = await client.get(f'/api/v1/{company.slug}/problems/{problem_id}/meetings')
        assert response.status_code == 200
        response_data = response.json()
        assert isinstance(response_data, list)
        assert len(response_data) == 1


class TestMeetingsUpdate:
    """
    Тесты PATCH запросов к эндпоинту meetings.
    """

    async def create_meeting(self, async_session, owner, company):
        date_meeting = (datetime.now() + timedelta(days=7)).date()
        problem = Problem(
            name='Test Problem',
            description='Some description',
            company_id=company.id,
            color=1,
            type='A',
            status='Новая',
            owner_id=owner.id,
        )
        async_session.add(problem)
        await async_session.commit()
        await async_session.refresh(problem)

        meeting = Meeting(
            title='Test Meeting',
            date_meeting=date_meeting,
            description='Discuss problem',
            status='Новая',
            place='Conference Room',
            problem_id=problem.id,
            owner_id=owner.id,
        )
        async_session.add(meeting)
        await async_session.commit()
        await async_session.refresh(meeting)
        return meeting.id, problem.id

    @pytest.mark.asyncio
    async def test_patch_meeting_full_update(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        employee_of_company,
        company_for_test,
    ):
        """
        Полное обновление всех полей встречи.
        """
        owner = await employee_of_company()
        company = await company_for_test()
        meeting_id, problem_id = await self.create_meeting(async_session, owner, company)

        updated_data = {
            'title': 'Updated Title',
            'date_meeting': (datetime.now() + timedelta(days=10)).date().isoformat(),
            'description': 'Updated Description',
            'status': 'Приостановлена',
            'place': 'Updated Place',
        }

        response = await client.patch(
            f'/api/v1/{company.slug}/problems/{problem_id}/meetings/{meeting_id}',
            json=updated_data,
        )
        assert response.status_code == 200

        data = response.json()
        for key, value in updated_data.items():
            assert data[key] == value

    @pytest.mark.asyncio
    async def test_patch_meeting_partial_update(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        employee_of_company,
        company_for_test,
    ):
        """
        Обновление каждого поля встречи отдельно.
        """
        owner = await employee_of_company()
        company = await company_for_test()
        meeting_id, problem_id = await self.create_meeting(async_session, owner, company)
        variants = (
            ('title', 'Updated Title'),
            ('description', 'Updated Description'),
            ('date_meeting', (datetime.now() + timedelta(days=10)).date().isoformat()),
            ('status', 'Приостановлена'),
            ('place', 'Updated Place'),
        )
        for field, value in variants:
            response = await client.patch(
                f'/api/v1/{company.slug}/problems/{problem_id}/meetings/{meeting_id}',
                json={field: value},
            )
            assert response.status_code == 200
            data = response.json()
            assert data[field] == value

    @pytest.mark.asyncio
    async def test_update_meeting_not_found(self, client: AsyncClient, company_for_test):
        """
        Попытка обновить несуществующую встречу.
        """
        company = await company_for_test()
        response_patch = await client.patch(
            f'/api/v1/{company.slug}/problems/1/meetings/1', json={'title': 'No Matter'}
        )
        assert response_patch.status_code == 404


class TestMeetingsDelete:
    """
    Тесты delete запросов к эндпоинту meetings.
    """

    async def create_meeting(self, async_session, owner, company):
        date_meeting = (datetime.now() + timedelta(days=7)).date()
        problem = Problem(
            name='Test Problem',
            description='Some description',
            company_id=company.id,
            color=1,
            type='A',
            status='Новая',
            owner_id=owner.id,
        )
        async_session.add(problem)
        await async_session.commit()
        await async_session.refresh(problem)

        meeting = Meeting(
            title='Test Meeting',
            date_meeting=date_meeting,
            description='Discuss problem',
            status='Новая',
            place='Conference Room',
            problem_id=problem.id,
            owner_id=owner.id,
        )
        async_session.add(meeting)
        await async_session.commit()
        await async_session.refresh(meeting)
        return meeting

    @pytest.mark.asyncio
    async def test_delet_meeting(
        self,
        async_session: AsyncSession,
        client: AsyncClient,
        employee_of_company,
        company_for_test,
    ):
        """
        Тест успешного удаление встречи.
        """
        owner = await employee_of_company()
        company = await company_for_test()
        meeting = await self.create_meeting(async_session, owner, company)
        variants = (
            204,
            404,
        )
        for status in variants:
            response = await client.delete(
                f'/api/v1/{company.slug}/problems/{meeting.problem_id}/meetings/{meeting.id}'
            )
            assert response.status_code == status
