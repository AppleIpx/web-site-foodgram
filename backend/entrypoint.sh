#! /bin/bash

python3 manage.py makemigrations users

python3 manage.py makemigrations web_site

python3 manage.py migrate --no-input

python3 manage.py collectstatic --no-input

#python3 manage.py filling_db

gunicorn foodgram.wsgi:application --bind 0.0.0.0:8000