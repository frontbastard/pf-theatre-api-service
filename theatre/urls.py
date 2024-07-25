from django.urls import path, include
from rest_framework import routers

from theatre.views import (
    TheatreHallViewSet,
    PerformanceViewSet,
    PlayViewSet,
    GenreViewSet,
    ActorViewSet,
    ReservationViewSet,
)

app_name = "theatre"

router = routers.DefaultRouter()
router.register("theatre-halls", TheatreHallViewSet)
router.register("performances", PerformanceViewSet)
router.register("plays", PlayViewSet)
router.register("genres", GenreViewSet)
router.register("actors", ActorViewSet)
router.register("reservations", ReservationViewSet)

urlpatterns = [
    path("", include(router.urls))
]
