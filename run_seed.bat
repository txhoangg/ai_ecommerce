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
echo [3/4] Syncing products and knowledge into ai-service...
docker compose exec ai-service python manage.py sync_products_to_faiss
docker compose exec ai-service python manage.py seed_knowledge_to_faiss

echo.
echo [4/4] Training behavior model in ai-service...
docker compose exec ai-service python manage.py train_behavior_model --epochs 10

echo.
echo ============================================================
echo  DONE! AI system fully initialized.
echo  Access: http://localhost:8000
echo  - Chat AI: http://localhost:8000/chat/
echo  - Recommend: http://localhost:8000/books/recommendations/
echo ============================================================
pause
