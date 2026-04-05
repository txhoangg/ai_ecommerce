FROM python:3.11-slim

WORKDIR /app

# Install build deps for torch/chromadb
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8011

CMD ["sh", "-c", "until python -c \"import socket; s=socket.socket(); s.connect(('postgres',5432)); s.close()\" 2>/dev/null; do echo 'Waiting for PostgreSQL...'; sleep 2; done && python manage.py makemigrations app --noinput && python manage.py migrate --noinput && python manage.py runserver 0.0.0.0:8011"]
