from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from django.db import transaction

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
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        email = self.request.data.get("email", None)
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
class ChangePasswordApiView(generics.GenericAPIView):
    model = User
    permission_classes = [IsAuthenticated, IsVerified]
    serializer_class = ChangePasswordSerializer

    def get_object(self):
        obj = self.request.user
        return obj

    def put(self, request, *args, **kwargs):
        self.object = self.get_object()
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            old_pass = serializer.data.get("old_password")
            new_pass = serializer.data.get("new_password")
            # check old password
            check = User.check_pass(old_pass, self.object)
            if check is False:
                return Response(
                    {"old_password": ["wrong password"]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # set new password to user
            User.set_pass(new_pass, self.object)
            return Response(
                {"detail": "password changes successfully"},
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            token = jwt.decode(
                token, settings.SECRET_KEY, algorithms=["HS256"]
            )
            user_id = token.get("user_id")
        except Exception:
            return Response(
                {"details": "token is not valid"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user_obj = User.objects.get(pk=user_id)
        if user_obj.is_verified:
            return Response(
                {"details": "your accout has already been verified"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user_obj.is_verified = True
        user_obj.save()
        return Response(
            {"details": "your account has been verified successfully"},
            status=status.HTTP_200_OK,
        )


# TODO:resend activation email for verify users
class ActivationResendApiView(generics.GenericAPIView):
    serializer_class = ActivationEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_obj = serializer.validated_data["user"]
        if user_obj.is_verified:
            return Response(
                {"details": "user is already activated and verified"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        send_email(user_obj.email, email_format="activation")
        return Response(
            {"details": "user activation resend successfully"},
            status=status.HTTP_200_OK,
        )


# TODO:send email for reset password when user is verified and can not login
class ResetPasswordEmailApiView(generics.GenericAPIView):
    serializer_class = ActivationEmailSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_obj = serializer.validated_data["user"]
        if user_obj.is_verified:
            send_email(user_obj.email, email_format="reset_password")
            return Response(
                {"details": "reset password link send successfully"},
                status=status.HTTP_200_OK,
            )
        else:
            return Response(
                {"details": "user is not verified"},
                status=status.HTTP_403_FORBIDDEN,
            )


# TODO:with this class the user is allowed to change password
class ResetPasswordConfirmation(generics.GenericAPIView):
    model = User
    serializer_class = ResetPasswordSerializer

    def post(self, request, token, *args, **kwargs):
        try:
            token = jwt.decode(
                token, settings.SECRET_KEY, algorithms=["HS256"]
            )
            user_id = token.get("user_id")
        except Exception:
            return Response(
                {"details": "token is not valid"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        user_obj = User.objects.get(pk=user_id)
        serializer = ResetPasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_obj.set_password(serializer.data.get("new_password"))
        user_obj.save()
        return Response(
            {"detail": "password changes successfully"},
            status=status.HTTP_200_OK,
        )
