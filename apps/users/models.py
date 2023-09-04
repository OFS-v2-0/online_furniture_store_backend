"""Модели приложения users."""
from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.core.mail import send_mail
from django.db import models
from django.db.models import CharField, DateField, EmailField
from django.utils import timezone

from apps.users.managers import UserManager
from common.validators import validate_phone


class User(AbstractBaseUser, PermissionsMixin):
    """Настраиваемая модель пользователя."""

    email = EmailField('Email', unique=True)
    phone = CharField('Телефон', validators=[validate_phone], max_length=30, blank=True, null=True)
    first_name = CharField('Имя', max_length=30, blank=True, null=True)
    last_name = CharField('Фамилия', max_length=50, blank=True, null=True)
    birthday = DateField('День рождения', blank=True, null=True)
    date_joined = models.DateTimeField('Дата создания', default=timezone.now)
    is_staff = models.BooleanField('Статус пользователя', default=False)
    is_active = models.BooleanField('Активен', default=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def get_full_name(self):
        """Возвращает имя и фамилию."""
        full_name = f'{self.first_name} {self.last_name}'
        return full_name.strip()

    def get_short_name(self):
        """Возвращает имя пользователя."""
        return self.first_name

    def email_user(self, subject, message, from_email=None, **kwargs):
        """Высылает письмо пользователю."""
        send_mail(subject, message, from_email, [self.email], **kwargs)

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
