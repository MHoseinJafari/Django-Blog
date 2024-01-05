from . import views
from rest_framework.routers import DefaultRouter

app_name = 'api-vi'

router = DefaultRouter()
router.register("blog", views.BlogModelViewSet, basename="blog")
urlpatterns = router.urls