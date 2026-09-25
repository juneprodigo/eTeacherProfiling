#!/bin/sh
set -e

echo "=== eTeacher Profiling (CES / DEPED) Backend Entrypoint ==="

# Wait for PostgreSQL database to be reachable
DB_TARGET_HOST="${DB_HOST:-db}"
DB_TARGET_PORT="${DB_PORT:-5432}"

echo "Waiting for PostgreSQL at ${DB_TARGET_HOST}:${DB_TARGET_PORT}..."
while ! nc -z "${DB_TARGET_HOST}" "${DB_TARGET_PORT}"; do
  sleep 0.5
done
echo "PostgreSQL is reachable!"

# Run Django migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Seed default users if not yet present
echo "Checking and seeding default administrative and faculty accounts..."
python seed_users.py || true

# Seed reference libraries (Training, Voluntary Work, Experience, Eligibility)
echo "Checking and seeding reference dropdown libraries..."
python manage.py seed_libraries || true

# Seed standard faculty attendance shift & records
echo "Checking and seeding default shift schedules..."
python seed_attendance.py || true

# Collect static files into staticfiles directory
echo "Collecting static files..."
python manage.py collectstatic --noinput || true

echo "Django preparation complete. Launching server..."
exec "$@"
