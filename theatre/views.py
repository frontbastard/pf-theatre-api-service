from rest_framework import viewsets

from theatre.models import (
    TheatreHall,
    Performance,
    Play,
    Genre,
    Actor,
    Reservation,
)
from theatre.serializers import (
    TheatreHallSerializer,
    PerformanceSerializer,
    PerformanceListSerializer,
    PlaySerializer,
    PlayListSerializer,
    GenreSerializer,
    ActorSerializer,
    PlayDetailSerializer,
    PerformanceDetailSerializer,
    ReservationSerializer
)


class TheatreHallViewSet(viewsets.ModelViewSet):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer


class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return PerformanceListSerializer

        if self.action == "retrieve":
            return PerformanceDetailSerializer

        return PerformanceSerializer

    def get_queryset(self):
        if self.action in ("list", "detail"):
            return self.queryset.select_related()

        return self.queryset


class PlayViewSet(viewsets.ModelViewSet):
    queryset = Play.objects.all()
    serializer_class = PlaySerializer

    def get_serializer_class(self):
        if self.action == "list":
            return PlayListSerializer

        if self.action == "retrieve":
            return PlayDetailSerializer

        return PlaySerializer

    def get_queryset(self):
        if self.action in ("list", "retrieve"):
            return self.queryset.prefetch_related("genres", "actors")

        return self.queryset


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer


class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
