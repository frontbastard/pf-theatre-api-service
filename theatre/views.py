from django.db.models import Count, F
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication

from theatre.models import (
    TheatreHall,
    Performance,
    Play,
    Genre,
    Actor,
    Reservation,
)
from theatre.permissions import IsAuthenticatedForPostOrReadOnly
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
    ReservationSerializer,
    ReservationListSerializer
)


class TheatreHallViewSet(viewsets.ModelViewSet):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer
    authentication_classes = (TokenAuthentication,)


class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.all()
    serializer_class = PerformanceSerializer
    authentication_classes = (TokenAuthentication,)

    def get_serializer_class(self):
        serializer = self.serializer_class

        if self.action == "list":
            serializer = PerformanceListSerializer

        if self.action == "retrieve":
            serializer = PerformanceDetailSerializer

        return serializer

    def get_queryset(self):
        queryset = self.queryset

        if self.action == "list":
            queryset = (
                queryset
                .select_related()
                .annotate(
                    tickets_available=(
                        F(
                            "theatre_hall__rows"
                        ) * F(
                            "theatre_hall__seats_in_row"
                        ) - Count(
                            "tickets"
                        )
                    )
                )
            )

        if self.action == "retrieve":
            queryset = queryset.select_related()

        return queryset


class PlayViewSet(viewsets.ModelViewSet):
    queryset = Play.objects.all()
    serializer_class = PlaySerializer
    authentication_classes = (TokenAuthentication,)

    @staticmethod
    def _params_to_ints(query_string):
        """
        Converts a string of format '1,3,4' to a list of integers [1,2,3].
        """
        return [int(str_id) for str_id in query_string.split(",")]

    def get_serializer_class(self):
        if self.action == "list":
            return PlayListSerializer

        if self.action == "retrieve":
            return PlayDetailSerializer

        return PlaySerializer

    def get_queryset(self):
        queryset = self.queryset
        title = self.request.query_params.get("title")
        genres = self.request.query_params.get("genres")

        if genres:
            genres = self._params_to_ints(genres)
            queryset = queryset.filter(genres__id__in=genres)

        if title:
            queryset = self.queryset.filter(title__icontains=title)

        if self.action in ("list", "retrieve"):
            queryset = queryset.prefetch_related("genres", "actors")

        return queryset.distinct()


class GenreViewSet(viewsets.ModelViewSet):
    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    authentication_classes = (TokenAuthentication,)


class ActorViewSet(viewsets.ModelViewSet):
    queryset = Actor.objects.all()
    serializer_class = ActorSerializer
    authentication_classes = (TokenAuthentication,)


class ReservationViewSet(viewsets.ModelViewSet):
    queryset = Reservation.objects.all()
    serializer_class = ReservationSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticatedForPostOrReadOnly,)

    def get_serializer_class(self):
        serializer = self.serializer_class

        if self.action == "list":
            return ReservationListSerializer

        return serializer

    def get_queryset(self):
        if self.request.user.is_authenticated:
            queryset = self.queryset.filter(user=self.request.user.id)

            if self.action == "list":
                queryset = queryset.prefetch_related(
                    "tickets__performance__play",
                    "tickets__performance__theatre_hall",
                )

            return queryset
        return Reservation.objects.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
