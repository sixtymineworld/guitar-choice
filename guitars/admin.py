from django.contrib import admin
from .models import Feedback, Guitar, GuitarOrder

admin.site.site_header = "GuitarChoice — Панель адміністратора"
admin.site.site_title = "GuitarChoice Admin"
admin.site.index_title = "Керування каталогом, кастом-замовленнями та зверненнями"


@admin.register(Guitar)
class GuitarAdmin(admin.ModelAdmin):
    list_display = ("name", "brand", "guitar_type", "price", "is_available")
    list_filter = ("guitar_type", "is_available", "brand")
    search_fields = ("name", "brand", "material")


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "created_at")
    search_fields = ("name", "email", "message")
    readonly_fields = ("created_at",)


@admin.register(GuitarOrder)
class GuitarOrderAdmin(admin.ModelAdmin):
    list_display = ("id", "item_title", "instrument_type", "body_shape", "wood", "color", "pickups_set", "quantity", "unit_price", "status", "created_at")
    list_filter = ("status", "instrument_type", "body_shape", "wood", "color", "pickups_set", "frets_count", "strings_count")
    search_fields = ("guitar__name", "guitar__brand", "session_key")
    readonly_fields = ("unit_price", "session_key", "created_at")
    list_select_related = ("guitar",)

    @admin.display(description="Гітара / Кастом")
    def item_title(self, obj):
        return obj.guitar.name if obj.guitar else f"Кастом {obj.get_instrument_type_display()} ({obj.get_body_shape_display()})"
