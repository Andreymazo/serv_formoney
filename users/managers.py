import re
from django.contrib.auth.base_user import BaseUserManager
from django.shortcuts import redirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


"""шаблон для Российских номеров типа +79219213232"""

def validate_phone_number(phone_number):
    pattern = r"^(\+?7|\+?\d{3}?)?(?:\(?(\d{3})\)?|(\d{3}))[-.\s]?((\d{3})|(\d{4}))[-.\s]?(\d{4})$"
    """
    Проверяет, соответствует ли номер телефона заданному шаблону.

    :param phone_number: Строка с номером телефона для проверки
    :return: Ничего не возвращает, если номер корректен, иначе вызывает ValueError
"""
    
    if not re.fullmatch(pattern, phone_number):
        raise ValueError(_('The Phone number must be proper'))
    else:
        return re.fullmatch(pattern, phone_number)


class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """

    def create_user(self, email, password, phone_number, **extra_fields):
        """
        Create and save a User with the given email, phone_numer and password.
        """
       
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
    
        if validate_phone_number(phone_number=phone_number) == None:
            print('if we here???')
            return redirect(reverse('users:login'))
        
        user = self.model(email=email, phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)
