import os

from dotenv import load_dotenv
from sqladmin.authentication import AuthenticationBackend
from starlette.requests import Request
from starlette.responses import RedirectResponse

load_dotenv()

SUPERUSER_EMAIL = os.getenv('FIRST_SUPERUSER_EMAIL')
SUPERUSER_PASSWORD = os.getenv('FIRST_SUPERUSER_PASSWORD')


class AdminAuth(AuthenticationBackend):
    """Авторизация для админки по email и паролю"""

    async def login(self, request: Request) -> bool:
        form = await request.form()
        email, password = form.get('username'), form.get('password')
        if email == SUPERUSER_EMAIL and password == SUPERUSER_PASSWORD:
            request.session.update({'authenticated': True, 'email': email})
            return True
        return False

    async def logout(self, request: Request) -> bool:
        request.session.clear()
        return True

    async def authenticate(self, request: Request):
        if request.session.get('authenticated'):
            return True
        return RedirectResponse(request.url_for('admin:login'), status_code=302)
