FROM python:3.7-slim

SHELL [ "/bin/bash" , "-c" ]

RUN apt-get update

COPY requirements.txt .
RUN pip3 install -r requirements.txt \
    && pip3 install --upgrade protobuf==3.20.0 

COPY src/ opt/src
COPY etc/ opt/etc

RUN apt update


WORKDIR opt/src
