from rest_framework import serializers

from theatre.models import TheatreHall


class TheatreHallSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheatreHall
        fields = "__all__"
