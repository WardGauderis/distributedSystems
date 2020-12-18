FROM python:alpine

WORKDIR /usr/src/app
RUN apk update && \
    apk add --virtual build-deps gcc python3-dev musl-dev postgresql-dev
COPY . .
RUN pip install -r requirements.txt

#CMD FLASK_APP=. flask run -h 0.0.0.0
CMD cd .. && gunicorn -b 0.0.0.0:5000 'app:create_app()'