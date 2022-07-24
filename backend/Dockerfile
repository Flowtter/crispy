FROM python:3.8-slim

RUN apt-get update && apt-get install -y ffmpeg

RUN mkdir -p /app/backend /app/resources/video /app/resources/music 

RUN echo '{ \
    "neural-network": { \
    "confidence": 0.8\
    },\
    "clip": {\
    "framerate": 8,\
    "second-before": 3,\
    "second-after": 2,\
    "second-between-kills": 1\
    },\
    "filters": {\
    "saturation": 1.3\
    },\
    "clips": {\
    "nice headshot on reyna": {\
    "saturation": 0.5,\
    "hflip": true\
    }\
    }\
    }' >>  /app/settings.json

RUN adduser app && chown -R app:app /app

WORKDIR /app/backend

USER app

COPY requirements.txt .
RUN python -m pip install --upgrade pip && pip install -r requirements.txt

COPY . .

EXPOSE 1337

WORKDIR /app

CMD [ "python", "backend/src/app.py" ]