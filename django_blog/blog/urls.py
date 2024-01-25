from . import views
from rest_framework.routers import DefaultRouter
from django.urls import path
from comment.views import CommentModelViewSet

app_name = "blog"

router = DefaultRouter()
router.register("blog", views.BlogModelViewSet, basename="blog")

urlpatterns = [
    path(
        "blog/<int:pk>/comments",
        CommentModelViewSet.as_view({"post": "create", "get": "list"}),
        name="comments",
    ),
    path(
        "blog/<int:pk>/vote", views.VoteCreateApiView.as_view(), name="vote"
    ),
]
urlpatterns += router.urls
