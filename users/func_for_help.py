import random
from config.constants import LEN_CODE
from config import settings
from django.core.mail import send_mail

def get_random_code():
    """Получить временный код из 5-ти цифр."""
    return "".join([str(random.randint(0, 9)) for _ in range(LEN_CODE)])


def send_code_by_email(email, code):
    """Отправить код на электронную почту."""
    message = f"Код: {code}"
    send_mail(
        subject="Временный код доступа",
        message=message,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email],
        fail_silently=False,
    )

    return message
