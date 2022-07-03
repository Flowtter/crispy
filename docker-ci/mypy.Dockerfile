FROM python:3.8-alpine

WORKDIR /app

COPY . /app

RUN pip3 install mypy
RUN pip3 install -r backend/requirements.txt

CMD ["./scripts/mypy.sh"]
