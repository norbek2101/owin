import pytest
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from rest_framework import status
from rest_framework.test import APIClient
from django.urls import reverse
from .models import User
from rest_framework_simplejwt.tokens import RefreshToken

@pytest.mark.django_db
class TestUserManager:
    def test_create_user_with_email(self):
        user = User.objects.create_user(
            name="John Doe",
            email="john@example.com",
            password="secure123"
        )
        assert user.name == "John Doe"
        assert user.email == "john@example.com"
        assert user.phone_number is None
        assert user.check_password("secure123")
        assert user.is_active
        assert not user.is_staff
        assert not user.is_superuser

    def test_create_user_with_phone(self):
        user = User.objects.create_user(
            name="Jane Doe",
            phone_number="+12025550123",
            password="secure123"
        )
        assert user.name == "Jane Doe"
        assert user.phone_number == "+12025550123"
        assert user.email is None
        assert user.check_password("secure123")

    def test_create_user_missing_name(self):
        with pytest.raises(ValueError, match="The Name field is required"):
            User.objects.create_user(
                name="",
                email="john@example.com",
                password="secure123"
            )

    def test_create_user_missing_email_and_phone(self):
        with pytest.raises(ValueError, match="Either a phone number or email must be provided"):
            User.objects.create_user(
                name="John Doe",
                password="secure123"
            )

    def test_create_superuser(self):
        user = User.objects.create_superuser(
            name="Admin User",
            email="admin@example.com",
            password="admin123"
        )
        assert user.name == "Admin User"
        assert user.email == "admin@example.com"
        assert user.check_password("admin123")
        assert user.is_staff
        assert user.is_superuser

    def test_create_superuser_not_staff(self):
        with pytest.raises(ValueError, match="Superuser must have is_staff=True"):
            User.objects.create_superuser(
                name="Admin User",
                email="admin@example.com",
                password="admin123",
                is_staff=False
            )

    def test_get_by_identifier_email(self):
        User.objects.create_user(
            name="John Doe",
            email="john@example.com",
            password="secure123"
        )
        user = User.objects.get_by_identifier("john@example.com")
        assert user.name == "John Doe"
        assert user.email == "john@example.com"

    def test_get_by_identifier_phone(self):
        User.objects.create_user(
            name="Jane Doe",
            phone_number="+12025550123",
            password="secure123"
        )
        user = User.objects.get_by_identifier("+12025550123")
        assert user.name == "Jane Doe"
        assert user.phone_number == "+12025550123"

    def test_get_by_identifier_nonexistent(self):
        with pytest.raises(User.DoesNotExist):
            User.objects.get_by_identifier("nonexistent@example.com")

@pytest.mark.django_db
class TestCustomAuthBackend:
    def test_authenticate_with_email(self):
        User.objects.create_user(
            name="John Doe",
            email="john@example.com",
            password="secure123"
        )
        user = authenticate(username="john@example.com", password="secure123")
        assert user is not None
        assert user.email == "john@example.com"

    def test_authenticate_with_phone(self):
        User.objects.create_user(
            name="Jane Doe",
            phone_number="+12025550123",
            password="secure123"
        )
        user = authenticate(username="+12025550123", password="secure123")
        assert user is not None
        assert user.phone_number == "+12025550123"

    def test_authenticate_invalid_credentials(self):
        User.objects.create_user(
            name="John Doe",
            email="john@example.com",
            password="secure123"
        )
        user = authenticate(username="john@example.com", password="wrongpass")
        assert user is None

    def test_authenticate_nonexistent_user(self):
        user = authenticate(username="nonexistent@example.com", password="secure123")
        assert user is None

@pytest.mark.django_db
class TestAuthAPI:
    def setup_method(self):
        self.client = APIClient()

    def test_register_with_email(self):
        url = reverse('register')
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "secure123"
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['name'] == "John Doe"
        assert response.data['user']['email'] == "john@example.com"

    def test_register_with_phone(self):
        url = reverse('register')
        data = {
            "name": "Jane Doe",
            "phone_number": "+12025550123",
            "password": "secure123"
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['name'] == "Jane Doe"
        assert response.data['user']['phone_number'] == "+12025550123"

    def test_register_missing_name(self):
        url = reverse('register')
        data = {
            "email": "john@example.com",
            "password": "secure123"
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "name" in response.data

    def test_register_missing_email_and_phone(self):
        url = reverse('register')
        data = {
            "name": "John Doe",
            "password": "secure123"
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "Either phone_number or email must be provided" in str(response.data)

    def test_register_duplicate_email(self):
        User.objects.create_user(
            name="Existing User",
            email="john@example.com",
            password="secure123"
        )
        url = reverse('register')
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "password": "secure123"
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "email" in response.data
        assert response.data["email"] == "A user with that email already exists."

    def test_register_duplicate_phone(self):
        User.objects.create_user(
            name="Existing User",
            phone_number="+12025550123",
            password="secure123"
        )
        url = reverse('register')
        data = {
            "name": "Jane Doe",
            "phone_number": "+12025550123",
            "password": "secure123"
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "phone_number" in response.data
        assert response.data["phone_number"] == "A user with that phone number already exists."

    def test_login_with_email(self):
        User.objects.create_user(
            name="John Doe",
            email="john@example.com",
            password="secure123"
        )
        url = reverse('login')
        data = {
            "identifier": "john@example.com",
            "password": "secure123"
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['email'] == "john@example.com"

    def test_login_with_phone(self):
        User.objects.create_user(
            name="Jane Doe",
            phone_number="+12025550123",
            password="secure123"
        )
        url = reverse('login')
        data = {
            "identifier": "+12025550123",
            "password": "secure123"
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert 'access' in response.data
        assert 'refresh' in response.data
        assert response.data['user']['phone_number'] == "+12025550123"

    def test_login_invalid_credentials(self):
        User.objects.create_user(
            name="John Doe",
            email="john@example.com",
            password="secure123"
        )
        url = reverse('login')
        data = {
            "identifier": "john@example.com",
            "password": "wrongpass"
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "error" in response.data

    def test_logout(self):
        user = User.objects.create_user(
            name="John Doe",
            email="john@example.com",
            password="secure123"
        )
        refresh = RefreshToken.for_user(user)
        url = reverse('logout')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        response = self.client.post(url, {'refresh': str(refresh)}, format='json')
        assert response.status_code == status.HTTP_205_RESET_CONTENT

    def test_logout_invalid_token(self):
        user = User.objects.create_user(
            name="John Doe",
            email="john@example.com",
            password="secure123"
        )
        url = reverse('logout')
        self.client.credentials(HTTP_AUTHORIZATION='Bearer invalid_token')
        response = self.client.post(url, {'refresh': 'invalid_token'}, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_profile_authenticated(self):
        user = User.objects.create_user(
            name="John Doe",
            email="john@example.com",
            password="secure123"
        )
        refresh = RefreshToken.for_user(user)
        url = reverse('profile')
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['name'] == "John Doe"
        assert response.data['email'] == "john@example.com"

    def test_profile_unauthenticated(self):
        url = reverse('profile')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED