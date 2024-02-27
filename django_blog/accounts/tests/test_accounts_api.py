from rest_framework.test import APIClient
import pytest
from django.urls import reverse
from accounts.models import User, Profile


@pytest.fixture
def api_client():
    client = APIClient()
    return client


@pytest.fixture
def user_data():
    data = {
        "email": "mo@gmail.com",
        "password": "m@1234567",
        "password1": "m@1234567",
    }
    return data


@pytest.fixture
def normal_user():
    profile = Profile.objects.create(
        user=User.objects.create_user(
            email="mo@gmail.com",
            password="m@1234567",
            is_verified=True,
        )
    )
    return profile.user


@pytest.mark.django_db
class TestAccountsApi:
    def test_post_registration_response_201_status(
        self, api_client, user_data
    ):
        url = reverse("accounts:registration")
        response = api_client.post(url, user_data, format="json")
        assert response.status_code == 201
        assert User.objects.count() == 1
        assert User.objects.first().email == "mo@gmail.com"
        assert Profile.objects.count() == 1

    def test_post_registration_password_no_match_response_400_status(
        self, api_client
    ):
        url = reverse("accounts:registration")
        data = {
            "email": "mo@gmail.com",
            "password": "m@1234567",
            "password1": "m@12345678",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == 400
        assert User.objects.count() == 0
        assert Profile.objects.count() == 0

    def test_post_registration_no_email_response_400_status(self, api_client):
        url = reverse("accounts:registration")
        data = {
            "password": "m@1234567",
            "password1": "m@12345678",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == 400
        assert User.objects.count() == 0
        assert Profile.objects.count() == 0

    def test_post_registration_no_password1_response_400_status(
        self, api_client
    ):
        url = reverse("accounts:registration")
        data = {
            "email": "mo@gmail.com",
            "password": "m@1234567",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == 400
        assert User.objects.count() == 0
        assert Profile.objects.count() == 0

    def test_post_registration_unique_email_response_400_status(
        self, api_client, normal_user, user_data
    ):
        url = reverse("accounts:registration")
        api_client.force_login(normal_user)
        response = api_client.post(url, user_data, format="json")
        assert response.status_code == 400
        assert User.objects.count() == 1

    def test_post_registration_password_complexity_response_400_status(
        self, api_client
    ):
        url = reverse("accounts:registration")
        data = {
            "email": "mo@gmail.com",
            "password": "m",
            "password1": "m",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == 400

    def test_create_jwt_token_response_200_status(
        self, api_client, normal_user
    ):
        url = reverse("accounts:jwt-create")
        data = {
            "email": "mo@gmail.com",
            "password": "m@1234567",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == 200
        assert User.objects.count() == 1
        assert normal_user.is_verified == True
        assert response.data["email"] == "mo@gmail.com"
        assert response.data["user_id"] == 1
        return (response.data["refresh"], response.data["access"])

    def test_create_jwt_token_not_verified_response_400_status(
        self, api_client
    ):
        url = reverse("accounts:jwt-create")
        User.objects.create_user("mo@gmail.com", "m@1234567")
        data = {
            "email": "mo@gmail.com",
            "password": "m@1234567",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == 400
        assert User.objects.count() == 1

    def test_create_jwt_token_not_register_response_401_status(
        self, api_client
    ):
        url = reverse("accounts:jwt-create")
        data = {
            "email": "mo@gmail.com",
            "password": "m@1234567",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == 401
        assert User.objects.count() == 0

    def test_create_jwt_token_not_active_response_401_status(self, api_client):
        url = reverse("accounts:jwt-create")
        User.objects.create_user(
            email="mo@gmail.com",
            password="m@1234567",
            is_active=False,
            is_verified=True,
        )
        data = {
            "email": "mo@gmail.com",
            "password": "m@1234567",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == 401
        assert User.objects.count() == 1

    def test_post_refresh_valid_jwt_token_response_200_status(
        self, api_client, normal_user
    ):
        token = self.test_create_jwt_token_response_200_status(
            api_client, normal_user
        )
        url = reverse("accounts:jtw-refresh")
        data = {
            "refresh": token[0],
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == 200

    def test_post_refresh_invalid_jwt_token_response_200_status(
        self, api_client, normal_user
    ):
        token = self.test_create_jwt_token_response_200_status(
            api_client, normal_user
        )
        url = reverse("accounts:jtw-refresh")
        data = {
            "refresh": token[0] + "to invalid",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == 401

    def test_post_verify_valid_jwt_token_response_200_status(
        self, api_client, normal_user
    ):
        token = self.test_create_jwt_token_response_200_status(
            api_client, normal_user
        )
        url = reverse("accounts:token-verify")
        data = {
            "token": token[1],
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == 200
        data = {
            "token": token[0],
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == 200

    def test_post_verify_invalid_jwt_token_response_401_status(
        self, api_client, normal_user
    ):
        token = self.test_create_jwt_token_response_200_status(
            api_client, normal_user
        )
        url = reverse("accounts:token-verify")
        data = {
            "token": token[1] + "12",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == 401
        data = {
            "token": token[0] + "12",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == 401

    def test_put_change_password_valid_data_response_200(
        self, api_client, normal_user
    ):
        url = reverse("accounts:change-password")
        user = normal_user
        api_client.force_login(user)
        data = {
            "old_password": "m@1234567",
            "new_password": "m@12345678",
            "new_password1": "m@12345678",
        }
        response = api_client.put(url, data, format="json")
        assert response.status_code == 200

    def test_put_change_password_unauthorized_response_401(self, api_client):
        url = reverse("accounts:change-password")
        data = {
            "old_password": "m@1234567",
            "new_password": "m@12345678",
            "new_password1": "m@12345678",
        }
        response = api_client.put(url, data, format="json")
        assert response.status_code == 401

    def test_put_change_password_not_match_passwords_response_400(
        self, api_client, normal_user
    ):
        url = reverse("accounts:change-password")
        user = normal_user
        api_client.force_login(user)
        data = {
            "old_password": "m@1234567",
            "new_password": "m@12345678",
            "new_password1": "m@123456789",
        }
        response = api_client.put(url, data, format="json")
        assert response.status_code == 400

    def test_put_change_password_wrong_old_password_response_400(
        self, api_client, normal_user
    ):
        url = reverse("accounts:change-password")
        user = normal_user
        api_client.force_login(user)
        data = {
            "old_password": "m@123456799",
            "new_password": "m@12345678",
            "new_password1": "m@12345678",
        }
        response = api_client.put(url, data, format="json")
        assert response.status_code == 400

    def test_put_change_password_not_old_password_response_400(
        self, api_client, normal_user
    ):
        url = reverse("accounts:change-password")
        user = normal_user
        api_client.force_login(user)
        data = {
            "new_password": "m@12345678",
            "new_password1": "m@12345678",
        }
        response = api_client.put(url, data, format="json")
        assert response.status_code == 400

    def test_put_profile_response_200(self, api_client, normal_user):
        url = reverse("accounts:profile")
        user = normal_user
        api_client.force_login(user)
        data = {
            "first_name": "mohammad",
            "last_name": "jafari",
            "description": "this is my description",
        }
        response = api_client.put(url, data, format="json")
        assert response.status_code == 200
        assert User.objects.count() == 1
        assert Profile.objects.count() == 1
        for profile_obj in Profile.objects.all():
            assert profile_obj.first_name == "mohammad"
            assert profile_obj.last_name == "jafari"
            assert profile_obj.description == "this is my description"

    def test_put_profile_unauthorized_response_401_status(self, api_client):
        url = reverse("accounts:profile")
        data = {
            "first_name": "mohammad",
            "last_name": "jafari",
            "description": "this is my description",
        }
        response = api_client.put(url, data)
        assert response.status_code == 401
        assert User.objects.count() == 0
        assert Profile.objects.count() == 0

    def test_put_profile_bad_request_response_400(
        self, api_client, normal_user
    ):
        url = reverse("accounts:profile")
        user = normal_user
        api_client.force_login(user)
        data = {
            "last_name": "jafari",
            "description": "this is my description",
        }
        response = api_client.put(url, data)
        assert response.status_code == 400
        assert User.objects.count() == 1
        assert Profile.objects.count() == 1
        for profile_obj in Profile.objects.all():
            assert profile_obj.first_name != "mohammad"
            assert profile_obj.last_name != "jafari"
            assert profile_obj.description != "this is my description"

    def test_get_profile_response_200(self, api_client, normal_user):
        url = reverse("accounts:profile")
        user = normal_user
        api_client.force_login(user)
        response = api_client.get(url)
        assert response.status_code == 200
        assert User.objects.count() == 1
        assert Profile.objects.count() == 1

    def test_get_profile_unauthorized__response_401_status(self, api_client):
        url = reverse("accounts:profile")
        response = api_client.get(url)
        assert response.status_code == 401
        assert User.objects.count() == 0
        assert Profile.objects.count() == 0

    def test_get_verfication_email_response_200_status(
        self, api_client, normal_user
    ):
        url = reverse("accounts:verification-email")
        user = normal_user
        api_client.force_login(user)
        response = api_client.get(url)
        assert response.status_code == 200

    def test_get_verfication_email_unauthorized_response_401_status(
        self, api_client
    ):
        url = reverse("accounts:verification-email")
        response = api_client.get(url)
        assert response.status_code == 401

    def test_get_activation_valid_token_response_200_status(
        self, api_client, normal_user
    ):
        token = self.test_create_jwt_token_response_200_status(
            api_client, normal_user
        )
        normal_user.is_verified = False
        normal_user.save()
        url = reverse("accounts:activation", args=[token[1]])
        response = api_client.get(url)
        assert response.status_code == 200

    def test_get_activation_invalid_token_response_200_status(
        self, api_client, normal_user
    ):
        token = self.test_create_jwt_token_response_200_status(
            api_client, normal_user
        )
        normal_user.is_verified = False
        normal_user.save()
        url = reverse("accounts:activation", args=[token[1] + "m"])
        response = api_client.get(url)
        assert response.status_code == 400

    def test_get_activation_verified_user_token_response_400_status(
        self, api_client, normal_user
    ):
        token = self.test_create_jwt_token_response_200_status(
            api_client, normal_user
        )
        url = reverse("accounts:activation", args=[token[1]])
        response = api_client.get(url)
        assert response.status_code == 400

    def test_post_resend_activation_valid_data_response_200(
        self, api_client, normal_user
    ):
        url = reverse("accounts:resend-activation")
        normal_user.is_verified = False
        normal_user.save()
        data = {
            "email": "mo@gmail.com",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == 200

    def test_post_resend_activation_verify_user_response_400(
        self, api_client, normal_user
    ):
        url = reverse("accounts:resend-activation")
        data = {
            "email": "mo@gmail.com",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == 400

    def test_post_resend_activation_no_user_response_400(self, api_client):
        url = reverse("accounts:resend-activation")
        data = {
            "email": "mo@gmail.com",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == 400

    def test_post_reset_password_email_valid_data_response_200(
        self, api_client, normal_user
    ):
        url = reverse("accounts:reset-password")
        data = {
            "email": "mo@gmail.com",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == 200

    def test_post_reset_password__email_no_user_response_400(self, api_client):
        url = reverse("accounts:reset-password")
        data = {
            "email": "mo@gmail.com",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == 400

    def test_post_reset_password_confirm_valid_token_response_200(
        self, api_client, normal_user
    ):
        token = self.test_create_jwt_token_response_200_status(
            api_client, normal_user
        )
        url = reverse("accounts:reset-password-confirmation", args=[token[1]])
        data = {
            "new_password": "m@12345678",
            "new_password1": "m@12345678",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == 200

    def test_post_reset_password_confirm_invalid_token_response_400(
        self, api_client, normal_user
    ):
        token = self.test_create_jwt_token_response_200_status(
            api_client, normal_user
        )
        url = reverse(
            "accounts:reset-password-confirmation",
            args=[token[1] + "m"],
        )
        data = {
            "new_password": "m@12345678",
            "new_password1": "m@12345678",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == 400

    def test_post_reset_password_confirm_not_match_password_response_400(
        self, api_client, normal_user
    ):
        token = self.test_create_jwt_token_response_200_status(
            api_client, normal_user
        )
        url = reverse("accounts:reset-password-confirmation", args=[token[1]])
        data = {
            "new_password": "m@123456789",
            "new_password1": "m@12345678",
        }
        response = api_client.post(url, data, format="json")
        assert response.status_code == 400
