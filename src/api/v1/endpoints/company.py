"""Модуль роутеров для пользователя-админа компании."""

from http import HTTPStatus
from typing import Any, List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from fastapi_users.exceptions import InvalidPasswordException, UserAlreadyExists, UserNotExists
from fastapi_users.manager import BaseUserManager
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.auth.dependencies import current_company_admin, current_user
from src.api.v1.auth.managers import get_user_manager
from src.api.v1.constants import Summary
from src.api.v1.validator import validator_check_object_exists
from src.companies.constants import (
    ERROR_INVALID_PASSWORD,
    ERROR_USER_ALREADY_EXISTS,
    ERROR_USER_NOT_EXISTS,
)
from src.companies.crud import company_crud, company_departments_crud
from src.companies.schemas import (
    CompanyDepartmentCreateSchema,
    CompanyDepartmentResponseSchema,
    CompanyDepartmentUpdateSchema,
    CompanyResponseSchema,
    CompanyUserDepartmentUpdateSchema,
)
from src.database.db_depends import get_async_session
from src.users.crud.user import user_crud
from src.users.schemas import UserCreateSchema, UserReadSchema

DEPARTMENT_EXIST_ERROR_MESSAGE = 'Объект с таким именем уже существует.'

router = APIRouter(dependencies=[Depends(current_user), Depends(current_company_admin)])
# router = APIRouter()


@router.get(
    '/{company_slug}',
    response_model=CompanyResponseSchema,
    summary=Summary.TABIT_COMPANY,
)
async def get_company(
    company_slug: str,
    session: AsyncSession = Depends(get_async_session),
):
    """Получает информацию о компании."""
    return await company_crud.get_by_slug(session=session, obj_slug=company_slug, raise_404=True)


@router.get(
    '/{company_slug}/departments',
    response_model=List[CompanyDepartmentResponseSchema],
    summary=Summary.TABIT_COMPANY_DEPARTMENTS_LIST,
)
async def get_all_departments(
    company_slug: str,
    session: AsyncSession = Depends(get_async_session),
):
    """Получает список всех отделов компании."""
    company = await validator_check_object_exists(session, company_crud, object_slug=company_slug)
    return await company_departments_crud.get_multi(
        session=session, filters={'company_id': company.id}
    )


@router.post(
    '/{company_slug}/departments',
    response_model=CompanyDepartmentResponseSchema,
    summary=Summary.TABIT_COMPANY_DEPARTMENTS_CREATE,
)
async def create_department(
    company_slug: str,
    object_in: CompanyDepartmentCreateSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """Создает новый отдел компании."""
    company = await validator_check_object_exists(session, company_crud, object_slug=company_slug)
    object_name = object_in.dict()['name']
    departments = await company_departments_crud.get_multi(
        session=session, filters={'company_id': company.id, 'name': object_name}
    )
    if departments:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=DEPARTMENT_EXIST_ERROR_MESSAGE,
        )
    db_obj = await company_departments_crud.create(
        session=session, obj_in=object_in, auto_commit=False
    )
    session.expunge(db_obj)
    db_obj.company_id = company.id
    session.add(db_obj)
    await session.commit()
    await session.refresh(db_obj)
    return db_obj


@router.post(
    '/{company_slug}/departments/import',
    summary=Summary.TABIT_COMPANY_DEPARTMENTS_IMPORT,
)
async def import_departments(
    company_slug: str,
    session: AsyncSession = Depends(get_async_session),
) -> Any:
    """Импортирует список отделов компании."""
    company = await validator_check_object_exists(session, company_crud, object_slug=company_slug)
    departments_list = await company_departments_crud.get_multi(
        session=session, filters={'company_id': company.id}
    )
    with open('departments_list.txt', 'w') as file:
        file.write('id  name  slug  company_id\n')
        for department in departments_list:
            id = department.id
            name = department.name
            slug = department.slug
            company_id = department.company_id
            file.write(f'{id}  {name}  {slug}  {company_id}\n')
    return FileResponse(
        path='departments_list.txt',
        filename='departments_list.txt',
    )


