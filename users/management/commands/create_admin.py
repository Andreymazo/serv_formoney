from django.core.management import BaseCommand

from users.models import CustomUser


class Command(BaseCommand):

    def handle(self, *args, **options):
        # names_emails = {'Георгий':'george@mom.ru', 'Максим':'maxim@mom.ru', 'Вася':'vasia@mom.ru'}
        # for i, ii in names_emails.items():
            customuser = CustomUser.objects.create_user(
                email='boriss_rabotnik@nha.com',
                password='qwerty',
                phone_number='71234561234',

            )
            # customuser.set_password('qwert123asd')
            # customuser.save()
