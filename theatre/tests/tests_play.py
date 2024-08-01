from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import Play
from theatre.serializers import PlaySerializer, PlayListSerializer
from theatre.tests.factories import (
    UserFactory,
    PlayFactory,
    ActorFactory,
    GenreFactory,
)

PLAY_URL = reverse("theatre:play-list")


class UnauthorizedPlayTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_authentication_is_not_required(self):
        res = self.client.get(PLAY_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_filter_plays_by_genres(self):
        genre_1 = GenreFactory()
        genre_2 = GenreFactory()
        play_with_genre_1 = PlayFactory(genres=[genre_1], image=None)
        play_with_genre_2 = PlayFactory(genres=[genre_2], image=None)
        play_without_genres = PlayFactory(genres=[], image=None)

        res = self.client.get(
            PLAY_URL, {
                "genres":
                    f"{genre_1.id},"
                    f"{genre_2.id}"
            }
        )

        serializer_play_genre_1 = PlayListSerializer(play_with_genre_1)
        serializer_play_genre_2 = PlayListSerializer(play_with_genre_2)
        serializer_play_without_genres = PlayListSerializer(
            play_without_genres
        )

        self.assertIn(serializer_play_genre_1.data, res.data["results"])
        self.assertIn(serializer_play_genre_2.data, res.data["results"])
        self.assertNotIn(
            serializer_play_without_genres.data, res.data["results"]
        )

    def test_filter_plays_by_title(self):
        play_title_1 = PlayFactory(title="Test_1 Title", image=None)
        play_title_2 = PlayFactory(title="Test_2 Title", image=None)
        play_title_3 = PlayFactory(title="Another Title", image=None)

        res = self.client.get(PLAY_URL, {"title": "test"})

        serializer_play_title_1 = PlayListSerializer(play_title_1)
        serializer_play_title_2 = PlayListSerializer(play_title_2)
        serializer_play_title_3 = PlayListSerializer(play_title_3)

        self.assertIn(serializer_play_title_1.data, res.data["results"])
        self.assertIn(serializer_play_title_2.data, res.data["results"])
        self.assertNotIn(serializer_play_title_3.data, res.data["results"])


class AuthorizedPlayTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)
        self.play_data = {
            "title": "Test title",
            "description": "Test description",
            "actors": [],
            "genres": [],
        }

    def test_plays_list(self):
        actors = [ActorFactory() for _ in range(2)]
        genres = [GenreFactory() for _ in range(2)]
        PlayFactory(actors=actors, genres=genres)

        res = self.client.get(PLAY_URL)
        plays = Play.objects.all()
        serializer = PlaySerializer(plays, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), len(serializer.data))

    def test_not_admin_can_not_create_play(self):
        res = self.client.post(PLAY_URL, self.play_data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Play.objects.count(), 0)

    def test_admin_can_create_play(self):
        admin_user = UserFactory(is_staff=True)
        self.client.force_authenticate(admin_user)
        res = self.client.post(PLAY_URL, self.play_data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Play.objects.count(), 1)
