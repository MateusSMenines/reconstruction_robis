FROM python:3.7-slim

SHELL [ "/bin/bash" , "-c" ]

RUN apt-get update

COPY requirements.txt .
RUN pip3 install -r requirements.txt \
    && pip3 install --upgrade protobuf==3.20.0 

COPY requirements_yolo.txt .
RUN pip3 install -r requirements_yolo.txt

COPY src/ opt/src
COPY etc/ opt/etc

RUN apt update
RUN apt install -y libgl1-mesa-glx
RUN apt-get install ffmpeg libsm6 libxext6  -y


WORKDIR opt/src
