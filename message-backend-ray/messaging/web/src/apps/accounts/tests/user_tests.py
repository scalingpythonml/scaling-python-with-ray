from collections import namedtuple
from unittest import mock

from django.contrib.auth import get_user_model

import pytest


User = get_user_model()
UserStub = namedtuple("User", "username full_name email password")
test_user_data = UserStub(
    "farts",
    "test-fullname",
    "somewhere@test.com",
    "&Aqa&5y!8wMpWGUC8gJBWqpxjE8p8nT7XDB2xwZA4$KEb9Nd2&&kv42Y*!Vg4kHE8fPw5k2PwBSD$y*bqzEmXdH8fe#F4#BdY5x",
)


@pytest.fixture
def user():
    assert not User.objects.count()
    user = User.objects.create_user(
        username=test_user_data.username,
        full_name=test_user_data.full_name,
        email=test_user_data.email,
    )
    user.is_active = True
    user.set_password(test_user_data.password)
    user.save()
    assert User.objects.count() == 1
    yield user
    user.delete()
    assert not User.objects.count()


@pytest.fixture
def superuser():
    assert not User.objects.count()
    user = User.objects.create_superuser(
        username=test_user_data.username,
        email=test_user_data.email,
        password=test_user_data.password,
        full_name=test_user_data.full_name,
    )
    assert User.objects.count() == 1
    # Check user
    assert user.is_active
    assert user.is_staff
    assert user.is_superuser
    yield user
    user.delete()
    assert not User.objects.count()


@pytest.fixture
def inactiveuser():
    assert not User.objects.count()
    user = User.objects.create_inactive_user(
        username=test_user_data.username,
        email=test_user_data.email,
        password=test_user_data.password,
        full_name=test_user_data.full_name,
    )
    assert User.objects.count() == 1
    # Check user
    assert not user.is_active
    assert not user.is_staff
    assert not user.is_superuser
    yield user
    user.delete()
    assert not User.objects.count()


@pytest.fixture
def activeuser():
    assert not User.objects.count()
    user = User.objects.create_user(
        username=test_user_data.username,
        email=test_user_data.email,
        password=test_user_data.password,
        full_name=test_user_data.full_name,
    )
    assert User.objects.count() == 1
    # Check user
    assert user.is_active
    assert not user.is_staff
    assert not user.is_superuser
    yield user
    user.delete()
    assert not User.objects.count()


@pytest.mark.django_db
def test_user(user):
    pass


@pytest.mark.django_db
def test_superuser(superuser):
    pass


@pytest.mark.django_db
def test_inactiveuser(inactiveuser):
    pass


@pytest.mark.django_db
def test_activeuser(activeuser):
    pass
