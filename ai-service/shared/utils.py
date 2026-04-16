import logging
import requests
from typing import Optional
from django.conf import settings

logger = logging.getLogger(__name__)


def fetch_product(product_id: int, timeout: int = 5) -> Optional[dict]:
    """Fetch a single product from product-service. Returns None on failure."""
    try:
        resp = requests.get(
            f"{settings.PRODUCT_SERVICE_URL}/products/{product_id}/",
            timeout=timeout,
        )
        if resp.status_code == 200:
            return resp.json()
        logger.debug(f"fetch_product {product_id}: HTTP {resp.status_code}")
    except requests.exceptions.ConnectionError:
        logger.warning(f"Product service not reachable (fetch_product {product_id})")
    except requests.exceptions.Timeout:
        logger.warning(f"Product service timeout (fetch_product {product_id})")
    except Exception as e:
        logger.error(f"fetch_product error: {e}")
    return None


def fetch_products(params: dict = None, timeout: int = 10) -> list:
    """Fetch a list of products from product-service. Returns empty list on failure."""
    try:
        request_params = dict(params or {})
        if 'limit' in request_params and 'page_size' not in request_params:
            request_params['page_size'] = request_params.pop('limit')
        resp = requests.get(
            f"{settings.PRODUCT_SERVICE_URL}/products/",
            params=request_params,
            timeout=timeout,
        )
        if resp.status_code == 200:
            data = resp.json()
            return data.get('results', data) if isinstance(data, dict) else data
        logger.debug(f"fetch_products: HTTP {resp.status_code}")
    except requests.exceptions.ConnectionError:
        logger.warning("Product service not reachable (fetch_products)")
    except requests.exceptions.Timeout:
        logger.warning("Product service timeout (fetch_products)")
    except Exception as e:
        logger.error(f"fetch_products error: {e}")
    return []


def paginate_response(data: list, page: int = 1, page_size: int = 20) -> dict:
    """Simple in-memory pagination helper."""
    total = len(data)
    start = (page - 1) * page_size
    end = start + page_size
    return {
        'count': total,
        'page': page,
        'page_size': page_size,
        'total_pages': (total + page_size - 1) // page_size,
        'results': data[start:end],
    }


def safe_int(value, default: int = 0) -> int:
    """Safely convert a value to int."""
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def safe_float(value, default: float = 0.0) -> float:
    """Safely convert a value to float."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
