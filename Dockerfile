# syntax=docker/dockerfile:1

FROM python:3.10-slim-buster

ENV TZ="Europe/Bratislava"

WORKDIR /app

COPY install-packages.sh .
RUN ./install-packages.sh
COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

COPY . /app

RUN mkdir /app/data
RUN mkdir /app/data/glucose
RUN mkdir /app/data/insulin
RUN mkdir /app/data/dexcom_export
EXPOSE 80

CMD ["gunicorn", "src.app:server", "-b", ":80"]