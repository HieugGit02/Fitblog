#!/bin/bash
set -e

echo "Running Django migrations..."
python manage.py migrate --noinput

echo "Collecting static files..."
python manage.py collectstatic --clear --noinput

echo "Creating superuser (if not exists)..."
python manage.py shell << END
from django.contrib.auth.models import User
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@fitblog.local', 'admin123')
    print("Superuser 'admin' created")
else:
    print("Superuser 'admin' already exists")
END

echo "Migrations and setup complete!"
