FROM python:3.8-slim

RUN apt-get update && apt-get install -y ffmpeg

RUN mkdir -p /app/backend /app/resources/video /app/resources/music
RUN adduser app && chown -R app:app /app

WORKDIR /app/backend

USER app

COPY requirements.txt .
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE 1337

WORKDIR /app

CMD [ "python", "backend/src/app.py" ]