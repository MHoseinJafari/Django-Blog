from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from accounts.permissions import IsVerifiedOrReadOnly
from blog.serializers import CommentSerializer
from .models import Comment
from blog.models import Blog


class CommentModelViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticatedOrReadOnly, IsVerifiedOrReadOnly]
    queryset = Comment.objects.all()

    def perform_create(self, serializer):
        serializer.save(
            author=self.request.user,
            post=Blog.objects.get(pk=self.kwargs.get("pk")),
        )

    def get_queryset(self):
        return (
            super()
            .get_queryset()
            .filter(post=self.kwargs.get("pk"))
            .order_by("-date")
        )
