from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import Play
from theatre.serializers import PlaySerializer
from theatre.tests.factories import (
    UserFactory, PlayFactory, ActorFactory,
    GenreFactory,
)

PLAY_URL = reverse("theatre:play-list")


class UnauthorizedPlayTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(PLAY_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class AuthorizedPlayTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_plays_list(self):
        actors = [ActorFactory() for _ in range(2)]
        genres = [GenreFactory() for _ in range(2)]
        PlayFactory(actors=actors, genres=genres)

        res = self.client.get(PLAY_URL)
        plays = Play.objects.all()
        serializer = PlaySerializer(plays, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), len(serializer.data))
