from . import views
from rest_framework.routers import DefaultRouter
from django.urls import path

app_name = "blog"

router = DefaultRouter()
router.register("blog", views.BlogModelViewSet, basename="blog")

urlpatterns = [
    path("vote/", views.VoteCreateApiView.as_view(), name="vote"),
]
urlpatterns += router.urls
