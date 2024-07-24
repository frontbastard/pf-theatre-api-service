from rest_framework import viewsets

from theatre.models import TheatreHall, Performance
from theatre.serializers import (
    TheatreHallSerializer,
    PerformanceSerializer,
    PerformanceListSerializer
)


class TheatreHallViewSet(viewsets.ModelViewSet):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer


class PerformanceViewSet(viewsets.ModelViewSet):
    queryset = Performance.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return PerformanceListSerializer

        return PerformanceSerializer

    def get_queryset(self):
        queryset = Performance.objects.all()
        if self.action == "list":
            return queryset.select_related()

        return queryset
