from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase


# Create your tests here.

User = get_user_model()
client = APIClient()


class IsUserTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(
            email='admin@admin.com',
            first_name='Test',
            last_name='Test',
        )
        self.user.set_password('Zaqwerty123')
        self.user.save()
        self.client.force_authenticate(user=self.user)


class IsDeveloperTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(
            email='admin@admin.com',
            first_name='Test',
            last_name='Test',
            is_developer=True
        )
        self.user.set_password('Zaqwerty123')
        self.user.save()
        self.client.force_authenticate(user=self.user)


class ResidentialComplexTestCase(IsDeveloperTestCase):

    def test_get_my_complex(self):
        url = '/housing/complex/get_my_complex/'
        response = self.client.get(url)
        if self.user.is_developer:
            assert response.status_code == 200
        else:
            assert response.status_code == 404

    def test_get_complex(self):
        url = reverse('housing:residential-complex-detail', kwargs={'pk': 1})
        response = self.client.get(url)
        if self.user.is_developer:
            assert response.status_code == 200
        else:
            assert response.status_code == 404

    def test_update_complex(self):
        url = reverse('housing:residential-complex-detail', kwargs={'pk': 3})
        data = {
            "name": "Test",
            "description": "Test",
            "is_commissioning": "true",
            "address": "test",
            "map_lat": "46.37668422515867",
            "map_lon": "30.721478800598362",
            "distance": 2500,
            "ceiling_height": 2.5,
            "gas": "true",
            "status": "Квартиры",
            "type_house": "Многоквартирный",
            "class_house": "Элитный",
            "technology": "Монолитный каркас с керамзитно-блочным заполнением",
            "territory": "Закрытая охраняемая",
            "communal_payments": "Платежи",
            "heating": "Центральное",
            "sewerage": "Центральная",
            "water_service": "Центральное",
            "sales_department_contact": {
                "first_name": "Юля",
                "last_name": "Тест",
                "phone": "+380955554433",
                "email": "user@example.com"
            },
            "benefits": {
                "playground": "true",
                "sportsground": "true",
                "parking": "true",
                "territory_protected": "true"
            },
            "registration_and_payment": {
                "formalization": "Юстиция",
                "payment_options": "Ипотека",
                "purpose": "Жилое помещение",
                "contract_sum": "Неполная"
            },
            "images_order": [
            ],
            "images": [
            ]
        }
        response = self.client.put(url, data=data, format='json')
        assert response.status_code == 200

