from rest_framework import viewsets, mixins

from theatre.models import TheatreHall
from theatre.serializers import TheatreHallSerializer


class TheatreHallViewSet(viewsets.ModelViewSet):
    queryset = TheatreHall.objects.all()
    serializer_class = TheatreHallSerializer
