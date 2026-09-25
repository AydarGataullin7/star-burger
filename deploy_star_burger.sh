#!/bin/bash

set -e

echo "=== Deploy started ==="

cd /root/star-burger

echo "--- 1. Pulling latest code from GitHub ---"
git pull

echo "--- 2. Stopping old containers ---"
docker compose -f docker-compose.yaml down

echo "--- 3. Building and starting new containers ---"
docker compose -f docker-compose.yaml up -d --build

echo "--- 4. Applying database migrations ---"
docker compose -f docker-compose.yaml exec -T backend python manage.py migrate

echo "--- 5. Collecting static files ---"
docker compose -f docker-compose.yaml exec -T backend python manage.py collectstatic --noinput

echo "--- 6. Notifying Rollbar about deployment ---"
COMMIT_HASH=$(git rev-parse HEAD)
ROLLBAR_TOKEN=$(grep ROLLBAR_ACCESS_TOKEN .env | cut -d '=' -f2)

curl -s -X POST https://api.rollbar.com/api/1/deploy/ \
  -H "Content-Type: application/json" \
  -d "{
        \"access_token\": \"$ROLLBAR_TOKEN\",
        \"environment\": \"production\",
        \"revision\": \"$COMMIT_HASH\",
        \"local_username\": \"root\",
        \"comment\": \"Deploy via script\"
      }" > /dev/null

echo "Rollbar notified."

echo "=== Deployment complete! ==="
