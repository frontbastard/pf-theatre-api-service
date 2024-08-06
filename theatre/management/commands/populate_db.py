import random

from decouple import config
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone
from faker import Faker

from theatre.models import (
    TheatreHall,
    Genre,
    Actor,
    Play,
    Performance,
    Reservation,
    Ticket,
)

fake = Faker()


class Command(BaseCommand):
    help = "Populate the database with fake data"  # noqa: VNE003

    def handle(self, *args, **kwargs):
        self.stdout.write("Cleaning the database...")
        self.clean_database()
        self.stdout.write("Database cleaned successfully.")

        self.stdout.write("Populating the database...")
        self.create_users()
        self.create_theatre_halls()
        self.create_genres()
        self.create_actors()
        self.create_plays()
        self.create_performances()
        self.create_reservations_and_tickets()
        self.stdout.write("Database populated successfully.")

    def clean_database(self):
        Ticket.objects.all().delete()
        Reservation.objects.all().delete()
        Performance.objects.all().delete()
        Play.objects.all().delete()
        Actor.objects.all().delete()
        Genre.objects.all().delete()
        TheatreHall.objects.all().delete()
        get_user_model().objects.exclude(is_superuser=True).delete()

    def create_users(self):
        for _ in range(10):
            get_user_model().objects.create_user(
                email=fake.unique.email(),
                password=config("FAKER_USER_PASSWORD")
            )

    def create_theatre_halls(self):
        for _ in range(3):
            TheatreHall.objects.create(
                name=fake.company(),
                rows=random.randint(5, 20),
                seats_in_row=random.randint(10, 30)
            )

    def create_genres(self):
        genres = ["Comedy", "Drama", "Musical", "Tragedy", "Historical"]
        for genre in genres:
            Genre.objects.create(name=genre)

    def create_actors(self):
        for _ in range(20):
            Actor.objects.create(
                first_name=fake.first_name(),
                last_name=fake.last_name()
            )

    def create_plays(self):
        actors = list(Actor.objects.all())
        genres = list(Genre.objects.all())
        for _ in range(10):
            play = Play.objects.create(
                title=fake.catch_phrase(),
                description=fake.text()
            )
            play.actors.set(
                random.sample(actors, k=random.randint(2, 5))
            )
            play.genres.set(
                random.sample(
                    genres, k=random.randint(1, 3)
                )
            )

    def create_performances(self):
        plays = list(Play.objects.all())
        halls = list(TheatreHall.objects.all())
        for _ in range(30):
            Performance.objects.create(
                play=random.choice(plays),
                theatre_hall=random.choice(halls),
                show_time=fake.future_datetime(
                    end_date="+30d",
                    tzinfo=timezone.get_current_timezone()
                )
            )

    def create_reservations_and_tickets(self):
        users = list(get_user_model().objects.all())
        performances = list(Performance.objects.all())
        for _ in range(50):
            reservation = Reservation.objects.create(
                user=random.choice(users)
            )
            performance = random.choice(performances)
            for _ in range(random.randint(1, 4)):
                while True:
                    try:
                        Ticket.objects.create(
                            row=random.randint(
                                1, performance.theatre_hall.rows
                            ),
                            seat=random.randint(
                                1, performance.theatre_hall.seats_in_row
                            ),
                            performance=performance,
                            reservation=reservation
                        )
                        break
                    except:  # noqa: E722
                        continue
