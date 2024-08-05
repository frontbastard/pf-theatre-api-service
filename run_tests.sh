#!/bin/bash
docker-compose run --rm test python manage.py test --settings=theatre_service.settings_test
