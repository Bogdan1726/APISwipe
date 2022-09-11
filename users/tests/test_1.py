from allauth.account.models import EmailAddress
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient, APITestCase
from users.models import Notary, Filter

# Create your tests here.

User = get_user_model()
client = APIClient()


class RegistrationTestCase(APITestCase):

    def test_registration(self):
        url = reverse('users:rest_register')
        data = {
            "email": "user@example.com",
            "password1": "Zaqwerty123",
            "password2": "Zaqwerty123",
            "first_name": "Test-user",
            "last_name": "Test-user"
        }
        response = self.client.post(url, data=data)
        assert response.status_code == 201


class LoginUserTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(
            email='user@example.com',
            first_name='Test-user',
            last_name='Test-user',
        )
        self.user.set_password("Zaqwerty123")
        self.user.save()
        EmailAddress.objects.create(
            user=self.user,
            email=self.user.email,
            verified=True,
            primary=True
        )

    def test_login(self):
        url = reverse('users:rest_login')
        data = {
            "email": "user@example.com",
            "password": "Zaqwerty123"
        }
        response = self.client.post(url, data=data)
        assert response.status_code == 200


class BaseTestCase(APITestCase):

    def setUp(self):
        self.user = User.objects.create(
            email='admin@admin.com',
            first_name='Test',
            last_name='Test',
            is_staff=True
        )
        self.user.set_password('Zaqwerty123')
        self.user.save()
        self.client.force_authenticate(user=self.user)


class NotaryTestCase(BaseTestCase):

    def test_create(self):
        url = reverse('users:notary-list')
        valid_data = {
            'first_name': 'Test',
            'last_name': 'Test',
            'phone': '+380933252525',
            'email': 'notary@test.com'
        }
        invalid_data = {
            'first_name': 'Test 2',
            'last_name': 'Test 2',
            'phone': '+380000000000',
            'email': 'notary@test..com'
        }
        valid_response = self.client.post(url, data=valid_data)
        invalid_response = self.client.post(url, data=invalid_data)
        if self.user.is_staff:
            assert invalid_response.status_code == 400
            assert valid_response.status_code == 201
        else:
            assert invalid_response.status_code == 403
            assert valid_response.status_code == 403

    def test_update(self):
        Notary.objects.create(
            id=1,
            first_name='Test notary',
            last_name='Test notary',
            phone='+380933699636',
            email='notary_test@test.com'
        )
        url = reverse('users:notary-detail', kwargs={'pk': 1})
        data = {
            'first_name': 'Testing',
            'last_name': 'Testing',
            'phone': '+380955455822',
            'email': 'notary5@test.com'
        }
        response = self.client.put(url, data=data)
        if self.user.is_staff:
            assert response.status_code == 200
        else:
            assert response.status_code == 403

    def test_list(self):
        url = reverse('users:notary-list')
        response = self.client.get(url)
        assert response.status_code == 200


class FilterTestCase(BaseTestCase):

    def test_create(self):
        url = reverse('users:user-filter-list')
        data = {
            "status_house": True,
            "district": "test",
            "microdistrict": "test",
            "rooms": 5,
            "price_start": 25000,
            "price_end": 40000,
            "area_start": 20,
            "area_end": 50,
            "type_housing": "Все",
            "purpose": "Дом",
            "payment_options": "Ипотека",
            "state": "Черновая"
        }
        data_unique = {
            "status_house": True,
            "district": "test",
            "microdistrict": "test",
            "rooms": 5,
            "price_start": 25000,
            "price_end": 40000,
            "area_start": 20,
            "area_end": 50,
            "type_housing": "Все",
            "purpose": "Дом",
            "payment_options": "Ипотека",
            "state": "Черновая"
        }
        data_invalid = {
            "status_house": True,
            "district": "test",
            "microdistrict": "test",
            "rooms": 5,
            "price_start": 45000,
            "price_end": 40000,
            "area_start": 60,
            "area_end": 50,
            "type_housing": "Новостройки",
            "purpose": "Дом",
            "payment_options": "Ипотека",
            "state": "Черновая"
        }

        response = self.client.post(url, data=data)
        response_data_unique = self.client.post(url, data=data_unique)
        response_invalid = self.client.post(url, data=data_invalid)
        assert response_data_unique.status_code == 400
        assert response_invalid.status_code == 400
        assert response.status_code == 201

    def test_update(self):
        user = User.objects.create(
            email='test@test.com',
            first_name='Test',
            last_name='Test',
        )
        user.set_password('Zaqwerty123')
        user.save()
        Filter.objects.create(
            id=1,
            status_house=True,
            district="test",
            microdistrict="test",
            rooms=5,
            price_start=25000,
            price_end=40000,
            area_start=20,
            area_end=50,
            type_housing="Все",
            purpose="Дом",
            payment_options="Ипотека",
            state="Черновая",
            user=user
        )
        url = reverse('users:user-filter-detail', kwargs={'pk': 1})
        data = {
            "status_house": True,
            "district": "test",
            "microdistrict": "test",
            "rooms": 5,
            "price_start": 25000,
            "price_end": 40000,
            "area_start": 20,
            "area_end": 50,
            "type_housing": "Все",
            "purpose": "Дом",
            "payment_options": "Ипотека",
            "state": "Черновая"
        }
        response = self.client.put(url, data=data)
        assert response.status_code == 404

    def test_list(self):
        url = reverse('users:user-filter-list')
        response = self.client.get(url)
        assert response.status_code == 200
