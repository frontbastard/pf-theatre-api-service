from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import Reservation
from theatre.serializers import ReservationSerializer
from theatre.tests.factories import UserFactory, ReservationFactory

RESERVATION_URL = reverse("theatre:reservation-list")


class UnauthorizedReservationTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_authentication_is_required(self):
        res = self.client.get(RESERVATION_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedReservationTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_reservations_list(self):
        ReservationFactory(user=self.user)

        res = self.client.get(RESERVATION_URL)
        reservations = Reservation.objects.all()
        serializer = ReservationSerializer(reservations, many=True)

        self.assertEqual(res.data["results"], serializer.data)
