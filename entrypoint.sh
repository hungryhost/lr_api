#!/bin/sh
python manage.py collectstatic --noinput
python manage.py clear_cache
python manage.py reset_schema
python manage.py reset_db

python manage.py makemigrations userAccount
python manage.py makemigrations properties
python manage.py migrate --noinput
echo "from django.contrib.auth.models import User;
User.objects.filter(email='$DJANGO_ADMIN_EMAIL').delete();
User.objects.create_superuser('$DJANGO_ADMIN_USER', '$DJANGO_ADMIN_EMAIL', '$DJANGO_ADMIN_PASSWORD')" | python manage.py shell

exec "$@"
