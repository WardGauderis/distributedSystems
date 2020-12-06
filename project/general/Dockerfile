FROM python:alpine

WORKDIR /usr/src/app
RUN apk update && \
    apk add --virtual build-deps gcc python3-dev musl-dev postgresql-dev
COPY requirements.txt .
RUN pip install -r requirements.txt

CMD python run.py