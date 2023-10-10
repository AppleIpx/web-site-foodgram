FROM python:3.9

RUN mkdir /app
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt --no-cache-dir
RUN chmod +x entrypoint.sh

ENTRYPOINT ["/app/entrypoint.sh"]
