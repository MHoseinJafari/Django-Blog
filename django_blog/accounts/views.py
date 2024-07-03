from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db import transaction
from rest_framework.exceptions import ParseError


import jwt

from django.shortcuts import get_object_or_404
from django.conf import settings

from .serializers import (
    RegistrationSerializer,
    CustomTokenObtainPairSerializer,
    ChangePasswordSerializer,
    ProfileSerializer,
    ActivationEmailSerializer,
    ResetPasswordSerializer,
)
from django.contrib.auth import get_user_model
from .models import Profile, User
from accounts.permissions import IsVerified
from reusuble.func import send_email


# TODO:register user and send email for activation
class RegistrationApiView(generics.CreateAPIView):
    serializer_class = RegistrationSerializer

    @transaction.atomic
    def perform_create(self, serializer):
        instanse = serializer.save()
        email = instanse.email
        send_email(email, email_format="activation")
        user = User.objects.get(email=email)
        Profile.objects.create(user=user)
        return Response({"email": email}, status=status.HTTP_201_CREATED)


# TODO:generate token
class CustomobtainAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token, created = Token.objects.get_or_create(user=user)
        return Response(
            {"token": token.key, "user_id": user.pk, "email": user.email}
        )


# TODO:delete token
class CustomDiscardAuthToken(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        request.user.auth_token.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# TODO:generate jwt token
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


# TODO:user can change password in account
class ChangePasswordApiView(generics.UpdateAPIView):
    model = User
    permission_classes = [IsAuthenticated, IsVerified]
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        obj = self.request.user
        return obj

    def update(self, request, *args, **kwargs):
        serializer = ChangePasswordSerializer(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        return Response(
            {"detail": "password changes successfully"},
            status=status.HTTP_200_OK,
        )


# TODO:show profile in account and user can change profile information
class ProfileApiView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsVerified]
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()

    def get_object(self):
        queryset = self.get_queryset()
        obj = get_object_or_404(queryset, user=self.request.user)
        return obj


# TODO:structure of send email
class VerficationEmailApiView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        self.email = request.user.email
        send_email(self.email, email_format="activation")
        return Response("email sent")


# TODO:activation email for verify users
class ActivationApiView(APIView):
    def get(self, request, token, *args, **kwargs):
        try:
            User.user_activation(token)
        except ValueError as e:
            raise ParseError({"details": str(e)})
        return Response(
            {"details": "your account has been verified successfully"},
            status=status.HTTP_200_OK,
        )


# TODO:resend activation email for verify users
class ActivationResendApiView(generics.CreateAPIView):
    serializer_class = ActivationEmailSerializer

    def perform_create(self, serializer):
        user_obj = serializer.validated_data["user"]
        try:
            User.check_verify(user_obj)
        except ValueError as e:
            raise ParseError({"detail": str(e)})
        send_email(user_obj.email, email_format="activation")


# TODO:send email for reset password when user is verified and can not login
class ResetPasswordEmailApiView(generics.CreateAPIView):
    serializer_class = ActivationEmailSerializer

    def perform_create(self, serializer):
        user_obj = serializer.validated_data["user"]
        if not user_obj.is_verified:
            raise ParseError({"details": "user is not verified"})
        send_email(user_obj.email, email_format="reset_password")


# TODO:with this class the user is allowed to change password
class ResetPasswordConfirmation(generics.CreateAPIView):
    model = User
    serializer_class = ResetPasswordSerializer

    def create(self, request, token):
        user_obj = User.check_jwt(token)
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_obj.set_password(serializer.data.get("new_password"))
        user_obj.save()
        return Response(
            {"detail": "password changes successfully"},
            status=status.HTTP_200_OK,
        )
