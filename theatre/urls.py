from django.urls import path, include
from rest_framework import routers

from theatre.views import TheatreHallViewSet

app_name = "theatre"

router = routers.DefaultRouter()
router.register("theatre-halls", TheatreHallViewSet)

urlpatterns = [
    path("", include(router.urls))
]
