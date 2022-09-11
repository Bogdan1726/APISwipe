from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from faker import Faker

User = get_user_model()

fake = Faker('ru_RU')


class Command(BaseCommand):
    help = 'Generate 5 tests users'

    def handle(self, *args, **options):
        if not User.objects.filter(is_superuser=True).exists():
            super_user = User.objects.create(
                first_name='Admin',
                last_name='Admin',
                email='admin@admin.com',
                is_superuser=True
            )
            super_user.set_password('Zaqwerty123')
            EmailAddress.objects.create(
                user=super_user,
                email=super_user.email,
                verified=True,
                primary=True
            )
            super_user.save()
            self.stdout.write('Successfully create superusers')
        else:
            self.stdout.write('Superuser is already!')
