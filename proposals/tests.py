import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import RefreshToken
from proposals.models import Client, Proposal
from proposals.serializers import ClientSerializer, ProposalSerializer

User = get_user_model()

@pytest.fixture
def user():
    """
    Create a test user.
    """
    return User.objects.create_user(
        name="Test User",
        email="test@example.com",
        password="secure123"
    )

@pytest.fixture
def other_user():
    """
    Create a second test user.
    """
    return User.objects.create_user(
        name="Other User",
        email="other@example.com",
        password="secure123"
    )

@pytest.fixture
def client_instance(user):
    """
    Create a test client.
    """
    return Client.objects.create(
        company_name="Test Client",
        email="client@example.com",
        phone_number="+12025550123",
        added_by=user
    )

@pytest.fixture
def api_client():
    """
    Provide an API client for making requests.
    """
    return APIClient()

@pytest.mark.django_db
class TestClientSerializer:
    def test_valid_client(self, user):
        data = {
            "company_name": "Acme Corp",
            "email": "contact@acme.com",
            "phone_number": "+12025550123"
        }
        serializer = ClientSerializer(data=data, context={'request': type('Request', (), {'user': user})()})
        assert serializer.is_valid()
        client = serializer.save()
        assert client.added_by == user
        assert client.company_name == "Acme Corp"

    def test_missing_contact_fields(self):
        data = {
            "company_name": "Acme Corp"
        }
        serializer = ClientSerializer(data=data)
        assert not serializer.is_valid()
        assert "Either phone_number or email must be provided." in str(serializer.errors)

@pytest.mark.django_db
class TestProposalSerializer:
    def test_valid_proposal(self, user, client_instance):
        data = {
            "client_id": client_instance.id,
            "title": "Website Redesign",
            "description": "Redesign client website."
        }
        serializer = ProposalSerializer(data=data, context={'request': type('Request', (), {'user': user})()})
        assert serializer.is_valid()
        proposal = serializer.save()
        assert proposal.created_by == user
        assert proposal.client == client_instance
        assert proposal.title == "Website Redesign"

    def test_invalid_client_id(self, user):
        data = {
            "client_id": 999,
            "title": "Website Redesign",
            "description": "Redesign client website."
        }
        serializer = ProposalSerializer(data=data, context={'request': type('Request', (), {'user': user})()})
        assert not serializer.is_valid()
        assert "client_id" in serializer.errors

@pytest.mark.django_db
class TestClientAPI:
    def setup_method(self):
        self.client = APIClient()

    def test_create_client_authenticated(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        url = reverse('proposals:client-list-create')
        data = {
            "company_name": "Acme Corp",
            "email": "contact@acme.com",
            "phone_number": "+12025550123"
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['company_name'] == "Acme Corp"
        assert response.data['added_by']['id'] == user.id

    def test_create_client_unauthenticated(self):
        url = reverse('proposals:client-list-create')
        data = {
            "company_name": "Acme Corp",
            "email": "contact@acme.com"
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_list_clients(self, user, client_instance):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        url = reverse('proposals:client-list-create')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['company_name'] == "Test Client"

    def test_list_clients_other_user(self, user, other_user, client_instance):
        refresh = RefreshToken.for_user(other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        url = reverse('proposals:client-list-create')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0  # Other user sees no clients

    def test_retrieve_client(self, user, client_instance):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        url = reverse('proposals:client-detail', kwargs={'pk': client_instance.id})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['company_name'] == "Test Client"

    def test_retrieve_client_unauthorized(self, user, other_user, client_instance):
        refresh = RefreshToken.for_user(other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        url = reverse('proposals:client-detail', kwargs={'pk': client_instance.id})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_client(self, user, client_instance):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        url = reverse('proposals:client-detail', kwargs={'pk': client_instance.id})
        data = {
            "company_name": "Updated Client",
            "email": "updated@example.com"
        }
        response = self.client.put(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['company_name'] == "Updated Client"

    def test_delete_client(self, user, client_instance):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        url = reverse('proposals:client-detail', kwargs={'pk': client_instance.id})
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Client.objects.count() == 0

@pytest.mark.django_db
class TestProposalAPI:
    def setup_method(self):
        self.client = APIClient()

    def test_create_proposal_authenticated(self, user, client_instance):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        url = reverse('proposals:proposal-list-create')
        data = {
            "client_id": client_instance.id,
            "title": "Website Redesign",
            "description": "Redesign client website."
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == status.HTTP_201_CREATED
        assert response.data['title'] == "Website Redesign"
        assert response.data['created_by']['id'] == user.id
        assert response.data['client']['id'] == client_instance.id

    def test_create_proposal_unauthenticated(self):
        url = reverse('proposals:proposal-list-create')
        data = {
            "client_id": 1,
            "title": "Website Redesign",
            "description": "Redesign client website."
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_create_proposal_invalid_client(self, user):
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        url = reverse('proposals:proposal-list-create')
        data = {
            "client_id": 999,
            "title": "Website Redesign",
            "description": "Redesign client website."
        }
        response = self.client.post(url, data, format='json')
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "client_id" in response.data

    def test_list_proposals(self, user, client_instance):
        Proposal.objects.create(
            client=client_instance,
            title="Test Proposal",
            description="Test description",
            created_by=user
        )
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        url = reverse('proposals:proposal-list-create')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['title'] == "Test Proposal"

    def test_list_proposals_other_user(self, user, other_user, client_instance):
        Proposal.objects.create(
            client=client_instance,
            title="Test Proposal",
            description="Test description",
            created_by=user
        )
        refresh = RefreshToken.for_user(other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        url = reverse('proposals:proposal-list-create')
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0  # Other user sees no proposals

    def test_retrieve_proposal(self, user, client_instance):
        proposal = Proposal.objects.create(
            client=client_instance,
            title="Test Proposal",
            description="Test description",
            created_by=user
        )
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        url = reverse('proposals:proposal-detail', kwargs={'pk': proposal.id})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == "Test Proposal"

    def test_retrieve_proposal_unauthorized(self, user, other_user, client_instance):
        proposal = Proposal.objects.create(
            client=client_instance,
            title="Test Proposal",
            description="Test description",
            created_by=user
        )
        refresh = RefreshToken.for_user(other_user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        url = reverse('proposals:proposal-detail', kwargs={'pk': proposal.id})
        response = self.client.get(url)
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_proposal(self, user, client_instance):
        proposal = Proposal.objects.create(
            client=client_instance,
            title="Test Proposal",
            description="Test description",
            created_by=user
        )
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        url = reverse('proposals:proposal-detail', kwargs={'pk': proposal.id})
        data = {
            "client_id": client_instance.id,
            "title": "Updated Proposal",
            "description": "Updated description."
        }
        response = self.client.put(url, data, format='json')
        assert response.status_code == status.HTTP_200_OK
        assert response.data['title'] == "Updated Proposal"

    def test_delete_proposal(self, user, client_instance):
        proposal = Proposal.objects.create(
            client=client_instance,
            title="Test Proposal",
            description="Test description",
            created_by=user
        )
        refresh = RefreshToken.for_user(user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {str(refresh.access_token)}')
        url = reverse('proposals:proposal-detail', kwargs={'pk': proposal.id})
        response = self.client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert Proposal.objects.count() == 0