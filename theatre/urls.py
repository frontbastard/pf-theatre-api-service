from django.urls import path, include
from rest_framework import routers

from theatre.views import TheatreHallViewSet, PerformanceViewSet

app_name = "theatre"

router = routers.DefaultRouter()
router.register("theatre-halls", TheatreHallViewSet)
router.register("performances", PerformanceViewSet)

urlpatterns = [
    path("", include(router.urls))
]
