FROM python:3.10
WORKDIR /stt
COPY requirements.txt /stt/
RUN apt-get update && apt-get install -y ffmpeg libavcodec-extra libssl-dev libasound2
RUN pip install -r requirements.txt
COPY . /stt
CMD python stt.py