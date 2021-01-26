#!/bin/sh
python manage.py collectstatic --noinput
python manage.py clear_cache

python manage.py migrate --noinput

exec "$@"
