# pull official base image
FROM python:3.8.0-alpine

# set work directory
WORKDIR /usr/src/

# set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

#openrc
RUN apk update && apk add --no-cache build-base nginx mysql-client mariadb-connector-c-dev docker-cli

# install dependencies
COPY ./docker/requirements.txt /usr/src/requirements.txt
RUN pip install --upgrade pip && pip install -r requirements.txt
RUN apk del build-base


#Copy Files
COPY ./docker/start.py  /usr/src/start.py
COPY ./docker/settings.py  /usr/src/settings.py
COPY ./docker/nginx.conf /usr/src/nginx.conf

# copy project
COPY . /usr/src/app/
CMD ["python3", "start.py"]
