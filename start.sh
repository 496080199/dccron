#!/bin/sh

gunicorn  -b 127.0.0.1:8000 dccron.wsgi:application