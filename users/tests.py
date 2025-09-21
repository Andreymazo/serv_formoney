from django.test import TestCase
from django.contrib.auth import get_user_model
from config import settings


User = get_user_model()


class TestCustomuser(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='testuser@test.pl', password = 'testpass', phone_number='79219321211')

    def test_user(self):
        self.assertEqual(self.user.email, 'testuser@test.pl')
        self.assertEqual(self.user.phone_number, '79219321211')

