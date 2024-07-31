import pathlib
import uuid

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import UniqueConstraint
from django.utils import timezone
from django.utils.text import slugify


def create_image_path(instance, filename: str) -> pathlib.Path:
    filename = (
        f"{slugify(instance.title)}-{uuid.uuid4()}"
        f"{pathlib.Path(filename).suffix}"
    )
    return pathlib.Path(
        "uploads",
        slugify(instance.__class__.__name__),
        pathlib.Path(filename)
    )


class TheatreHall(models.Model):
    name = models.CharField(max_length=255)
    rows = models.PositiveIntegerField()
    seats_in_row = models.PositiveIntegerField()

    @property
    def capacity(self) -> int:
        return self.rows * self.seats_in_row

    def __str__(self):
        return f"Hall #{self.id}: {self.name}"


class Genre(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Actor(models.Model):
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    @property
    def full_name(self):
        return self.__str__()


class Play(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(null=True, blank=True)
    actors = models.ManyToManyField(Actor, blank=True, related_name="plays")
    genres = models.ManyToManyField(Genre, blank=True, related_name="plays")
    image = models.ImageField(
        null=True,
        blank=True,
        upload_to=create_image_path
    )

    def __str__(self):
        return self.title

    class Meta:
        ordering = ("-title",)


class Performance(models.Model):
    play = models.ForeignKey(
        Play,
        on_delete=models.CASCADE,
        related_name="performances"
    )
    theatre_hall = models.ForeignKey(TheatreHall, on_delete=models.CASCADE)
    show_time = models.DateTimeField(db_index=True)

    def __str__(self):
        return f"{self.play.title} {str(self.show_time)}"

    def clean(self):
        if self.show_time < timezone.now():
            raise ValidationError("Show time cannot be in the past.")

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ("-show_time",)


class Reservation(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE
    )

    def __str__(self):
        return f"Reservation #{self.id} by {self.user}"

    class Meta:
        ordering = ("-created_at",)


class Ticket(models.Model):
    row = models.PositiveIntegerField()
    seat = models.PositiveIntegerField()
    performance = models.ForeignKey(
        Performance,
        on_delete=models.CASCADE,
        related_name="tickets"
    )
    reservation = models.ForeignKey(
        Reservation,
        on_delete=models.CASCADE,
        related_name="tickets"
    )

    @staticmethod
    def validate_ticket(row, seat, theatre_hall, error_to_raise):
        for ticket_attr_value, ticket_attr_name, theatre_hall_attr_name in [
            (row, "row", "rows"),
            (seat, "seat", "seats_in_row")
        ]:
            count_attrs = getattr(theatre_hall, theatre_hall_attr_name)

            if not (1 <= ticket_attr_value <= count_attrs):
                raise error_to_raise(
                    {
                        ticket_attr_name:
                            f"{ticket_attr_name} "
                            f"number must be in available range: "
                            f"(1, {theatre_hall_attr_name}): "
                            f"(1, {count_attrs})"
                    }
                )

    def __str__(self):
        return f"{self.performance} - (row: {self.row}, seat: {self.seat})"

    def clean(self):
        Ticket.validate_ticket(
            self.row,
            self.seat,
            self.performance.theatre_hall,
            ValidationError,
        )

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)

    class Meta:
        ordering = ("row", "seat")
        constraints = [
            UniqueConstraint(
                fields=["row", "seat", "performance"],
                name="unique_ticket_row_seat_performance"
            )
        ]
