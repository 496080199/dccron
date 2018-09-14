#!/bin/sh
if [[ $1 -eq 1 ]];
then
  python manage.py makemigrations
  python manage.py migrate
  python manage.py loaddata initial_data.yaml
fi
nginx&&gunicorn  -b 0.0.0.0:8000 dccron.wsgi:application