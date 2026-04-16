from decimal import Decimal, InvalidOperation, ROUND_HALF_UP

from django import template

register = template.Library()


@register.filter
def vnd(value):
    try:
        amount = Decimal(str(value))
    except (InvalidOperation, TypeError, ValueError):
        return ""

    amount = amount.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    sign = "-" if amount < 0 else ""
    formatted = f"{abs(int(amount)):,}".replace(",", ".")
    return f"{sign}{formatted}đ"
