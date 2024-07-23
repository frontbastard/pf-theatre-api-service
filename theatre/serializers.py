from rest_framework import serializers

from theatre.models import TheatreHall


class TheatreHallSerializer(serializers.Serializer):
    id = serializers.IntegerField(read_only=True)
    name = serializers.CharField(max_length=255)
    rows = serializers.IntegerField(required=True)
    seats_in_row = serializers.IntegerField(required=True)

    def create(self, validated_data):
        return TheatreHall.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get("name", instance.name)
        instance.rows = validated_data.get("rows", instance.rows)
        instance.seats_in_row = validated_data.get("seats_in_row",
                                                   instance.seats_in_row)
        instance.save()
        return instance
