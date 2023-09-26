#FROM python:3.9
#
#RUN mkdir /app
#WORKDIR /app
#
#COPY requirements.txt /app/
#RUN pip install --no-cache-dir -r requirements.txt
#
#COPY . /app/
#
## Установление права на выполнение для entrypoint.sh
#RUN chmod +x entrypoint.sh
#
#EXPOSE 8000
#
#ENTRYPOINT ["/app/entrypoint.sh"]
#-----------------------------------------

#FROM python:3.9
#
## Устанавливаем переменные среды
#ENV PYTHONDONTWRITEBYTECODE 1
#ENV PYTHONUNBUFFERED 1
#
#WORKDIR /app
#
#COPY ./requirements.txt /app/
#RUN pip install --no-cache-dir -r requirements.txt
#RUN pip install gunicorn
#
## Копируем весь проект внутрь контейнера
#COPY . /app/
#
#RUN python manage.py makemigrations users
#
#RUN python manage.py makemigrations web_site
#
##RUN python manage.py migrate
#
##RUN python manage.py migrate --no-input
#
#RUN python manage.py collectstatic --no-input

#CMD ["python", "manage.py", "migrate"]
#CMD ["gunicorn", "foodgram.wsgi:application", "--bind", "0.0.0.0:8000"]
#CMD ["python", "manage.py", "migrate", "&&", "gunicorn", "foodgram.wsgi:application", "--bind", "0.0.0.0:8000"]

#-----------------------------------

FROM python:3.9

RUN mkdir /app
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt --no-cache-dir
RUN chmod +x entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
