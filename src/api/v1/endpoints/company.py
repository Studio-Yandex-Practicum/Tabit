"""Модуль роутеров для пользователя-админа компании."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi_users.exceptions import InvalidPasswordException, UserAlreadyExists, UserNotExists
from fastapi_users.manager import BaseUserManager
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.v1.auth.dependencies import current_company_admin, current_user_tabit
from src.api.v1.auth.managers import get_user_manager
from src.core.constants.endpoints import Summary, TextError
from src.api.v1.validator import validator_check_object_exists
from src.core.constants.company import (
    ERROR_INVALID_PASSWORD,
    ERROR_USER_ALREADY_EXISTS,
    ERROR_USER_NOT_EXISTS,
)
from src.companies.crud import company_crud, company_departments_crud
from src.schemas import (
    CompanyDepartmentCreateSchema,
    CompanyDepartmentResponseSchema,
    CompanyDepartmentUpdateSchema,
    CompanyEmployeeUpdateSchema,
    CompanyResponseSchema,
    UserCreateSchema,
    UserReadSchema,
)
from src.core.database.db_depends import get_async_session
from src.users.crud.user import user_crud

router = APIRouter(dependencies=[Depends(current_user_tabit), Depends(current_company_admin)])


@router.get(
    '/{company_slug}',
    summary=Summary.TABIT_COMPANY,
    status_code=status.HTTP_200_OK,
    response_model=CompanyResponseSchema,
)
async def get_company(
    company_slug: str,
    session: AsyncSession = Depends(get_async_session),
) -> CompanyResponseSchema | None:
    """
    Получает информацию о компании.
    Доступно только пользователю-админу компании.
    В пути принимает 'company_slug' - значение `slug` компании.
    Параметры декоратора:
        path: URL-адрес, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: Pydantic-схема.
        summary: краткое описание.
    Параметры функции:
        company_slug: значение `slug` компании.
        session: асинхронная сессия.
    Вернет JSON, пример:
    {
      "id": 0,
      "name": "string",
      "description": "string",
      "logo": "string",
      "license_id": 0,
      "max_admins_count": 0,
      "max_employees_count": 0,
      "start_license_time": "2025-02-18T13:34:06.541Z",
      "end_license_time": "2025-02-18T13:34:06.541Z",
      "is_active": true,
      "slug": "string",
      "created_at": "2025-02-18T13:34:06.541Z",
      "updated_at": "2025-02-18T13:34:06.541Z"
    }
    Если компании не существует вернет ответ со статусом 404.
    """
    return await company_crud.get_by_slug(session=session, obj_slug=company_slug, raise_404=True)


@router.get(
    '/{company_slug}/departments',
    response_model=List[CompanyDepartmentResponseSchema],
    status_code=status.HTTP_200_OK,
    summary=Summary.TABIT_COMPANY_DEPARTMENTS_LIST,
)
async def get_all_departments(
    company_slug: str,
    session: AsyncSession = Depends(get_async_session),
) -> List[CompanyDepartmentResponseSchema]:
    """
    Получает список всех отделов компании.
    Доступно только пользователю-админу компании.
    Проверяет существует ли компания и после, по id компании фильтрует отделы.
    В пути принимает 'company_slug' - значение `slug` компании.
    Параметры декоратора:
        path: URL-адрес, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
        summary: краткое описание.
    Параметры функции:
        company_slug: значение `slug` компании.
        session: асинхронная сессия.
    Вернет JSON, пример:
    [
      {
        "name": "string",
        "slug": "string",
        "id": 0,
        "company_id": 0
      }
    ]
    Если отделов нет вернет пустой список.
    """
    company = await validator_check_object_exists(session, company_crud, object_slug=company_slug)
    return await company_departments_crud.get_multi(
        session=session, filters={'company_id': company.id}
    )


@router.post(
    '/{company_slug}/departments',
    response_model=CompanyDepartmentResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary=Summary.TABIT_COMPANY_DEPARTMENTS_CREATE,
)
async def create_department(
    company_slug: str,
    object_in: CompanyDepartmentCreateSchema,
    session: AsyncSession = Depends(get_async_session),
) -> CompanyDepartmentResponseSchema:
    """
    Создает новый отдел компании.
    Доступно только пользователю-админу компании.
    Проверяет существует ли компания и после, передает id компании в данные для создания отдела.
    Имя отдела введенное пользователем проверяется на уникальность, если уникальность не соблюдена
    вернется ответ со статусом 400.
    В пути принимает 'company_slug' - значение `slug` компании.
    Параметры декоратора:
        path: URL-адрес, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: Pydantic-схема.
        summary: краткое описание.
    Параметры функции:
        company_slug: значение `slug` компании.
        object_in: данные введенные пользователем в соответствии со схемой.
        session: асинхронная сессия.
    При успешной транзакции вернет JSON, пример:
      {
        "name": "string",
        "slug": "string",
        "id": 0,
        "company_id": 0
      }
    """
    company = await validator_check_object_exists(session, company_crud, object_slug=company_slug)
    object_name = object_in.model_dump()['name']
    departments = await company_departments_crud.get_multi(
        session=session, filters={'company_id': company.id, 'name': object_name}
    )
    if departments:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=TextError.DEPARTMENT_EXIST_ERROR_MESSAGE,
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
    status_code=status.HTTP_200_OK,
    summary=Summary.TABIT_COMPANY_DEPARTMENTS_IMPORT,
)
async def import_departments(
    company_slug: str,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Импортирует список отделов компании.
    Доступно только пользователю-админу компании.
    Проверяет существует ли компания и после, передает id компании для фильтрации списка.
    После записывет данные в файл.
    В пути принимает 'company_slug' - значение `slug` компании.
    Параметры декоратора:
        path: URL-адрес, который будет использоваться для этой операции.
        summary: краткое описание.
    Параметры функции:
        company_slug: значение `slug` компании.
        session: асинхронная сессия.
    Вернет файл .txt с данными отделов.
    """
    company = await validator_check_object_exists(session, company_crud, object_slug=company_slug)
    departments_list = await company_departments_crud.get_multi(
        session=session, filters={'company_id': company.id}
    )
    return await company_crud.get_import(objects_in=departments_list, file_name='departments_list')


