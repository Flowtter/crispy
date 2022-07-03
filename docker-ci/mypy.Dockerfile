FROM python:3.8-alpine

WORKDIR /app

COPY . /app

RUN pip3 install mypy

CMD ["./scripts/mypy.sh"]
