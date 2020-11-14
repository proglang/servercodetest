FROM python:3.9-alpine

# set work directory
WORKDIR /usr/src/plugin

COPY . /usr/src/plugin/

RUN pip install --upgrade pip && pip install -r requirements.txt

#https://stackoverflow.com/questions/29663459/python-app-does-not-print-anything-when-running-detached-in-docker
CMD ["python3", "-u", "main.py"]