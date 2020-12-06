FROM python:alpine

WORKDIR /usr/src/app
RUN apk update && \
    apk add --virtual build-deps gcc python3-dev musl-dev postgresql-dev
COPY . ./general
RUN pip install -r general/requirements.txt

CMD python service/run.py