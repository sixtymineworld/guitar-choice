from decimal import Decimal
from django import template
from django.db.models import Sum
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def format_uah(price):
    try:
        val = int(round(float(price)))
        return f"{val:,}".replace(",", " ") + " ₴"
    except (ValueError, TypeError):
        return f"{price} ₴"


@register.simple_tag
def render_stars(rating, max_stars=5):
    try:
        val = int(rating)
    except (ValueError, TypeError):
        val = 0
    val = max(0, min(val, max_stars))
    filled = "★" * val
    empty = "☆" * (max_stars - val)
    return mark_safe(f'<span class="rating-stars" aria-label="{val} з {max_stars}">{filled}{empty}</span>')


@register.simple_tag(takes_context=True)
def get_cart_count(context):
    request = context.get("request")
    if not request or not request.session.session_key:
        return 0
    from guitars.models import GuitarOrder

    total = GuitarOrder.objects.filter(
        session_key=request.session.session_key, status=GuitarOrder.Status.CART
    ).aggregate(total=Sum("quantity"))["total"]
    return total or 0
