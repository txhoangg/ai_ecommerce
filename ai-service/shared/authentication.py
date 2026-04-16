import jwt
import logging
from django.conf import settings
from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

logger = logging.getLogger(__name__)


class JWTAuthentication(BaseAuthentication):
    """
    JWT-based authentication for internal service calls.
    Reads the 'Authorization: Bearer <token>' header.
    Returns (payload_dict, token) on success, or None to skip this authenticator.
    """

    def authenticate(self, request):
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if not auth_header.startswith('Bearer '):
            return None

        token = auth_header.split(' ', 1)[1].strip()
        if not token:
            return None

        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=['HS256'],
            )
            return (payload, token)
        except jwt.ExpiredSignatureError:
            raise AuthenticationFailed('Token has expired.')
        except jwt.InvalidTokenError as e:
            logger.debug(f"Invalid JWT token: {e}")
            return None

    def authenticate_header(self, request):
        return 'Bearer'


def get_user_id_from_request(request) -> int | None:
    """
    Helper to extract user_id from a JWT-authenticated request or from request data/params.
    Returns None if not found.
    """
    # From JWT auth
    if hasattr(request, 'user') and isinstance(request.user, dict):
        return request.user.get('user_id') or request.user.get('id')

    # From request body (for POST)
    if hasattr(request, 'data') and request.data:
        uid = request.data.get('user_id') or request.data.get('customer_id')
        if uid is not None:
            try:
                return int(uid)
            except (ValueError, TypeError):
                pass

    # From query params (for GET)
    uid = request.query_params.get('user_id') or request.query_params.get('customer_id')
    if uid is not None:
        try:
            return int(uid)
        except (ValueError, TypeError):
            pass

    return None
