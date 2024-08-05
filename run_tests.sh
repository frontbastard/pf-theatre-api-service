#!/bin/bash
docker-compose run --rm test python manage.py test -v 2 --settings=theatre_service.settings_test --keepdb
