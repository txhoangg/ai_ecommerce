import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'ai-service-secret-key'
DEBUG = True
ALLOWED_HOSTS = ['*']

INSTALLED_APPS = [
    'django.contrib.contenttypes',
    'django.contrib.auth',
    'rest_framework',
    'corsheaders',
    'modules.graph',
    'modules.rag',
    'modules.behavior',
    'modules.recommendation',
]

MIDDLEWARE = [
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'config.urls'
CORS_ALLOW_ALL_ORIGINS = True

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DB_NAME', 'ai_db'),
        'USER': os.getenv('DB_USER', 'postgres'),
        'PASSWORD': os.getenv('DB_PASSWORD', 'postgres'),
        'HOST': os.getenv('DB_HOST', 'postgres'),
        'PORT': os.getenv('DB_PORT', '5432'),
    }
}

REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.AllowAny'],
}

# Neo4j
NEO4J_URI = os.getenv('NEO4J_URI', 'bolt://neo4j:7687')
NEO4J_USER = os.getenv('NEO4J_USER', 'neo4j')
NEO4J_PASSWORD = os.getenv('NEO4J_PASSWORD', 'password123')

# AI
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', '')
GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'gemini-3.1-flash-lite-preview')
GEMINI_REQUEST_TIMEOUT_SECONDS = int(os.getenv('GEMINI_REQUEST_TIMEOUT_SECONDS', '8'))
GEMINI_COOLDOWN_SECONDS = int(os.getenv('GEMINI_COOLDOWN_SECONDS', '60'))

# Service URLs
PRODUCT_SERVICE_URL = os.getenv('PRODUCT_SERVICE_URL', 'http://product-service:8012')
INTERACTION_SERVICE_URL = os.getenv('INTERACTION_SERVICE_URL', 'http://interaction-service:8006')

# FAISS
FAISS_INDEX_PATH = os.getenv('FAISS_INDEX_PATH', '/tmp/bookstore_faiss.index')
FAISS_METADATA_PATH = os.getenv('FAISS_METADATA_PATH', '/tmp/bookstore_faiss_metadata.pkl')

# Behavior model
BEHAVIOR_MODEL_PATH = os.getenv('BEHAVIOR_MODEL_PATH', '/tmp/behavior_lstm.pt')

JWT_SECRET = os.getenv('JWT_SECRET', 'super-secret-jwt-key')

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
}
