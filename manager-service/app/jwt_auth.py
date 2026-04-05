"""
JWT Authentication for microservice - Assignment 06
Validates JWT tokens issued by the API Gateway.
"""

import jwt
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

SHARED_SECRET = "super-secret-jwt-key"


class JWTAuthentication(BaseAuthentication):
    """
    Authenticate requests using a JWT Bearer token from the API Gateway.
    - If Authorization header is present → validate token (raise 401 on invalid/expired).
    - If Authorization header is absent → return None (allow anonymous / inter-service calls).
    """

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return None  # No token → anonymous, allowed for inter-service calls

        token = auth_header[7:]
        try:
            payload = jwt.decode(token, SHARED_SECRET, algorithms=['HS256'])
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired.')
        except jwt.InvalidTokenError:
            raise AuthenticationFailed('Invalid token.')

        # Return a simple user-like object carrying role info
        return (SimpleJWTUser(payload), token)


class SimpleJWTUser:
    """Lightweight user object attached to request.user when JWT is valid."""

    def __init__(self, payload):
        self.id = payload.get('user_id')
        self.role = payload.get('role')
        self.is_authenticated = True

    def __str__(self):
        return f"JWTUser(id={self.id}, role={self.role})"
