from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import TheatreHall
from theatre.serializers import TheatreHallSerializer
from theatre.tests.factories import UserFactory, TheatreHallFactory

THEATRE_HALL_URL = reverse("theatre:theatrehall-list")
PAYLOAD = {
    "name": "Test",
    "rows": 5,
    "seats_in_row": 10,
}


class UnauthorizedTheatreHallTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_authentication_is_not_required(self):
        res = self.client.get(THEATRE_HALL_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)


class AuthorizedTheatreHallTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_theatre_halls_list(self):
        TheatreHallFactory()

        res = self.client.get(THEATRE_HALL_URL)
        theatre_halls = TheatreHall.objects.all()
        serializer = TheatreHallSerializer(theatre_halls, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), len(serializer.data))

    def test_not_admin_can_not_create_theatre_hall(self):
        res = self.client.post(THEATRE_HALL_URL, PAYLOAD)
        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(TheatreHall.objects.count(), 0)


class AdminTheatreHallTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory(is_staff=True)
        self.client.force_authenticate(self.user)

    def test_admin_can_create_play(self):
        res = self.client.post(THEATRE_HALL_URL, PAYLOAD)

        play = TheatreHall.objects.get(pk=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(TheatreHall.objects.count(), 1)

        for key in PAYLOAD:
            self.assertEqual(PAYLOAD[key], getattr(play, key))
