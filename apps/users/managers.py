"""User manager с описанием с реализацией создания различных пользователей."""
from django.contrib.auth.models import UserManager as DjangoUserManager
from django.utils.crypto import get_random_string

from config.settings.base import SITE_EMAIL, SITE_URL


class UserManager(DjangoUserManager):
    """Индивидуальная модель пользователя."""

    def _create_user(self, email: str, password: str | None, **extra_fields):
        """Создание пользователя с помощью email."""
        if not email:
            raise ValueError('Необходим email.')
        if password is None:
            password = get_random_string(length=12)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        user.email_user(
            'Регистрация на сайте',
            message=f'Ваш email успешно зарегистрирован на сайте OFS '
            f'{SITE_URL}.\n'
            f'Ваш пароль: {password}.\n'
            f'Вы можете сменить пароль в личном кабинете.',
            from_email=SITE_EMAIL,
        )
        return user

    def create_user(self, email: str, password: str | None = None, **extra_fields):
        """Создание пользователя с помощью email."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email: str, password: str | None = None, **extra_fields):
        """Создание суперпользователя с помощью email."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)
