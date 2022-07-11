FROM python:3.8-alpine

WORKDIR /app

COPY . /app

RUN pip3 install mypy==0.961

CMD ["./scripts/mypy.sh"]
