#!/bin/sh
if [[ $DCINIT -eq 1 ]];
then
  python manage.py makemigrations
  python manage.py migrate
  python manage.py loaddata initial_data.yaml
  echo "数据初始化完成"
else
    echo "无需初始化"
fi
nginx&&gunicorn  -b 0.0.0.0:8000 dccron.wsgi:application