from django import template
from django.utils.safestring import mark_safe

register = template.Library()


@register.simple_tag
def format_uah(price):
    """Format a numeric price with space thousand separators and ₴ symbol."""
    try:
        val = int(round(float(price)))
        return f"{val:,}".replace(",", " ") + " ₴"
    except (ValueError, TypeError):
        return f"{price} ₴"


@register.simple_tag
def render_stars(rating, max_stars=5):
    """Render a star rating string (e.g., ★★★★☆)."""
    try:
        val = int(rating)
    except (ValueError, TypeError):
        val = 0
    val = max(0, min(val, max_stars))
    filled = "★" * val
    empty = "☆" * (max_stars - val)
    return mark_safe(f'<span class="rating-stars" aria-label="{val} з {max_stars}">{filled}{empty}</span>')

