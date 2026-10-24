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
    if not request or not request.user.is_authenticated:
        return 0
    from guitars.models import GuitarOrder

    total = GuitarOrder.objects.filter(
        user=request.user, status=GuitarOrder.Status.CART
    ).aggregate(total=Sum("quantity"))["total"]
    return total or 0


@register.simple_tag(takes_context=True)
def get_favorite_count(context):
    request = context.get("request")
    if not request or not request.user.is_authenticated:
        return 0
    from guitars.models import Favorite
    return Favorite.objects.filter(user=request.user).count()


@register.simple_tag(takes_context=True)
def get_user_favorite_ids(context):
    request = context.get("request")
    if not request or not request.user.is_authenticated:
        return set()
    from guitars.models import Favorite
    return set(Favorite.objects.filter(user=request.user).values_list("guitar_id", flat=True))
