FROM python:3.8-alpine

WORKDIR /app

COPY . /app

RUN pip3 install pylint
RUN pip3 install -r backend/requirements.txt

CMD ["./scripts/pylint.sh"]
