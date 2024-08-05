import sys

from decouple import config, UndefinedValueError
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.db.utils import IntegrityError


class Command(BaseCommand):
    help = "Create a superuser if none exist"  # noqa: VNE003

    def handle(self, *args, **options):
        try:
            email = config("SUPERUSER_EMAIL")
            password = config("SUPERUSER_PASSWORD")

            if not email or not password:
                raise UndefinedValueError
        except UndefinedValueError:
            self.stdout.write(
                self.style.ERROR(
                    "ERROR: SUPERUSER_EMAIL or "
                    "SUPERUSER_PASSWORD not set in .env"
                )
            )
            sys.exit(1)

        user = get_user_model()
        if not user.objects.filter(is_superuser=True).exists():

            try:
                user.objects.create_superuser(
                    email=email,
                    password=password,
                )
                self.stdout.write(self.style.SUCCESS("Superuser created."))
            except IntegrityError:
                self.stdout.write(
                    self.style.WARNING("Superuser already exists.")
                )
