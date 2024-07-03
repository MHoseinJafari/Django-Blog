from django.urls import path
from comment.views import CommentModelViewSet


urlpatterns = [
    path(
        "",
        CommentModelViewSet.as_view({"post": "create", "get": "list"}),
        name="comments",
    ),
]
