from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.urls import reverse


class Guitar(models.Model):
    """An instrument available for configuration and ordering."""

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
        return reverse("guitar_detail", kwargs={"pk": self.pk})


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
    """A custom guitar configuration created in the configurator and kept in the cart."""

    class BodyShape(models.TextChoices):
        STRATOCASTER = "stratocaster", "Стратокастер (Stratocaster)"
        TELECASTER = "telecaster", "Телекастер (Telecaster)"
        LES_PAUL = "les_paul", "Лес Пол (Les Paul)"
        SUPERSTRAT = "superstrat", "Суперстрат (Superstrat)"

    class Color(models.TextChoices):
        BLACK = "black", "Чорний глянець"
        SUNBURST = "sunburst", "Вінтажний санберст"
        WINE = "wine", "Бордовий глянець"
        WHITE = "white", "Олімпійський білий"
        NATURAL = "natural", "Натуральне дерево"

    class FretsCount(models.TextChoices):
        FRETS_21 = "21", "21 лад"
        FRETS_22 = "22", "22 лади"
        FRETS_24 = "24", "24 лади"

    class StringsCount(models.TextChoices):
        STRINGS_6 = "6", "6 струн"
        STRINGS_7 = "7", "7 струн"
        STRINGS_8 = "8", "8 струн"

    class PickupsSet(models.TextChoices):
        SSS = "sss", "SSS (3 сингли Vintage)"
        HSS = "hss", "HSS (Хамбакер + 2 сингли)"
        HH = "hh", "HH (2 хамбакери Custom)"
        HSH = "hsh", "HSH (2 хамбакери + сингл)"

    class Wood(models.TextChoices):
        ALDER = "alder", "Вільха (Alder)"
        ASH = "ash", "Ясен (Ash)"
        MAHOGANY = "mahogany", "Махагоні (Mahogany)"
        BASSWOOD = "basswood", "Липа (Basswood)"

    class Status(models.TextChoices):
        CART = "cart", "У кошику"
        PLACED = "placed", "Оформлено"

    BASE_CRAFT_PRICE = 18500

    # Доплати за кастомні опції майстерні, грн
    SURCHARGES = {
        "body_shape": {
            BodyShape.STRATOCASTER: 0,
            BodyShape.TELECASTER: 800,
            BodyShape.SUPERSTRAT: 2800,
            BodyShape.LES_PAUL: 4500,
        },
        "wood": {
            Wood.ALDER: 0,
            Wood.BASSWOOD: 1400,
            Wood.ASH: 3800,
            Wood.MAHOGANY: 6200,
        },
        "color": {
            Color.NATURAL: 0,
            Color.BLACK: 1800,
            Color.WHITE: 2400,
            Color.SUNBURST: 3800,
            Color.WINE: 4500,
        },
        "frets_count": {
            FretsCount.FRETS_21: 0,
            FretsCount.FRETS_22: 1200,
            FretsCount.FRETS_24: 2600,
        },
        "strings_count": {
            StringsCount.STRINGS_6: 0,
            StringsCount.STRINGS_7: 4200,
            StringsCount.STRINGS_8: 6800,
        },
        "pickups_set": {
            PickupsSet.SSS: 4200,
            PickupsSet.HSS: 5800,
            PickupsSet.HH: 7600,
            PickupsSet.HSH: 8900,
        },
    }

    guitar = models.ForeignKey(
        Guitar,
        verbose_name="базова модель",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="orders",
    )
    body_shape = models.CharField("форма гітари", max_length=20, choices=BodyShape.choices, default=BodyShape.STRATOCASTER)
    wood = models.CharField("дерево корпусу", max_length=20, choices=Wood.choices, default=Wood.ALDER)
    color = models.CharField("колір", max_length=20, choices=Color.choices, default=Color.NATURAL)
    frets_count = models.CharField("кількість ладів", max_length=10, choices=FretsCount.choices, default=FretsCount.FRETS_22)
    strings_count = models.CharField("кількість струн", max_length=10, choices=StringsCount.choices, default=StringsCount.STRINGS_6)
    pickups_set = models.CharField("сет звукознімачів", max_length=20, choices=PickupsSet.choices, default=PickupsSet.SSS)
    quantity = models.PositiveSmallIntegerField(
        "кількість",
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(20)],
    )
    unit_price = models.DecimalField("ціна за одиницю, грн", max_digits=10, decimal_places=2, editable=False)
    session_key = models.CharField("сесія", max_length=40, db_index=True)
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
            name = f"Кастом {self.get_body_shape_display()}"
        return f"Замовлення №{self.pk}: {name}"

    def options_surcharge(self):
        return sum(self.SURCHARGES.get(field, {}).get(getattr(self, field), 0) for field in self.SURCHARGES)

    def calculate_unit_price(self):
        base = self.guitar.price if (self.guitar_id and self.guitar) else self.BASE_CRAFT_PRICE
        return base + self.options_surcharge()

    @property
    def total_price(self):
        return self.unit_price * self.quantity

    def save(self, *args, **kwargs):
        # Поки замовлення в кошику — ціна актуальна; після оформлення вона фіксується
        if self.status == self.Status.CART or self.unit_price is None:
            self.unit_price = self.calculate_unit_price()
        super().save(*args, **kwargs)