@router.get(
    '/{company_slug}/departments/{department_id}',
    response_model=CompanyDepartmentResponseSchema,
    status_code=status.HTTP_200_OK,
    summary=Summary.TABIT_COMPANY_DEPARTMENT,
)
async def get_department(
    company_slug: str,
    department_id: int,
    session: AsyncSession = Depends(get_async_session),
) -> CompanyDepartmentResponseSchema:
    """
    Получает информацию об отделе компании.
    Доступно только пользователю-админу компании.
    Проверяет существует ли компания и после, по id отдела получает данные.
    В пути принимает 'company_slug' - значение `slug` компании и 'department_id'
     - значение `id` отдела.
    Параметры декоратора:
        path: URL-адрес, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: Pydantic-схема.
        summary: краткое описание.
    Параметры функции:
        company_slug: значение `slug` компании.
        department_id: значение `id` отдела.
        session: асинхронная сессия.
    При успешной транзакции вернет JSON, пример:
      {
        "name": "string",
        "slug": "string",
        "id": 0,
        "company_id": 0
      }
    Если отдела нет вернет ответ со статусом 404.
    """
    await validator_check_object_exists(session, company_crud, object_slug=company_slug)
    return await company_departments_crud.get_or_404(session=session, obj_id=department_id)


@router.patch(
    '/{company_slug}/departments/{department_id}',
    response_model=CompanyDepartmentResponseSchema,
    status_code=status.HTTP_200_OK,
    summary=Summary.TABIT_COMPANY_DEPARTMENTS_UPDATE,
)
async def update_department(
    company_slug: str,
    department_id: int,
    object_in: CompanyDepartmentUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
) -> CompanyDepartmentResponseSchema:
    """
    Обновляет данные отдела компании.
    Доступно только пользователю-админу компании.
    Проверяет существует ли компания и после, передает id компании и имя отдела
    введенное пользователем для проверки на уникальность, если уникальность не соблюдена
    вернется ответ со статусом 400. Далее получает объект отдела и передает с данными
     для обновления.
    В пути принимает 'company_slug' - значение `slug` компании и 'department_id'
     - значение `id` отдела.
    Параметры декоратора:
        path: URL-адрес, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: Pydantic-схема.
        summary: краткое описание.
    Параметры функции:
        company_slug: значение `slug` компании.
        department_id: значение `id` отдела.
        object_in: данные введенные пользователем в соответствии со схемой.
        session: асинхронная сессия.
    При успешной транзакции вернет JSON, пример:
      {
        "name": "string",
        "slug": "string",
        "id": 0,
        "company_id": 0
      }
    Если отдел не найден вернет ответ со статусом 404.
    """
    company = await validator_check_object_exists(session, company_crud, object_slug=company_slug)
    object_name = object_in.model_dump()['name']
    departments = await company_departments_crud.get_multi(
        session=session, filters={'company_id': company.id, 'name': object_name}
    )
    if departments:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=TextError.DEPARTMENT_EXIST_ERROR_MESSAGE,
        )
    db_object = await company_departments_crud.get_or_404(session, obj_id=department_id)
    return await company_departments_crud.update(session, db_obj=db_object, obj_in=object_in)


