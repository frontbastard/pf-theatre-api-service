from io import BytesIO

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import Play
from theatre.serializers import (
    PlaySerializer,
    PlayListSerializer,
    PlayDetailSerializer,
)
from theatre.tests.factories import (
    UserFactory,
    PlayFactory,
    ActorFactory,
    GenreFactory,
)

PLAY_URL = reverse("theatre:play-list")


def create_test_image():
    file_content = BytesIO(
        b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82'
    )

    return SimpleUploadedFile(
        "test_image.png", file_content.getvalue(), content_type="image/png"
    )


def create_payload():
    genres = GenreFactory.create_batch(size=3)
    actors = ActorFactory.create_batch(size=3)

    return {
        "title": "Test title",
        "description": "Test description",
        "genres": [genre.id for genre in genres],
        "actors": [actor.id for actor in actors],
        "image": create_test_image(),
    }


def detail_url(id):
    return reverse("theatre:play-detail", args=(id,))


class UnauthorizedPlayTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_authentication_is_not_required(self):
        res = self.client.get(PLAY_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_filter_plays_by_genres(self):
        genre_1 = GenreFactory()
        genre_2 = GenreFactory()
        play_with_genre_1 = PlayFactory(genres=[genre_1])
        play_with_genre_2 = PlayFactory(genres=[genre_2])
        play_without_genres = PlayFactory(genres=[])

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
        play_title_1 = PlayFactory(title="Test_1 Title")
        play_title_2 = PlayFactory(title="Test_2 Title")
        play_title_3 = PlayFactory(title="Another Title")

        res = self.client.get(PLAY_URL, {"title": "test"})

        serializer_play_title_1 = PlayListSerializer(play_title_1)
        serializer_play_title_2 = PlayListSerializer(play_title_2)
        serializer_play_title_3 = PlayListSerializer(play_title_3)

        self.assertIn(serializer_play_title_1.data, res.data["results"])
        self.assertIn(serializer_play_title_2.data, res.data["results"])
        self.assertNotIn(serializer_play_title_3.data, res.data["results"])

    def test_retrieve_play_detail(self):
        play = PlayFactory()
        url = detail_url(play.id)
        res = self.client.get(url)
        serializer = PlayDetailSerializer(play)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_play_forbidden(self):
        payload = create_payload()

        res = self.client.post(PLAY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


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

    def test_not_admin_can_not_create_play(self):
        payload = create_payload()

        res = self.client.post(PLAY_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Play.objects.count(), 0)


class AdminPlayTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory(is_staff=True)
        self.client.force_authenticate(self.user)

    def test_admin_can_create_play(self):
        payload = create_payload()

        res = self.client.post(PLAY_URL, payload)

        play = Play.objects.get(pk=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Play.objects.count(), 1)
        self.assertTrue(play.image)

        for key, value in payload.items():
            if key == "image":
                self.assertTrue(bool(getattr(play, key)))
                self.assertTrue(getattr(play, key).name.endswith(".png"))
            elif key in ["genres", "actors"]:
                self.assertEqual(
                    set(value),
                    set(getattr(play, key).values_list("id", flat=True))
                )
            else:
                self.assertEqual(value, getattr(play, key))
