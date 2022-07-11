FROM python:3.8-alpine

WORKDIR /app

COPY . /app

RUN pip3 install pylint==2.14.3

CMD ["./scripts/pylint.sh"]
