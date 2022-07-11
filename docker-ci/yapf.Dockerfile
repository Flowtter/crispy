FROM python:3.8-alpine

WORKDIR /app

COPY . /app

RUN pip3 install yapf==0.32.0

CMD ["./scripts/yapf.sh"]
