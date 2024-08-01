from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import Genre
from theatre.serializers import GenreSerializer
from theatre.tests.factories import UserFactory, GenreFactory, ActorFactory

GENRE_URL = reverse("theatre:genre-list")


class UnauthorizedGenreTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_authentication_is_not_required(self):
        res = self.client.get(GENRE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class AuthorizedGenreTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)
        self.genre_data = {"name": "Test name"}

    def test_genres_list(self):
        GenreFactory()

        res = self.client.get(GENRE_URL)
        genres = Genre.objects.all()
        serializer = GenreSerializer(genres, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), len(serializer.data))

    def test_not_admin_can_not_create_genre(self):
        res = self.client.post(GENRE_URL, self.genre_data)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Genre.objects.count(), 0)

    def test_admin_can_create_genre(self):
        admin_user = UserFactory(is_staff=True)
        self.client.force_authenticate(admin_user)
        res = self.client.post(GENRE_URL, self.genre_data)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Genre.objects.count(), 1)
