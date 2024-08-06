from datetime import timedelta

from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from theatre.models import Performance
from theatre.serializers import (
    PerformanceSerializer,
    PerformanceDetailSerializer,
)
from theatre.tests.factories import (
    UserFactory,
    PerformanceFactory,
    PlayFactory,
    TheatreHallFactory,
)

PERFORMANCE_URL = reverse("theatre:performance-list")


def create_payload():
    play = PlayFactory()
    theatre_hall = TheatreHallFactory()

    return {
        "play": play.id,
        "theatre_hall": theatre_hall.id,
        "show_time": timezone.now() + timezone.timedelta(days=1),
    }


def detail_url(id):
    return reverse("theatre:performance-detail", args=(id,))


class UnauthorizedPerformanceTest(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_authentication_is_not_required(self):
        res = self.client.get(PERFORMANCE_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)

    def test_retrieve_performance_detail(self):
        performance = PerformanceFactory()
        url = detail_url(performance.id)
        res = self.client.get(url)
        serializer = PerformanceDetailSerializer(performance)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_performance_forbidden(self):
        payload = create_payload()

        res = self.client.post(PERFORMANCE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthorizedPerformanceTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory()
        self.client.force_authenticate(self.user)

    def test_performances_list(self):
        PerformanceFactory()

        res = self.client.get(PERFORMANCE_URL)
        performances = Performance.objects.all()
        serializer = PerformanceSerializer(performances, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data["results"]), len(serializer.data))

    def test_not_admin_can_not_create_performance(self):
        payload = create_payload()

        res = self.client.post(PERFORMANCE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(Performance.objects.count(), 0)


class AdminPerformanceTest(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = UserFactory(is_staff=True)
        self.client.force_authenticate(self.user)

    def test_admin_can_create_performance(self):
        payload = create_payload()

        res = self.client.post(PERFORMANCE_URL, payload)

        performance = Performance.objects.get(pk=res.data["id"])

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Performance.objects.count(), 1)
        self.assertEqual(payload["play"], performance.play.id)
        self.assertEqual(payload["theatre_hall"], performance.theatre_hall.id)
        self.assertAlmostEqual(
            payload["show_time"], performance.show_time, delta=timedelta(seconds=1)
        )
