"""
API Gateway Middleware - Assignment 06
- JWT validation for protected routes
- Request/Response logging
- Rate limiting (simple in-memory)
"""

import jwt
import time
import logging
import threading
from collections import defaultdict
from django.http import JsonResponse
from django.conf import settings

logger = logging.getLogger('api_gateway')

SHARED_SECRET = "super-secret-jwt-key"

# Routes that require JWT validation (non-HTML, API-style checks)
# For HTML views, session-based auth is handled in each view.
# This middleware enforces JWT for any path prefixed with /api/
JWT_PROTECTED_PREFIXES = ['/api/']

# Routes fully exempt from all middleware checks
EXEMPT_PATHS = [
    '/health/',
    '/metrics/',
    '/static/',
    '/admin/',
    '/favicon.ico',
]

# ─── Rate Limiting ─────────────────────────────────────────────────────────────
# Simple token-bucket per IP: max 60 requests per minute
RATE_LIMIT_REQUESTS = 60
RATE_LIMIT_WINDOW = 60  # seconds

_rate_store = defaultdict(list)  # ip -> [timestamps]
_rate_lock = threading.Lock()


def is_rate_limited(ip):
    now = time.time()
    with _rate_lock:
        timestamps = _rate_store[ip]
        # Remove old timestamps outside the window
        _rate_store[ip] = [t for t in timestamps if now - t < RATE_LIMIT_WINDOW]
        if len(_rate_store[ip]) >= RATE_LIMIT_REQUESTS:
            return True
        _rate_store[ip].append(now)
        return False


def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded:
        return x_forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '127.0.0.1')


# ─── JWT Validation Helper ─────────────────────────────────────────────────────

def validate_jwt(token):
    """Decode and validate JWT token. Returns payload or None."""
    try:
        payload = jwt.decode(token, SHARED_SECRET, algorithms=['HS256'])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


# ─── Middleware Classes ────────────────────────────────────────────────────────

class RequestLoggingMiddleware:
    """Log every request with method, path, status code, and response time."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        from api_gateway.health import increment_request_count
        increment_request_count()

        start = time.time()
        ip = get_client_ip(request)

        response = self.get_response(request)

        duration_ms = int((time.time() - start) * 1000)
        logger.info(
            f"[{ip}] {request.method} {request.path} → {response.status_code} ({duration_ms}ms)"
        )
        response['X-Response-Time-Ms'] = str(duration_ms)
        return response


class RateLimitMiddleware:
    """Block IPs that exceed RATE_LIMIT_REQUESTS per RATE_LIMIT_WINDOW seconds."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        for exempt in EXEMPT_PATHS:
            if request.path.startswith(exempt):
                return self.get_response(request)

        ip = get_client_ip(request)
        if is_rate_limited(ip):
            logger.warning(f"[RateLimit] {ip} exceeded rate limit on {request.path}")
            return JsonResponse(
                {'error': 'Too many requests. Please slow down.'},
                status=429
            )
        return self.get_response(request)


class JWTAuthMiddleware:
    """
    Validate JWT token for /api/* paths.
    Attaches jwt_user to request if token is valid.
    For HTML views, session-based auth is used directly in each view.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only enforce JWT on /api/ prefixed paths
        needs_jwt = any(request.path.startswith(p) for p in JWT_PROTECTED_PREFIXES)

        if needs_jwt:
            auth_header = request.META.get('HTTP_AUTHORIZATION', '')
            token = None

            if auth_header.startswith('Bearer '):
                token = auth_header[7:]

            if token:
                payload = validate_jwt(token)
                if payload:
                    request.jwt_user = payload
                else:
                    return JsonResponse({'error': 'Invalid or expired token'}, status=401)
            else:
                return JsonResponse({'error': 'Authorization token required'}, status=401)

        return self.get_response(request)
