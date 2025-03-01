from fastapi import APIRouter, BackgroundTasks, HTTPException, status
from fastapi_mail import FastMail, MessageSchema, MessageType
from starlette.responses import JSONResponse

from src.config import email_settings
from src.utils.email_service.email_schema import EmailCreateSchema

router = APIRouter()


@router.post('/email')
async def simple_send_email(
    background_tasks: BackgroundTasks,
    email: EmailCreateSchema,
) -> JSONResponse:
    """
    Функция отправки электронного письма.
    Параметры функции:
    1) background_tasks: объект класса BackgroundTasks
       для отправки электронных писем в фоновом режиме;
    2) email: pydantic схема для создания и оптравки электронного письма;
    Варианты возвращаемых значений:
    - Объект класса JSONResponse;
    - Исключение HTTPException при ошибки отправки письма.
    """
    try:
        message = MessageSchema(
            subject=email.subject_email,
            recipients=email.model_dump().get('email'),
            template_body=email.model_dump().get('message'),
            subtype=MessageType.html,
        )
        fm = FastMail(email_settings.config_email)
        background_tasks.add_task(fm.send_message, message)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'{e}')
    return JSONResponse(status_code=200, content={'Статус': 'Электронное письмо отправлено!'})