@router.delete(
    '/{company_slug}/departments/{department_id}',
    summary=Summary.TABIT_COMPANY_DEPARTMENTS_DELETE,
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_department(
    company_slug: str,
    department_id: int,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Удаляет отдел компании.
    Доступно только пользователю-админу компании.
    Проверяет существует ли компания и отдел, и после передает объект отдела для удаления.
    В пути принимает 'company_slug' - значение `slug` компании и 'department_id'
     - значение `id` отдела.
    Параметры декоратора:
        path: URL-адрес, который будет использоваться для этой операции.
        summary: краткое описание.
        status_code: код статуса ответа.
    Параметры функции:
        company_slug: значение `slug` компании.
        department_id: значение `id` отдела.
        session: асинхронная сессия.
    При успешной транзакции вернет ответ со статусом 204.
    Если компания или отдел не найдены ответ со статусом 404.
    """
    await validator_check_object_exists(session, company_crud, object_slug=company_slug)
    department = await validator_check_object_exists(
        session, company_departments_crud, object_id=department_id
    )
    await company_departments_crud.remove(session, db_object=department)

    return status.HTTP_204_NO_CONTENT


@router.get(
    '/{company_slug}/employees',
    response_model=List[UserReadSchema],
    status_code=status.HTTP_200_OK,
    summary=Summary.TABIT_COMPANY_EMPLOYEES_LIST,
)
async def get_all_employees(
    company_slug: str,
    session: AsyncSession = Depends(get_async_session),
) -> List[UserReadSchema]:
    """
    Получает список всех сотрудников компании.
    Доступно только пользователю-админу компании.
    Проверяет существует ли компания и после, по id компании фильтрует сотрудников.
    В пути принимает 'company_slug' - значение `slug` компании.
    Параметры декоратора:
        path: URL-адрес, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: список с Pydantic-схемами.
        summary: краткое описание.
    Параметры функции:
        company_slug: значение `slug` компании.
        session: асинхронная сессия.
    Приуспешной транзакции вернет JSON, пример:
    [
      {
        "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
        "email": "user@example.com",
        "is_active": true,
        "is_superuser": false,
        "is_verified": false,
        "name": "string",
        "surname": "string",
        "patronymic": "string",
        "phone_number": "string",
        "birthday": "2025-02-18",
        "telegram_username": "string",
        "role": "string",
        "start_date_employment": "2025-02-18",
        "end_date_employment": "2025-02-18",
        "avatar_link": "string",
        "company_id": 0,
        "current_department_id": 0,
        "last_department_id": 0,
        "department_transition_date": "2025-02-18",
        "employee_position": "string",
        "created_at": "2025-02-18T14:58:43.453Z",
        "updated_at": "2025-02-18T14:58:43.453Z"
      }
    ]
    Если сотрудников нет, пустой список.
    """
    company = await validator_check_object_exists(session, company_crud, object_slug=company_slug)
    return await user_crud.get_multi(session, filters={'company_id': company.id})


@router.post(
    '/{company_slug}/employees',
    response_model=UserReadSchema,
    status_code=status.HTTP_201_CREATED,
    summary=Summary.TABIT_COMPANY_EMPLOYEES_CREATE,
)
async def create_company_employee(
    company_slug: str,
    create_data: UserCreateSchema,
    user_manager: BaseUserManager = Depends(get_user_manager),
    session: AsyncSession = Depends(get_async_session),
) -> UserReadSchema:
    """
    Создает сотрудника в компании.
    Доступно только пользователю-админу компании.
    Проверяет существует ли компания. Если нет, вернется ответ со статусом 404.
    В пути принимает 'company_slug' - значение `slug` компании.
    Параметры декоратора:
        path: URL-адрес, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: Pydantic-схема.
        summary: краткое описание.
    Параметры функции:
        company_slug: значение `slug` компании.
        create_data: данные введенные пользователем соответствующие схеме UserCreateSchema.
        user_manager: менеджер для пользователей.
        session: асинхронная сессия.
    При успешном выполнении вернет JSON, пример:
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "email": "user@example.com",
      "is_active": true,
      "is_superuser": false,
      "is_verified": false,
      "name": "string",
      "surname": "string",
      "patronymic": "string",
      "phone_number": "string",
      "birthday": "2025-02-18",
      "telegram_username": "string",
      "role": "string",
      "start_date_employment": "2025-02-18",
      "end_date_employment": "2025-02-18",
      "avatar_link": "string",
      "company_id": 0,
      "current_department_id": 0,
      "last_department_id": 0,
      "department_transition_date": "2025-02-18",
      "employee_position": "string",
      "created_at": "2025-02-18T16:16:09.210Z",
      "updated_at": "2025-02-18T16:16:09.210Z"
    }
    Если пользователь уже существует или пароль не соответствует требованиям ответ со статусом 400.
    """
    await validator_check_object_exists(session, company_crud, object_slug=company_slug)
    try:
        created_user = await user_manager.create(create_data)
    except UserAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_USER_ALREADY_EXISTS
        )
    except InvalidPasswordException:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=ERROR_INVALID_PASSWORD)
    return created_user


@router.post(
    '/{company_slug}/employees/import',
    status_code=status.HTTP_200_OK,
    summary=Summary.TABIT_COMPANY_EMPLOYEES_IMPORT,
)
async def import_employees(
    company_slug: str,
    session: AsyncSession = Depends(get_async_session),
):
    """
    Импортирует список сотрудников компании.
    Доступно только пользователю-админу компании.
    Проверяет существует ли компания и после, передает id компании для фильтрации списка.
    В пути принимает 'company_slug' - значение `slug` компании.
    Параметры декоратора:
        path: URL-адрес, который будет использоваться для этой операции.
        summary: краткое описание.
    Параметры функции:
        company_slug: значение `slug` компании.
        session: асинхронная сессия.
    Вернет файл .txt с данными сотрудников.
    """
    company = await validator_check_object_exists(session, company_crud, object_slug=company_slug)
    employees_list = await user_crud.get_multi(session, filters={'company_id': company.id})
    return await company_crud.get_import(objects_in=employees_list, file_name='employees_list')


@router.get(
    '/{company_slug}/employees/{uuid}',
    response_model=UserReadSchema,
    status_code=status.HTTP_200_OK,
    summary=Summary.TABIT_COMPANY_EMPLOYEE,
)
async def get_employee(
    company_slug: str,
    uuid: UUID,
    session: AsyncSession = Depends(get_async_session),
) -> UserReadSchema:
    """
    Получает информацию о сотруднике компании.
    Доступно только пользователю-админу компании.
    Проверяет существует ли компания и после, по uuid ссотрудника получает данные.
    В пути принимает 'company_slug' - значение `slug` компании и 'uuid'
     - значение `uuid` сотрудника.
    Параметры декоратора:
        path: URL-адрес, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: Pydantic-схема.
        summary: краткое описание.
    Параметры функции:
        company_slug: значение `slug` компании.
        uuid: значение `uuid` сотрудника.
        session: асинхронная сессия.
    При успешном запросе вернет JSON, пример:
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "email": "user@example.com",
      "is_active": true,
      "is_superuser": false,
      "is_verified": false,
      "name": "string",
      "surname": "string",
      "patronymic": "string",
      "phone_number": "string",
      "birthday": "2025-02-18",
      "telegram_username": "string",
      "role": "string",
      "start_date_employment": "2025-02-18",
      "end_date_employment": "2025-02-18",
      "avatar_link": "string",
      "company_id": 0,
      "current_department_id": 0,
      "last_department_id": 0,
      "department_transition_date": "2025-02-18",
      "employee_position": "string",
      "created_at": "2025-02-18T16:16:09.210Z",
      "updated_at": "2025-02-18T16:16:09.210Z"
    }
    Если сотрудник не найден ответ со статусом 404.
    """
    await validator_check_object_exists(session, company_crud, object_slug=company_slug)
    return await user_crud.get_or_404(session=session, obj_id=uuid)


@router.patch(
    '/{company_slug}/employees/{uuid}',
    response_model=UserReadSchema,
    status_code=status.HTTP_200_OK,
    summary=Summary.TABIT_COMPANY_EMPLOYEES_UPDATE,
)
async def update_company_employee(
    company_slug: str,
    uuid: UUID,
    object_in: CompanyEmployeeUpdateSchema,
    session: AsyncSession = Depends(get_async_session),
) -> UserReadSchema:
    """
    Обновляет данные сотрудника компании.
    Доступно только пользователю-админу компании.
    Проверяет существует ли компания и по uuid получает объект пользователя.
    В пути принимает 'company_slug' - значение `slug` компании и 'uuid'
     - значение `uuid` сотрудника.
    Параметры декоратора:
        path: URL-адрес, который будет использоваться для этой операции.
        response_model: тип, который будет использоваться для ответа: Pydantic-схема.
        summary: краткое описание.
    Параметры функции:
        company_slug: значение `slug` компании.
        uuid: `uuid` сотрудника.
        object_in: данные введенные пользователем соответствующие
         CompanyUserDepartmentUpdateSchema.
        session: асинхронная сессия.
    При успешной транзакции вернет JSON, пример:
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "email": "user@example.com",
      "is_active": true,
      "is_superuser": false,
      "is_verified": false,
      "name": "string",
      "surname": "string",
      "patronymic": "string",
      "phone_number": "string",
      "birthday": "2025-02-18",
      "telegram_username": "string",
      "role": "string",
      "start_date_employment": "2025-02-18",
      "end_date_employment": "2025-02-18",
      "avatar_link": "string",
      "company_id": 0,
      "current_department_id": 0,
      "last_department_id": 0,
      "department_transition_date": "2025-02-18",
      "employee_position": "string",
      "created_at": "2025-02-18T16:16:09.210Z",
      "updated_at": "2025-02-18T16:16:09.210Z"
    }
    Если сотрудник не найден ответ со статусом 404.
    """
    await validator_check_object_exists(session, company_crud, object_slug=company_slug)
    db_object = await user_crud.get_or_404(session=session, obj_id=uuid)
    return await user_crud.update(session=session, db_obj=db_object, obj_in=object_in)


@router.delete(
    '/{company_slug}/employees/{uuid}',
    status_code=status.HTTP_204_NO_CONTENT,
    summary=Summary.TABIT_COMPANY_EMPLOYEES_DELETE,
)
async def delete_company_employee(
    company_slug: str,
    uuid: UUID,
    user_manager: BaseUserManager = Depends(get_user_manager),
    session: AsyncSession = Depends(get_async_session),
):
    """
    Удаляет сотрудника компании.
    Доступно только пользователю-админу компании.
    Проверяет существует ли компания и сотрудник, и после передает объект для удаления.
    В пути принимает 'company_slug' - значение `slug` компании и 'uuid'
     - `uuid` сотрудника.
    Параметры декоратора:
        path: URL-адрес, который будет использоваться для этой операции.
        status_code: код статуса ответа.
        summary: краткое описание.
    Параметры функции:
        company_slug: значение `slug` компании.
        uuid: `uuid` сотрудника.
        user_manager: менеджер для пользователей.
        session: асинхронная сессия.
    При успешной транзакции вернет ответ со статусом 204.
    Если компания или отдел не найдены ответ со статусом 404.
    """
    await validator_check_object_exists(session, company_crud, object_slug=company_slug)
    try:
        user = await user_manager.get(uuid)
        await user_manager.delete(user)
    except UserNotExists:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=ERROR_USER_NOT_EXISTS)
    return status.HTTP_204_NO_CONTENT
