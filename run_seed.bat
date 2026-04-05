@echo off
echo ============================================================
echo  BOOKSTORE AI-ECOMMERCE - SEED + AI INIT
echo ============================================================

echo.
echo [1/4] Copying seed script into api-gateway container...
docker compose cp create_sample_data.py api-gateway:/tmp/create_sample_data.py

echo.
echo [2/4] Running seed script (creating books, customers, orders, ratings)...
docker compose exec api-gateway python /tmp/create_sample_data.py

echo.
echo [3/4] Building AI Knowledge Base (books + service FAQ)...
docker compose exec api-gateway python -c "import requests, jwt, datetime; token=jwt.encode({'sub':'seed','role':'service','exp':datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(hours=2)},'super-secret-jwt-key',algorithm='HS256'); h={'Authorization':'Bearer '+token}; r=requests.post('http://recommender-ai-service:8011/api/ai/kb/build/',headers=h,timeout=60); print('KB build:', r.status_code, r.text[:400])"

echo.
echo [4/4] Training Deep Learning model (NCF) from purchase + rating data...
docker compose exec api-gateway python -c "import requests, jwt, datetime; token=jwt.encode({'sub':'seed','role':'service','exp':datetime.datetime.now(datetime.timezone.utc)+datetime.timedelta(hours=2)},'super-secret-jwt-key',algorithm='HS256'); h={'Authorization':'Bearer '+token}; r=requests.post('http://recommender-ai-service:8011/api/ai/model/train/',headers=h,timeout=120); print('Model train:', r.status_code, r.text[:400])"

echo.
echo ============================================================
echo  DONE! AI system fully initialized.
echo  Access: http://localhost:8000
echo  - Chat AI: http://localhost:8000/chat/
echo  - Recommend: http://localhost:8000/books/recommendations/
echo ============================================================
pause
