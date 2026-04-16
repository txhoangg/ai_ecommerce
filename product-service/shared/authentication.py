import jwt
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed


class SimpleUser:
    """Minimal user-like object constructed from JWT payload."""

    def __init__(self, payload: dict):
        self.id = payload.get('user_id') or payload.get('id') or payload.get('sub')
        self.username = payload.get('username', '')
        self.email = payload.get('email', '')
        self.is_staff = payload.get('is_staff', False)
        self.is_superuser = payload.get('is_superuser', False)
        self.payload = payload
        self.is_authenticated = True
        self.is_anonymous = False
        self.is_active = True

    def __str__(self):
        return self.username or str(self.id)


class JWTAuthentication(BaseAuthentication):

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header:
            return None

        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != 'bearer':
            return None

        token = parts[1]
        try:
            secret_key = getattr(settings, 'JWT_SECRET_KEY', 'super-secret-jwt-key')
            algorithm = getattr(settings, 'JWT_ALGORITHM', 'HS256')
            payload = jwt.decode(
                token,
                secret_key,
                algorithms=[algorithm]
            )
            user = SimpleUser(payload)
            return (user, token)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired')
        except jwt.InvalidTokenError as e:
            raise AuthenticationFailed(f'Invalid token: {str(e)}')

    def authenticate_header(self, request):
        return 'Bearer realm="product-service"'
