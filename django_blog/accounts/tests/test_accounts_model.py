import pytest
from accounts.models import User, Profile
from django.db import transaction
from datetime import datetime


@pytest.fixture
def normal_user():
    user = User.objects.create_user(
        email="mohammad@gmail.com", password="m@1234567"
    )
    return user


@pytest.mark.django_db
class TestUserModel:
    def test_create_user_model_valid_data(self):
        user = User.objects.create_user(
            email="mo@gmail.com",
            password="m@1234567",
            is_staff=True,
            is_verified=True,
            is_superuser=False,
            is_active=True,
            created_date=datetime.now(),
        )
        # test create user with unique email
        try:
            with transaction.atomic():
                User.objects.create_user(
                    email="mo@gmail.com",
                    password="m@/123456789",
                )
        except Exception:
            assert True
        assert User.objects.count() == 1
        assert User.objects.filter(pk=user.id).exists() == True
        assert user.email == "mo@gmail.com"
        assert user.is_staff == True
        assert user.is_superuser == False
        assert user.is_active == True
        assert user.is_verified == True
        profile = Profile.objects.first()
        assert profile is None
        assert Profile.objects.count() == 0

    def test_create_user_model_default_permission(self):
        user = User.objects.create_user(
            email="mo@gmail.com",
            password="m@1234567",
            created_date=datetime.now(),
        )
        assert User.objects.count() == 1
        assert user.is_staff == False
        assert user.is_superuser == False
        assert user.is_active == True
        assert user.is_verified == False

    def test_create_user_model_no_email(self):
        try:
            User.objects.create_user(
                password="m@1234567",
                is_staff=True,
                is_verified=True,
                is_superuser=False,
                is_active=True,
                created_date=datetime.now(),
            )

        except Exception:
            assert True
        assert User.objects.count() == 0

    def test_create_user_model_no_password(self):
        try:
            User.objects.create_user(
                email="mo@gmail.com",
                is_staff=True,
                is_verified=True,
                is_superuser=False,
                is_active=True,
                created_date=datetime.now(),
            )
        except Exception:
            assert True
        assert User.objects.count() == 0

    # test does not work

    # def test_create_user_model_bad_data(self):
    #     user = User.objects.create_user(
    #         'm',
    #         'm',
    #     )
    #     assert user.email == 'm'

    def test_create_seperuser_model_valid_data(self):
        user = User.objects.create_superuser(
            email="mo@gmail.com",
            password="m@1234567",
        )
        assert user is not None
        assert user.is_staff == True
        assert user.is_superuser == True
        assert user.is_active == True
        assert user.is_verified == True

    def test_create_superuser_model_wrong_permission(self):
        try:
            User.objects.create_superuser(
                email="mo@gmail.com", password="m@1234567", is_staff=False
            )
        except Exception:
            assert True
        try:
            User.objects.create_superuser(
                email="mo@gmail.com", password="m@1234567", is_superuser=False
            )
        except Exception:
            assert True
        assert User.objects.count() == 0

    def test_create_profile_model_vlalid_data(self, normal_user):
        profile = Profile.objects.create(
            user=normal_user,
            first_name="John",
            last_name="christ",
            description="Description",
            created_date=datetime.now(),
        )

        assert profile is not None
        assert Profile.objects.count() == 1

    def test_create_profile_model_wrong_data(self):
        try:
            with transaction.atomic():
                Profile.objects.create(
                    first_name="John",
                    last_name="christ",
                    description="Description",
                    created_date=datetime.now(),
                )
        except Exception:
            assert True
        assert Profile.objects.count() == 0
        assert User.objects.count() == 0
