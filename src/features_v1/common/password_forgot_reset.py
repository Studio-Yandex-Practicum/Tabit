import logging

from fastapi import APIRouter

from .password_change_mixin import PasswordChangeMixin
from .password_forgot_mixin import PasswordForgotMixin
from .password_reset_mixin import PasswordResetMixin

logger = logging.getLogger(__name__)


class PasswordForgotResetMixin(PasswordForgotMixin, PasswordResetMixin, PasswordChangeMixin):
    """Общий миксин для восстановления, сброса и смены пароля."""

    def create_password_forgot_reset_routes(
        self,
        router: APIRouter,
        crud,
        current_user_dependency,
        user_type_name: str,
        prefix: str = '',
    ):
        self.create_forgot_route(router, crud, user_type_name, prefix)
        self.create_reset_routes(router, crud, user_type_name, prefix)
        self.create_change_route(router, crud, current_user_dependency, user_type_name, prefix)
