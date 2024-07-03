from rest_framework import viewsets, generics
from .models import Blog
from . import serializers
from accounts.permissions import (
    IsVerifiedOrReadOnly,
    IsOwnerOrReadOnly,
    IsVerified,
)
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
)
from rest_framework.filters import OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend


class BlogModelViewSet(viewsets.ModelViewSet):
    queryset = Blog.objects.all()
    permission_classes = [
        IsAuthenticatedOrReadOnly,
        IsVerifiedOrReadOnly,
        IsOwnerOrReadOnly,
    ]
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = {"category": ["exact", "in"]}
    ordering_fields = ["created_date"]

    def get_serializer_class(self):
        if self.action == "create":
            return serializers.BlogCreateSerializer
        return serializers.BlogSerializer


class VoteCreateApiView(generics.CreateAPIView):
    serializer_class = serializers.VoteSerializer
    permission_classes = [IsAuthenticated, IsVerified]

    def perform_create(self, serializer):
        vote_obj = serializer.validated_data["vote"]
        vote_obj = int(vote_obj)
        blog = serializer.validated_data["post"]
        blog.vote_submit(user=self.request.user, amount=vote_obj)

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(post=self.kwargs.get("pk"), user=self.request.user)
        )
