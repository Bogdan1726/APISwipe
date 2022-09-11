from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from faker import Faker
from ads.models import Announcement
from housing.models import ResidentialComplex
from random import choice, randint, uniform

User = get_user_model()

fake = Faker('uk_UA')


class Command(BaseCommand):
    help = 'Generate test ads'
    user_list = [user.id for user in User.objects.filter(is_staff=False, is_developer=False)]
    residential_complex = [residential_complex.id for residential_complex in ResidentialComplex.objects.all()]

    def handle(self, *args, **options):
        if not Announcement.objects.all().exists():
            if self.user_list and self.residential_complex:
                for _ in range(25):
                    Announcement.objects.create(
                        address=fake.address(), description='Тестовое объявление', area=round(uniform(40, 100), 1),
                        area_kitchen=round(uniform(5, 20), 1), price=randint(20000, 60000), is_moderation_check=True,
                        creator_id=choice(self.user_list), residential_complex_id=choice(self.residential_complex))
                    Announcement.objects.create(
                        address=fake.address(), description='Тестовое объявление', area=round(uniform(40, 100), 1),
                        area_kitchen=round(uniform(5, 20), 1), price=randint(20000, 60000), is_moderation_check=True,
                        creator_id=choice(self.user_list),
                        purpose=choice(['Дом', 'Коммерческие помещения', 'Офисное помещение']))
                self.stdout.write(self.style.SUCCESS('Successfully generated announcements'))
            else:
                self.stdout.write(
                    'Insufficient data to run the command to start run '
                    '"generate_test_users and and generate_builder_users.py"'
                )
        else:
            self.stdout.write('Announcements have already been generated before')
