from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from accounts.permissions import IsVerifiedOrReadOnly
from blog.serializers import CommentSerializer
from .models import Comment
from . import filters


class CommentModelViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsVerifiedOrReadOnly]
    filter_backends = [DjangoFilterBackend]
    filterset_class = filters.CommentFilter
    queryset = Comment.objects.all()
