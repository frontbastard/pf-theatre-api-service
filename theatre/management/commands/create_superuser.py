from decouple import config
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db.utils import IntegrityError


class Command(BaseCommand):
    help = "Create a superuser if none exist"  # noqa: VNE003

    def handle(self, *args, **options):
        user = get_user_model()
        if not user.objects.filter(is_superuser=True).exists():
            try:
                user.objects.create_superuser(
                    email=config("SUPERUSER_EMAIL"),
                    password=config("SUPERUSER_PASSWORD"),
                )
                self.stdout.write(self.style.SUCCESS("Superuser created."))
            except IntegrityError:
                self.stdout.write(
                    self.style.WARNING("Superuser already exists.")
                )
