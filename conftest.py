import pytest


def create_user(username):
    """A Django common user"""
    email = username + '@example.com'
    password = 'password'

    from django.contrib.auth import get_user_model
    User = get_user_model()

    try:
        User.objects.get(email=email)
    except User.DoesNotExist:
        user = User.objects.create_user(username, email, password)

        if username == 'admin':
            user.is_staff = True
            user.is_superuser = True
        user.save()
    return user


@pytest.fixture()
def admin_user(db):
    """A Django test admin user"""
    user = create_user('admin')
    return user


@pytest.fixture()
def admin_client(db):
    """A Django admin user"""
    from django.test.client import Client

    user = create_user('admin')

    client = Client()
    client.login(username=user.username, password=user.password)
    return client


@pytest.fixture()
def user(db):
    create_user('common')
