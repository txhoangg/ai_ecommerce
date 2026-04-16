FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir torch==2.0.1 --index-url https://download.pytorch.org/whl/cpu
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
EXPOSE 8013
CMD ["sh", "-c", "python manage.py migrate && python manage.py sync_products_to_faiss && python manage.py seed_knowledge_to_faiss && python manage.py train_behavior_model --epochs 10 && python manage.py runserver 0.0.0.0:8013"]
