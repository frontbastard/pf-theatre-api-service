from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import Actor
from theatre.serializers import ActorSerializer
from theatre.tests.factories import UserFactory, ActorFactory

ACTOR_URL = reverse("theatre:actor-list")
PAYLOAD = {
    "first_name": "Test first_name",
    "last_name": "Test last_name",
}


class UnauthorizedActorTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_authentication_is_not_required(self):
        res = self.client.get(ACTOR_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class AuthorizedActorTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_actors_list(self):
        ActorFactory()

        res = self.client.get(ACTOR_URL)
        actors = Actor.objects.all()
        serializer = ActorSerializer(actors, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), len(serializer.data))

    def test_not_admin_can_not_create_actor(self):
        res = self.client.post(ACTOR_URL, PAYLOAD)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Actor.objects.count(), 0)


class AdminActorTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory(is_staff=True)
        self.client.force_authenticate(self.user)

    def test_admin_can_create_play(self):
        res = self.client.post(ACTOR_URL, PAYLOAD)

        play = Actor.objects.get(pk=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Actor.objects.count(), 1)

        for key in PAYLOAD:
            self.assertEqual(PAYLOAD[key], getattr(play, key))
