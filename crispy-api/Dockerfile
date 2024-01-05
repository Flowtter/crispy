FROM python:3.10-slim
WORKDIR /app
RUN apt-get -y update
RUN apt-get install ffmpeg -y

COPY requirements.txt .
RUN pip install -r requirements.txt
COPY api api
COPY assets assets
COPY dataset dataset
COPY settings.json settings.json
EXPOSE 7821
CMD ["python", "-m", "api"]
