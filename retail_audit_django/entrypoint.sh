#!/bin/bash

# Exit immediately if a command exits with a non-zero status.
set -e

echo "--> Applying database migrations..."
python manage.py makemigrations
python manage.py migrate

echo "--> Checking/Creating superuser..."
# This Python script checks if the user exists. If not, it creates one.
python manage.py shell -c "
from django.contrib.auth import get_user_model;
User = get_user_model();
username = '$DJANGO_SUPERUSER_USERNAME';
email = '$DJANGO_SUPERUSER_EMAIL';
password = '$DJANGO_SUPERUSER_PASSWORD';

if not User.objects.filter(username=username).exists():
    print(f'Creating superuser: {username}');
    User.objects.create_superuser(username, email, password);
else:
    print(f'Superuser {username} already exists.');
"

echo "--> Starting server..."
exec "$@"
