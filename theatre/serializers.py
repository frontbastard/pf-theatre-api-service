from rest_framework import serializers

from theatre.models import TheatreHall, Performance


class TheatreHallSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheatreHall
        fields = "__all__"


class PerformanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Performance
        fields = "__all__"


class PerformanceListSerializer(serializers.ModelSerializer):
    theatre_hall_name = serializers.CharField(
        source="theatre_hall.name",
        read_only=True
    )
    play_title = serializers.CharField(
        source="play.title",
        read_only=True
    )

    class Meta:
        model = Performance
        fields = (
            "id",
            "show_time",
            "play_title",
            "theatre_hall_name",
        )
