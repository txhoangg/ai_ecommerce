import re
import unicodedata
from decimal import Decimal, InvalidOperation
from typing import Any, Optional


def slugify(text: str) -> str:
    text = unicodedata.normalize('NFKD', text)
    text = text.encode('ascii', 'ignore').decode('ascii')
    text = re.sub(r'[^\w\s-]', '', text).strip().lower()
    text = re.sub(r'[-\s]+', '-', text)
    return text


def to_decimal(value: Any, default: Decimal = Decimal('0')) -> Decimal:
    if value is None:
        return default
    try:
        return Decimal(str(value))
    except InvalidOperation:
        return default


def to_int(value: Any, default: int = 0) -> int:
    try:
        return int(value)
    except (ValueError, TypeError):
        return default


def format_price_vnd(amount: Decimal) -> str:
    return f"{int(amount):,}đ"


def paginate_queryset(queryset, page: int, page_size: int):
    offset = (page - 1) * page_size
    return queryset[offset:offset + page_size]


def build_pagination_meta(total: int, page: int, page_size: int) -> dict:
    total_pages = (total + page_size - 1) // page_size
    return {
        'total': total,
        'page': page,
        'page_size': page_size,
        'total_pages': total_pages,
        'has_next': page < total_pages,
        'has_prev': page > 1,
    }


def sanitize_string(value: Optional[str], max_length: int = None) -> str:
    if value is None:
        return ''
    value = str(value).strip()
    if max_length and len(value) > max_length:
        value = value[:max_length]
    return value
