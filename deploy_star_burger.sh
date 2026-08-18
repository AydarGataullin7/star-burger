#!/bin/bash

set -e

echo "Starting deployment..."

cd /root/star-burger

source venv/bin/activate

echo "Updating code from GitHub..."
git pull

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Installing Node.js dependencies..."
npm install

echo "Building frontend..."
./node_modules/.bin/parcel build bundles-src/index.js --dist-dir bundles --public-url="./"

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Applying database migrations..."
python manage.py migrate

echo "Restarting Gunicorn..."
systemctl restart star-burger

echo "Notifying Rollbar about deployment..."
COMMIT_HASH=$(git rev-parse HEAD)
ROLLBAR_TOKEN=$(grep ROLLBAR_DEPLOY_TOKEN ~/star-burger/.env | cut -d '=' -f2)

curl -X POST https://api.rollbar.com/api/1/deploy/ \
  -H "Content-Type: application/json" \
  -d "{
        \"access_token\": \"$ROLLBAR_TOKEN\",
        \"environment\": \"production\",
        \"revision\": \"$COMMIT_HASH\",
        \"local_username\": \"root\",
        \"comment\": \"Deploy via script\"
      }"

echo "Rollbar notified!"
echo "Deployment complete!"
