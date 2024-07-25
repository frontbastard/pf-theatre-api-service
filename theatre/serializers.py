from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from theatre.models import TheatreHall, Performance, Play, Actor, Genre


class TheatreHallSerializer(serializers.ModelSerializer):
    class Meta:
        model = TheatreHall
        fields = "__all__"


class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = "__all__"


class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = "__all__"


class PlaySerializer(serializers.ModelSerializer):
    class Meta:
        model = Play
        fields = "__all__"


class PlayListSerializer(PlaySerializer):
    actors = SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="full_name"
    )
    genres = SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name"
    )


class PlayDetailSerializer(PlaySerializer):
    actors = ActorSerializer(many=True)
    genres = GenreSerializer(many=True)


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


class PerformanceDetailSerializer(PerformanceSerializer):
    theatre_hall = TheatreHallSerializer(many=False, read_only=True)
    play = PlayDetailSerializer(many=False, read_only=True)
