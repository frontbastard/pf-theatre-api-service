from django.db import transaction
from rest_framework import serializers
from rest_framework.relations import SlugRelatedField

from theatre.models import (
    TheatreHall,
    Performance,
    Play,
    Actor,
    Genre,
    Reservation,
    Ticket,
)


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
        slug_field="full_name",
    )
    genres = SlugRelatedField(
        many=True,
        read_only=True,
        slug_field="name",
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
        read_only=True,
    )
    theatre_hall_seats = serializers.IntegerField(
        source="theatre_hall.capacity",
        read_only=True,
    )
    play_title = serializers.CharField(
        source="play.title",
        read_only=True,
    )
    tickets_available = serializers.IntegerField(read_only=True)

    class Meta:
        model = Performance
        fields = (
            "id",
            "show_time",
            "play_title",
            "theatre_hall_name",
            "tickets_available",
            "theatre_hall_seats",
        )


class PerformanceDetailSerializer(PerformanceSerializer):
    theatre_hall = TheatreHallSerializer(many=False, read_only=True)
    play = PlayDetailSerializer(many=False, read_only=True)
    taken_seats = serializers.SerializerMethodField()

    def get_taken_seats(self, obj):
        tickets = obj.tickets.all()
        return [{"row": ticket.row, "seat": ticket.seat} for ticket in tickets]


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket
        exclude = ("reservation",)

    def validate(self, attrs):
        Ticket.validate_ticket(
            attrs["row"],
            attrs["seat"],
            attrs["performance"].theatre_hall,
            serializers.ValidationError,
        )
        return attrs


class TicketListSerializer(TicketSerializer):
    performance = PerformanceListSerializer(read_only=True)


class ReservationSerializer(serializers.ModelSerializer):
    tickets = TicketSerializer(many=True, read_only=False, allow_empty=False)

    class Meta:
        model = Reservation
        fields = ("id", "created_at", "tickets")

    def create(self, validated_data):
        with transaction.atomic():
            tickets = validated_data.pop("tickets")
            reservation = Reservation.objects.create(**validated_data)

            for ticket in tickets:
                Ticket.objects.create(reservation=reservation, **ticket)

            return reservation


class ReservationListSerializer(ReservationSerializer):
    tickets = TicketListSerializer(many=True, read_only=True)
