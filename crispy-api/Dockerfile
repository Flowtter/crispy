FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY api api
EXPOSE 8000
CMD ["python", "-m", "api"]
