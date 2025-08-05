import re
from django.db import models
from django.contrib.auth.base_user import AbstractBaseUser
from django.core.exceptions import ValidationError
from users.managers import CustomUserManager
from config.constants import (
    
    MAX_LEN_EMAIL,
    MAX_LEN_PHONE_NUMBER,
    MIN_LEN_EMAIL
)
from django.core.validators import RegexValidator, MinLengthValidator
from django.utils.translation import gettext_lazy as _


NULLABLE = {'blank': True, 'null': True}
phone_validator = RegexValidator(
    r"^(\+?7|\+?\d{3}?)?(?:\(?(\d{3})\)?|(\d{3}))[-.\s]?((\d{3})|(\d{4}))[-.\s]?(\d{4})$"
)

def validate_name(value):
    # Проверка на наличие только букв или букв и цифр
    if not re.match(r'^[a-zA-Zа-яА-Я0-9]+$', value):
        raise ValidationError(_("Имя пользователя должно содержать только буквы или буквы и цифры"))

    # Проверка на отсутствие имени пользователя, состоящего только из цифр
    if re.match(r'^\d+$', value):
        raise ValidationError(_("Имя пользователя не может состоять только из цифр"))


class CustomUser(AbstractBaseUser):  # , PermissionsMixin):
    
    email = models.EmailField(_("Почта"),
                              max_length=MAX_LEN_EMAIL,
                              unique=True,
                              help_text=_("Введите email, не более 50 символов"),
                              )
    phone_number = models.CharField(_("Номер телефона"), 
                                    max_length=MAX_LEN_PHONE_NUMBER, 
                                    unique=True, 
                                    validators=[phone_validator], blank=False)
    ban = models.BooleanField(_("Бан"), default=False)
    full_name = models.CharField(max_length=30, **NULLABLE)
    is_staff = models.BooleanField(default=False)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)
    date_joined = models.DateTimeField(_("Время создания"), auto_now_add=True)
    changed_at = models.DateTimeField(_("Время изменения"), auto_now=True)

    valid_sign = models.CharField(**NULLABLE)
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = [phone_number, email]
    objects = CustomUserManager()

    def __str__(self):
        return f"{self.id}: {self.email}"

    
    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    @staticmethod
    def has_perm(perm, obj=None, **kwargs):
        return True

    @staticmethod
    def has_module_perms(app_label, **kwargs):
        return True

    