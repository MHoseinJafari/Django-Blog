from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.authtoken.models import Token
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

import jwt
from jwt.exceptions import (
    ExpiredSignatureError,
    InvalidSignatureError,
    DecodeError,
)

from django.shortcuts import get_object_or_404
from django.conf import settings
from mail_templated import EmailMessage
from .utils import EmailThread


from .serializers import (
    RegistrationSerializer,
    CustomTokenObtainPairSerializer,
    ChangePasswordSerializer,
    ProfileSerializer,
    ActivationEmailSerializer,
    ResetPasswordSerializer,
)
from django.contrib.auth import get_user_model
from .models import Profile
from accounts.permissions import IsVerified

User = get_user_model()


# TODO:send email function for multiple views
def send_email(email, email_format):
    user_obj = get_object_or_404(User, email=email)
    token = get_tokens_for_user(user_obj)
    email_obj = EmailMessage(
        "email/%s.tpl" % email_format,
        {"token": token},
        "admin@admin.com",
        to=[email],
    )
    EmailThread(email_obj).start()


# TODO:generate token for user for send email function
def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)


# TODO:register user and send email for activation
class RegistrationApiView(generics.GenericAPIView):
    serializer_class = RegistrationSerializer

    def post(self, request, *args, **kwargs):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            email = serializer.validated_data["email"]
            data = {"email": email}
            send_email(email, email_format="activation")
            return Response(data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            # check old password
            if not self.object.check_password(
                serializer.data.get("old_password")
            ):
                return Response(
                    {"old_password": ["wrong password"]},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            # set new password to user
            self.object.set_password(serializer.data.get("new_password"))
            self.object.save()
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
        except ExpiredSignatureError:
            return Response(
                {"details": "token has been expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except InvalidSignatureError:
            return Response(
                {"details": "token is not valid"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except DecodeError:
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
        except ExpiredSignatureError:
            return Response(
                {"details": "token has been expired"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except InvalidSignatureError:
            return Response(
                {"details": "token is not valid"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except DecodeError:
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