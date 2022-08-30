from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from faker import Faker

User = get_user_model()

fake = Faker()


class Command(BaseCommand):
    help = 'Generate 5 tests users'

    def handle(self, *args, **options):
        if not User.objects.filter(is_staff=False, is_developer=False).exists():
            for _ in range(5):
                user = User.objects.create(
                    first_name=fake.first_name(),
                    last_name=fake.last_name(),
                    email=fake.email(),
                )
                user.set_password('Zaqwerty123')
                user.save()
            self.stdout.write('Successfully generated users')
        else:
            self.stdout.write('Test users have already been generated before')
