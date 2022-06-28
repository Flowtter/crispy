FROM python:3.7-slim

RUN apt-get update
RUN apt-get install ffmpeg libsm6 libxext6 -y

COPY requirements.txt requirements.txt
RUN pip3 install -r requirements.txt

RUN adduser --disabled-password --gecos '' user

WORKDIR /app

RUN chown -R user:user /app
USER user

COPY . /app

EXPOSE 1337

CMD [ "uvicorn", "src.app:app", "--reload", "--host", "0.0.0.0", "--port", "1337" ]
