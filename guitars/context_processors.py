from django.db.models import Sum
from .models import GuitarOrder

def cart(request):
    """Expose the number of guitars in the visitor's cart to every template."""
    session_key = request.session.session_key
    if not session_key:
        return {"cart_count": 0}
    total = GuitarOrder.objects.filter(session_key=session_key, status=GuitarOrder.Status.CART).aggregate(total=Sum("quantity"))["total"]
    return {"cart_count": total or 0}

