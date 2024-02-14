import pytest
from rest_framework.test import APIClient
from rest_framework_simplejwt.tokens import RefreshToken


@pytest.fixture
def user(django_user_model):
    return django_user_model.objects.create_user(
        username='TestUser',
        password='1234567'
    )


@pytest.fixture
def user_2(django_user_model):
    return django_user_model.objects.create_user(
        username='TestUser_2',
        password='1234567'
    )


@pytest.fixture
def token(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@pytest.fixture
def user_client(token):
    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION=f'Bearer {token["access"]}'
    )
    return client


@pytest.fixture
def token_admin(admin_user):
    refresh = RefreshToken.for_user(admin_user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


@pytest.fixture
def admin(token_admin):
    client = APIClient()
    client.credentials(
        HTTP_AUTHORIZATION=f'Bearer {token_admin["access"]}'
    )
    return client
