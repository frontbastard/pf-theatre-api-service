import factory
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.utils import timezone

from theatre.models import Reservation, Play, Actor, Genre, TheatreHall


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = get_user_model()

    email = factory.Faker("email")
    password = factory.LazyFunction(
        lambda: make_password(
            factory.Faker("password").evaluate(
                None,
                None,
                {"locale": None}
            )
        )
    )

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        manager = cls._get_manager(model_class)
        return manager.create_user(*args, **kwargs)


class TheatreHallFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = TheatreHall

    name = factory.Faker("sentence")
    rows = factory.Faker("pyint", min_value=5, max_value=30)
    seats_in_row = factory.Faker("pyint", min_value=10, max_value=50)


class ReservationFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Reservation

    created_at = timezone.now()
    user = factory.SubFactory(UserFactory)


class ActorFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Actor

    first_name = factory.Faker("first_name")
    last_name = factory.Faker("last_name")


class GenreFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Genre

    name = factory.Faker("sentence")


class PlayFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = Play

    title = factory.Faker("sentence")
    description = factory.Faker("paragraph")

    @factory.post_generation
    def actors(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for actor in extracted:
                self.actors.add(actor)

    @factory.post_generation
    def genres(self, create, extracted, **kwargs):
        if not create:
            return

        if extracted:
            for genre in extracted:
                self.genres.add(genre)
