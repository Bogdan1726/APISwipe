from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase

# Create your tests here.
from ads.models import Announcement

User = get_user_model()
client = APIClient()


class BaseTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(
            email='admin@admin.com',
            first_name='Test',
            last_name='Test',
        )
        self.user.set_password('Zaqwerty123')
        self.user.save()
        self.client.force_authenticate(user=self.user)


class AnnouncementTestCase(BaseTestCase):

    def test_get_announcement_list(self):
        url = reverse('ads:announcement-feed-list')
        response = self.client.get(url)
        assert response.status_code == 200




