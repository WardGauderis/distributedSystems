FROM python:alpine

WORKDIR /usr/src/app
RUN apk update && \
    apk add --virtual build-deps gcc python3-dev musl-dev postgresql-dev
RUN pip install flask flask-sqlalchemy psycopg2

CMD python run.py