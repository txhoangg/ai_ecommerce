FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8001

CMD ["sh", "-c", "until python -c \"import socket; s=socket.socket(); s.connect(('mysql',3306)); s.close()\" 2>/dev/null; do echo 'Waiting for MySQL...'; sleep 2; done && python manage.py makemigrations && python manage.py migrate && python manage.py runserver 0.0.0.0:8001"]
