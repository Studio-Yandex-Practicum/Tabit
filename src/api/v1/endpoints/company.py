from uuid import UUID

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db_depends import get_async_session

router = APIRouter()

@router.get(
    '/{company_slug}',
    summary='Получить информацию о всех компаниях',
    dependencies=[Depends(get_async_session)],
)
async def get_all_companies(
        company_slug: str,
        session: AsyncSession = Depends(get_async_session),
):
    """Получает информацию о всех компаниях."""
    return {'message': 'Список компаний пока пуст'}

@router.get(
    '/{company_slug}/departments',
    summary='Получить список всех отделов компании',
    dependencies=[Depends(get_async_session)],
)
async def get_all_departments(
        company_slug: str,
        session: AsyncSession = Depends(get_async_session),
):
    """Получает список всех отделов компании."""
    # TODO: Проверить существование компании
    return {'message': 'Список отделов компании пока пуст'}

@router.post(
    '/{company_slug}/departments',
    summary='Создать новый отдел компании',
    dependencies=[Depends(get_async_session)],
)
async def create_department(
        company_slug: str,
        session: AsyncSession = Depends(get_async_session),
):
    """Создание нового отдела компании."""
    # TODO: Проверить существование компании
    # TODO: Проверить уникальность названия отдела
    return {'message': 'Создание отдела компании временно недоступно'}

@router.post(
    '/{company_slug}/departments/import',
    summary='Импортировать список отделов отдел компании',
    dependencies=[Depends(get_async_session)],
)
async def import_departments(
        company_slug: str,
        session: AsyncSession = Depends(get_async_session),
):
    """Импортирование списка отделов компании."""
    # TODO: Проверить существование компании
    # TODO: Разработать импорт отделов компании
    return {'message': 'Импортирование отделов компании временно недоступно'}

@router.get(
    '/{company_slug}/department/{department_id}',
    summary='Получить информацию об отделе компании',
    dependencies=[Depends(get_async_session)],
)
async def get_department(
        company_slug: str,
        department_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """Получение информации об отделе компании."""
    # TODO: Проверить существование компании + отдела
    return {'message': 'Информация об отделе компании пока недоступна'}


@router.patch(
    '/{company_slug}/department/{department_id}',
    summary='Обновить информацию об отделе компании',
    dependencies=[Depends(get_async_session)],
)
async def update_department(
        company_slug: str,
        department_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """Обновление данных отдела компании."""
    # TODO: Проверить существование компании + отдела
    # TODO: Проверить уникальность названия отдела
    return {'message': 'Обновление отдела компании временно недоступно'}

@router.delete(
    '/{company_slug}/department/{department_id}',
    summary='Удалить отдел компании',
    dependencies=[Depends(get_async_session)],
)
async def delete_department(
        company_slug: str,
        department_id: int,
        session: AsyncSession = Depends(get_async_session),
):
    """Удаление отдела компании."""
    # TODO: Проверить существование компании + отдела
    return {'message': 'Удаление отдела компании временно недоступно'}

@router.get(
    '/{company_slug}/employees',
    summary='Получить список всех сотрудников компании',
    dependencies=[Depends(get_async_session)],
)
async def get_all_employees(
        company_slug: str,
        session: AsyncSession = Depends(get_async_session),
):
    """Получает список всех сотрудников компании."""
    # TODO: Проверить существование компании
    return {'message': 'Список сотрудников компании пока пуст'}

@router.post(
    '/{company_slug}/employees',
    summary='Добавить сотрудника в отдел компании',
    dependencies=[Depends(get_async_session)],
)
async def add_employee_to_department(
        company_slug: str,
        session: AsyncSession = Depends(get_async_session),
):
    """Добавление сотрудника в отдел компании."""
    # TODO: Проверить существование компании
    return {'message': 'Создание сотрудника компании временно недоступно'}

@router.post(
    '/{company_slug}/employees/import',
    summary='Импортировать список сотрудников компании',
    dependencies=[Depends(get_async_session)],
)
async def import_employees(
        company_slug: str,
        session: AsyncSession = Depends(get_async_session),
):
    """Импортирование списка сотрудников компании."""
    # TODO: Проверить существование компании
    # TODO: Разработать импорт сотрудников компании
    return {'message': 'Импортирование сотрудников компании временно недоступно'}

@router.get(
    '/{company_slug}/employees/{uuid}',
    summary='Получить информацию о сотруднике компании',
    dependencies=[Depends(get_async_session)],
)
async def get_employee(
        company_slug: str,
        employee_id: UUID,
        session: AsyncSession = Depends(get_async_session),
):
    """Получение информации о сотруднике компании."""
    # TODO: Проверить существование компании + сотрудника
    return {'message': 'Информация о сотруднике компании пока недоступна'}


@router.patch(
    '/{company_slug}/employees/{uuid}',
    summary='Изменить отдел сотрудника компании',
    dependencies=[Depends(get_async_session)],
)
async def change_department_of_employee(
        company_slug: str,
        employee_id: UUID,
        session: AsyncSession = Depends(get_async_session),
):
    """Обновление данных сотрудника компании."""
    # TODO: Проверить существование компании + сотрудника
    return {'message': 'Обновление сотрудника компании временно недоступно'}


@router.delete(
    '/{company_slug}/employees/{uuid}',
    summary='Удалить сотрудника из департамента компании',
    dependencies=[Depends(get_async_session)],
)
async def delete_employee_from_department(
        company_slug: str,
        employee_id: UUID,
        session: AsyncSession = Depends(get_async_session),
):
    """Удаление сотрудника компании."""
    # TODO: Проверить существование компании + сотрудника
    return {'message': 'Удаление сотрудника компании временно недоступно'}
