FROM python:3.15-slim-trixie

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY app/ ./app/

EXPOSE 8080

ENTRYPOINT [ "fastapi", "run", "app/main.py"]
