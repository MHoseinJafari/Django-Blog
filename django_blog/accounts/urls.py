from django.urls import path
from . import views
from rest_framework_simplejwt.views import (
    TokenRefreshView,
    TokenVerifyView,
)



urlpatterns = [
    # registration
    path(
        "registration/",
        views.RegistrationApiView.as_view(),
        name="registration",
    ),
    # token
    path(
        "token/login/",
        views.CustomobtainAuthToken.as_view(),
        name="token-login",
    ),
    path(
        "token/logout/",
        views.CustomDiscardAuthToken.as_view(),
        name="token-logout",
    ),
    # jwt
    path(
        "jwt/create/",
        views.CustomTokenObtainPairView.as_view(),
        name="jwt-create",
    ),
    path("jwt/refresh/", TokenRefreshView.as_view(), name="jtw-refresh"),
    path("jwt/verify/", TokenVerifyView.as_view(), name="token-verify"),
    # change password
    path(
        "change-password/",
        views.ChangePasswordApiView.as_view(),
        name="change-password",
    ),
    # profile
    path("profile/", views.ProfileApiView.as_view(), name="profile"),
    # email
    path(
        "verification-email",
        views.VerficationEmailApiView.as_view(),
        name="verification-email",
    ),
    # activation with token
    path(
        "activation/confirm/<str:token>",
        views.ActivationApiView.as_view(),
        name="activation",
    ),
    # resend token
    path(
        "activation/resend/",
        views.ActivationResendApiView.as_view(),
        name="resend-activation",
    ),
    # reset password email
    path(
        "reset-password/",
        views.ResetPasswordEmailApiView.as_view(),
        name="reset-password",
    ),
    # reset password confirmation
    path(
        "reset-password/confirm/<str:token>",
        views.ResetPasswordConfirmation.as_view(),
        name="reset-password-confirmation",
    ),
]
