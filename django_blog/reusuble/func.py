from rest_framework_simplejwt.tokens import RefreshToken
from mail_templated import EmailMessage
from accounts.utils import EmailThread
from django.shortcuts import get_object_or_404
from django.contrib.auth import get_user_model


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
