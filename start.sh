#!/bin/sh
if [[ $DCINIT -eq 1 ]];
then
  python manage.py makemigrations
  python manage.py migrate
  python manage.py loaddata initial_data.yaml
else
    echo "未定义DCINIT"
fi
nginx&&gunicorn  -b 0.0.0.0:8000 dccron.wsgi:application