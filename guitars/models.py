from decimal import Decimal
from django.conf import settings
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse
from .constants import (
    ALL_CHOICES,
    ALL_SURCHARGES,
    BASE_CRAFT_PRICE,
    BASE_CRAFT_PRICES,
    CONFIG_OPTIONS,
    TYPE_SURCHARGES,
)


class Guitar(models.Model):
    class GuitarType(models.TextChoices):
        ACOUSTIC = "acoustic", "Акустична"
        ELECTRIC = "electric", "Електрогітара"
        BASS = "bass", "Бас-гітара"
        CLASSICAL = "classical", "Класична"

    name = models.CharField("назва", max_length=120)
    brand = models.CharField("бренд", max_length=80)
    guitar_type = models.CharField("тип", max_length=20, choices=GuitarType.choices)
    price = models.DecimalField("ціна, грн", max_digits=10, decimal_places=2, validators=[MinValueValidator(0)])
    description = models.TextField("опис")
    material = models.CharField("матеріал корпусу", max_length=100)
    strings_count = models.PositiveSmallIntegerField("кількість струн", default=6, validators=[MinValueValidator(1), MaxValueValidator(18)])
    is_available = models.BooleanField("доступна до замовлення", default=True)
    image_url = models.URLField("посилання на зображення", blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["brand", "name"]
        verbose_name = "гітара"
        verbose_name_plural = "гітари"

    def __str__(self):
        return f"{self.brand} {self.name}"

    def get_absolute_url(self):
        return reverse("guitars:guitar_detail", kwargs={"pk": self.pk})

    def get_sample_audio_url(self):
        from django.templatetags.static import static
        return static(f"media/{self.guitar_type}.mp3")


class Feedback(models.Model):
    name = models.CharField("ім'я", max_length=80)
    email = models.EmailField("email")
    message = models.TextField("повідомлення", max_length=1200)
    created_at = models.DateTimeField("створено", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "звернення"
        verbose_name_plural = "звернення"

    def __str__(self):
        return f"Звернення від {self.name}"


class GuitarOrder(models.Model):
    class InstrumentType(models.TextChoices):
        ELECTRIC = "electric", "Електрогітара"
        BASS = "bass", "Бас-гітара"
        ACOUSTIC = "acoustic", "Акустична гітара"

    class Status(models.TextChoices):
        CART = "cart", "У кошику"
        PLACED = "placed", "Оформлено"

    BASE_CRAFT_PRICE = BASE_CRAFT_PRICE
    BASE_CRAFT_PRICES = BASE_CRAFT_PRICES
    CONFIG_OPTIONS = CONFIG_OPTIONS
    ALL_CHOICES = ALL_CHOICES
    ALL_SURCHARGES = ALL_SURCHARGES
    TYPE_SURCHARGES = TYPE_SURCHARGES
    SURCHARGES = ALL_SURCHARGES

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="orders",
        verbose_name="користувач",
    )
    guitar = models.ForeignKey(
        Guitar,
        verbose_name="базова модель",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    instrument_type = models.CharField(
        "тип інструмента",
        max_length=20,
        choices=InstrumentType.choices,
        default=InstrumentType.ELECTRIC,
    )
    body_shape = models.CharField("форма гітари", max_length=35, choices=ALL_CHOICES["body_shape"], default="stratocaster")
    wood = models.CharField("дерево корпусу / топ", max_length=35, choices=ALL_CHOICES["wood"], default="alder")
    color = models.CharField("колір", max_length=35, choices=ALL_CHOICES["color"], default="natural")
    frets_count = models.CharField("кількість ладів", max_length=20, choices=ALL_CHOICES["frets_count"], default="22")
    strings_count = models.CharField("кількість струн", max_length=20, choices=ALL_CHOICES["strings_count"], default="6")
    pickups_set = models.CharField("звукознімачі / електроніка", max_length=35, choices=ALL_CHOICES["pickups_set"], default="sss")
    quantity = models.PositiveSmallIntegerField(
        "кількість",
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
    )
    unit_price = models.DecimalField("ціна за одиницю, грн", max_digits=10, decimal_places=2, editable=False)
    session_key = models.CharField("сесія", max_length=40, blank=True, default="", db_index=True)
    status = models.CharField("статус", max_length=20, choices=Status.choices, default=Status.CART)
    created_at = models.DateTimeField("створено", auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "замовлення"
        verbose_name_plural = "замовлення"

    def __str__(self):
        if self.guitar_id and self.guitar:
            name = self.guitar.name
        else:
            name = f"Кастом {self.get_instrument_type_display()} ({self.get_body_shape_display()})"
        return f"Замовлення №{self.pk}: {name}"

    def options_surcharge(self):
        type_surcharges = self.TYPE_SURCHARGES.get(self.instrument_type, {})
        total = 0
        for field in ["body_shape", "wood", "color", "frets_count", "strings_count", "pickups_set"]:
            val = getattr(self, field, None)
            total += type_surcharges.get(field, {}).get(val, self.ALL_SURCHARGES.get(field, {}).get(val, 0))
        return total

    def calculate_unit_price(self):
        if self.guitar_id and self.guitar:
            return self.guitar.price
        base = self.BASE_CRAFT_PRICES.get(self.instrument_type, self.BASE_CRAFT_PRICE)
        return Decimal(base + self.options_surcharge())

    @property
    def total_price(self):
        return self.unit_price * self.quantity

    def save(self, *args, **kwargs):
        if self.status == self.Status.CART or self.unit_price is None:
            self.unit_price = self.calculate_unit_price()
        super().save(*args, **kwargs)


class Review(models.Model):
    class Rating(models.IntegerChoices):
        POOR = 1, "1 — Погано"
        FAIR = 2, "2 — Задовільно"
        GOOD = 3, "3 — Добре"
        VERY_GOOD = 4, "4 — Дуже добре"
        EXCELLENT = 5, "5 — Відмінно"

    guitar = models.ForeignKey(Guitar, on_delete=models.CASCADE, related_name="reviews", verbose_name="гітара")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="reviews", verbose_name="автор")
    rating = models.PositiveSmallIntegerField("оцінка", choices=Rating.choices, default=Rating.EXCELLENT)
    comment = models.TextField("текст відгуку", max_length=1000)
    created_at = models.DateTimeField("створено", auto_now_add=True)
    updated_at = models.DateTimeField("оновлено", auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "відгук"
        verbose_name_plural = "відгуки"

    def __str__(self):
        return f"Відгук від {self.user} на {self.guitar} ({self.rating}★)"

    def get_absolute_url(self):
        return reverse("guitars:guitar_detail", kwargs={"pk": self.guitar_id})