@router.get(
    '/{company_slug}/departments/{department_id}',
    response_model=CompanyDepartmentResponseSchema,
    summary=Summary.TABIT_COMPANY_DEPARTMENT,
)
async def get_department(
    company_slug: str,
    department_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Получает информацию об отделе компании."""
    await validator_check_object_exists(session, company_crud, object_slug=company_slug)
    return await company_departments_crud.get_or_404(session=session, obj_id=department_id)


@router.patch(
    '/{company_slug}/departments/{department_id}',
    response_model=CompanyDepartmentUpdateSchema,
    summary=Summary.TABIT_COMPANY_DEPARTMENTS_UPDATE,
)
async def update_department(
    company_slug: str,
    department_id: int,
    object_in: CompanyDepartmentUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """Обновляет данные отдела компании."""
    company = await validator_check_object_exists(session, company_crud, object_slug=company_slug)
    object_name = object_in.dict()['name']
    departments = await company_departments_crud.get_multi(
        session=session, filters={'company_id': company.id, 'name': object_name}
    )
    if departments:
        raise HTTPException(
            status_code=HTTPStatus.BAD_REQUEST,
            detail=DEPARTMENT_EXIST_ERROR_MESSAGE,
        )
    db_object = await company_departments_crud.get_or_404(session, obj_id=department_id)
    return await company_departments_crud.update(session, db_obj=db_object, obj_in=object_in)


@router.delete(
    '/{company_slug}/departments/{department_id}',
    summary=Summary.TABIT_COMPANY_DEPARTMENTS_DELETE,
    status_code=HTTPStatus.NO_CONTENT,
)
async def delete_department(
    company_slug: str,
    department_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """Удаляет отдел компании."""
    await validator_check_object_exists(session, company_crud, object_slug=company_slug)
    department = await validator_check_object_exists(
        session, company_departments_crud, object_id=department_id
    )
    await company_departments_crud.remove(session, db_object=department)

    return HTTPStatus.NO_CONTENT


@router.get(
    '/{company_slug}/employees',
    response_model=List[UserReadSchema],
    summary=Summary.TABIT_COMPANY_EMPLOYEES_LIST,
)
async def get_all_employees(
    company_slug: str,
    session: AsyncSession = Depends(get_async_session),
):
    """Получает список всех сотрудников компании."""
    company = await validator_check_object_exists(session, company_crud, object_slug=company_slug)
    return await user_crud.get_multi(session, filters={'company_id': company.id})


@router.post(
    '/{company_slug}/employees',
    response_model=UserReadSchema,
    summary=Summary.TABIT_COMPANY_EMPLOYEES_CREATE,
)
async def add_employee_to_department(
    company_slug: str,
    create_data: UserCreateSchema,
    user_manager: BaseUserManager = Depends(get_user_manager),
    session: AsyncSession = Depends(get_async_session),
):
    """Создает сотрудника в компании."""
    await validator_check_object_exists(session, company_crud, object_slug=company_slug)
    try:
        created_user = await user_manager.create(create_data)
    except UserAlreadyExists:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=ERROR_USER_ALREADY_EXISTS)
    except InvalidPasswordException:
        raise HTTPException(status_code=HTTPStatus.BAD_REQUEST, detail=ERROR_INVALID_PASSWORD)
    return created_user


@router.post(
    '/{company_slug}/employees/import',
    summary=Summary.TABIT_COMPANY_EMPLOYEES_IMPORT,
)
async def import_employees(
    company_slug: str,
    session: AsyncSession = Depends(get_async_session),
):
    """Импортирует список сотрудников компании."""
    company = await validator_check_object_exists(session, company_crud, object_slug=company_slug)
    employees_list = await user_crud.get_multi(session, filters={'company_id': company.id})
    # TODO: Разработать импорт отделов компании
    with open('employees_list.txt', 'w') as file:
        file.write(
            'id name surname patronymic phone_number is_active '
            'birthday telegram_username role start_date_employment '
            'end_date_employment avatar_link company_id current_department_id '
            'last_department_id department_transition_date employee_position\n'
        )
        for employee in employees_list:
            id = employee.id
            name = employee.name
            surname = employee.surname
            patronymic = employee.patronymic
            phone_number = employee.phone_number
            is_active = employee.is_active
            birthday = employee.birthday
            telegram_username = employee.telegram_username
            role = employee.role
            start_date_employment = employee.start_date_employment
            end_date_employment = employee.end_date_employment
            avatar_link = employee.avatar_link
            company_id = employee.company_id
            current_department_id = employee.surname
            last_department_id = employee.surname
            department_transition_date = employee.surname
            employee_position = employee.surname
            file.write(
                f'{id} {name} {surname} {patronymic} {phone_number} {is_active} '
                f'{birthday} {telegram_username} {role} {start_date_employment} '
                f'{end_date_employment} {avatar_link} {company_id} {current_department_id} '
                f'{last_department_id} {department_transition_date} {employee_position}\n'
            )
    return FileResponse(
        path='employees_list.txt',
        filename='employees_list.txt',
    )


@router.get(
    '/{company_slug}/employees/{uuid}',
    response_model=UserReadSchema,
    summary=Summary.TABIT_COMPANY_EMPLOYEE,
)
async def get_employee(
    company_slug: str,
    uuid: UUID,
    session: AsyncSession = Depends(get_async_session),
):
    """Получает информацию о сотруднике компании."""
    await validator_check_object_exists(session, company_crud, object_slug=company_slug)
    return await user_crud.get_or_404(session=session, obj_id=uuid)


@router.patch(
    '/{company_slug}/employees/{uuid}',
    response_model=UserReadSchema,
    summary=Summary.TABIT_COMPANY_EMPLOYEES_UPDATE,
)
async def change_department_of_employee(
    company_slug: str,
    uuid: UUID,
    object_in: CompanyUserDepartmentUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
):
    """Обновляет данные сотрудника компании."""
    await validator_check_object_exists(session, company_crud, object_slug=company_slug)
    db_object = await user_crud.get_or_404(session=session, obj_id=uuid)
    return await user_crud.update(session=session, db_obj=db_object, obj_in=object_in)


@router.delete(
    '/{company_slug}/employees/{uuid}',
    status_code=HTTPStatus.NO_CONTENT,
    summary=Summary.TABIT_COMPANY_EMPLOYEES_DELETE,
)
async def delete_employee_from_department(
    company_slug: str,
    uuid: UUID,
    user_manager: BaseUserManager = Depends(get_user_manager),
    session: AsyncSession = Depends(get_async_session),
):
    """Удаляет сотрудника компании."""
    await validator_check_object_exists(session, company_crud, object_slug=company_slug)
    try:
        user = await user_manager.get(uuid)
        await user_manager.delete(user)
    except UserNotExists:
        raise HTTPException(status_code=HTTPStatus.NOT_FOUND, detail=ERROR_USER_NOT_EXISTS)
    return HTTPStatus.NO_CONTENT
