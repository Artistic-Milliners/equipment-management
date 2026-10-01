#!/bin/bash

# Exit on error
set -e

echo "================================================"
echo "Starting EMS Application Entrypoint Script"
echo "================================================"

# Wait for PostgreSQL to be ready
echo "Waiting for PostgreSQL to be ready..."
while ! pg_isready -h "${DB_HOST:-db}" -p "${DB_PORT:-5432}" -U "${DB_USER:-zohaib}" -d "${DB_NAME:-ems}" > /dev/null 2>&1; do
    echo "PostgreSQL is unavailable - sleeping"
    sleep 2
done
echo "✓ PostgreSQL is ready!"

# Run database migrations
echo "Running database migrations..."
python manage.py migrate --noinput
echo "✓ Migrations completed!"

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput --clear
echo "✓ Static files collected!"

# Create superuser if it doesn't exist (optional)
# echo "Creating superuser if not exists..."
# python manage.py shell << END
# from django.contrib.auth import get_user_model
# User = get_user_model()
# if not User.objects.filter(username='admin').exists():
#     User.objects.create_superuser('admin', 'admin@example.com', 'admin')
#     print('Superuser created!')
# else:
#     print('Superuser already exists.')
# END

echo "================================================"
echo "EMS Application is ready to start!"
echo "================================================"

# Execute the main command (passed as arguments to this script)
exec "$@"
