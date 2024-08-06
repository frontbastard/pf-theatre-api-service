#!/bin/bash

cleanup() {
    docker-compose -f docker-compose.test.yaml down
}

trap cleanup EXIT

docker-compose -f docker-compose.test.yaml up -d test_db
docker-compose -f docker-compose.test.yaml run --rm test
