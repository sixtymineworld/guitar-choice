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

    class InstrumentType(models.TextChoices):
        ELECTRIC = "electric", "Електрогітара"
        BASS = "bass", "Бас-гітара"
        ACOUSTIC = "acoustic", "Акустична гітара"

    class Status(models.TextChoices):
        CART = "cart", "У кошику"
        PLACED = "placed", "Оформлено"

    BASE_CRAFT_PRICES = {
        InstrumentType.ELECTRIC: 18500,
        InstrumentType.BASS: 19500,
        InstrumentType.ACOUSTIC: 17000,
    }
    BASE_CRAFT_PRICE = 18500

    # Опції для кожного типу інструмента: (value, label, surcharge)
    CONFIG_OPTIONS = {
        InstrumentType.ELECTRIC: {
            "body_shape": [
                ("stratocaster", "Стратокастер (Stratocaster)", 0),
                ("telecaster", "Телекастер (Telecaster)", 800),
                ("superstrat", "Суперстрат (Superstrat)", 2800),
                ("les_paul", "Лес Пол (Les Paul)", 4500),
            ],
            "wood": [
                ("alder", "Вільха (Alder)", 0),
                ("basswood", "Липа (Basswood)", 1400),
                ("ash", "Ясен (Ash)", 3800),
                ("mahogany", "Махагоні (Mahogany)", 6200),
            ],
            "color": [
                ("natural", "Натуральне дерево (Natural)", 0),
                ("black", "Чорний глянець (Gloss Black)", 1800),
                ("white", "Олімпійський білий (Olympic White)", 2400),
                ("sunburst", "Вінтажний санберст (Sunburst)", 3800),
                ("wine", "Бордовий глянець (Wine Red)", 4500),
            ],
            "frets_count": [
                ("21", "21 лад (Вінтаж)", 0),
                ("22", "22 лади (Стандарт)", 1200),
                ("24", "24 лади (Соло)", 2600),
            ],
            "strings_count": [
                ("6", "6 струн (Стандарт)", 0),
                ("7", "7 струн (Розширений діапазон)", 4200),
                ("8", "8 струн (Джент / Модерн)", 6800),
            ],
            "pickups_set": [
                ("sss", "SSS (3 сингли Vintage)", 4200),
                ("hss", "HSS (Хамбакер + 2 сингли)", 5800),
                ("hh", "HH (2 хамбакери Custom)", 7600),
                ("hsh", "HSH (2 хамбакери + сингл)", 8900),
            ],
        },
        InstrumentType.BASS: {
            "body_shape": [
                ("p_bass", "Precision Bass (Класичний бас)", 0),
                ("j_bass", "Jazz Bass (Ергономічний контур)", 1200),
                ("modern_bass", "Modern Bass (Спортивний дизайн)", 2500),
            ],
            "wood": [
                ("alder", "Вільха (Alder — класичний тон)", 0),
                ("ash", "Ясен (Ash — яскравий резонанс)", 3800),
                ("mahogany", "Махагоні (Глибокий щільний низ)", 6200),
                ("basswood", "Липа (Полегшений резонанс)", 1400),
            ],
            "color": [
                ("natural", "Натуральне дерево (Natural)", 0),
                ("black", "Чорний глянець (Gloss Black)", 1800),
                ("white", "Олімпійський білий (Olympic White)", 2400),
                ("sunburst", "Вінтажний санберст (Sunburst)", 3800),
                ("wine", "Бордовий глянець (Wine Red)", 4500),
            ],
            "frets_count": [
                ("20", "20 ладів (Вінтажний стандарт)", 0),
                ("24", "24 лади (Повний доступ до верхів)", 1600),
                ("fretless", "Безладовий гриф (Fretless)", 3200),
            ],
            "strings_count": [
                ("4", "4 струни (Класика)", 0),
                ("5", "5 струн (Розширений бас)", 3500),
                ("6", "6 струн (Прогресивний бас)", 5800),
            ],
            "pickups_set": [
                ("p_split", "Split-Coil (P-Bass Punch)", 3800),
                ("jj_set", "Jazz Single-Coil Set (J-Bass)", 4600),
                ("pj_set", "PJ-Set (Універсальний P+J)", 5400),
                ("dual_hb", "Dual Active Humbuckers", 7200),
            ],
        },
        InstrumentType.ACOUSTIC: {
            "body_shape": [
                ("dreadnought", "Дредноут (Dreadnought — потужний)", 0),
                ("grand_auditorium", "Grand Auditorium (Збалансований)", 1500),
                ("classical_body", "Класична форма (Іспанська)", 800),
            ],
            "wood": [
                ("spruce_mahogany", "Топ: Ялина Sitka / Боки: Махагоні", 0),
                ("cedar_rosewood", "Топ: Кедр / Боки: Палісандр", 3600),
                ("all_mahogany", "Повністю Махагоні (All-Mahogany)", 2400),
            ],
            "color": [
                ("natural", "Натуральний глянцевий лак", 0),
                ("natural_satin", "Натуральний матовий шовк (Satin)", 800),
                ("sunburst", "Вінтажний тютюновий санберст", 2800),
                ("black", "Чорний глянець", 1800),
            ],
            "frets_count": [
                ("19", "19 ладів (Класика)", 0),
                ("20", "20 ладів (Вестерн)", 500),
            ],
            "strings_count": [
                ("6_steel", "6 струн (Акустичний метал)", 0),
                ("6_nylon", "6 струн (Класичний нейлон)", 0),
                ("12_steel", "12 струн (12-струнна акустика)", 4500),
            ],
            "pickups_set": [
                ("none", "Без звукознімача (Чиста акустика)", 0),
                ("piezo_under", "Підпоріжковий п'єзодатчик", 2800),
                ("fishman_sys", "Преамп Fishman Presys (п'єзо + мікрофон)", 5900),
            ],
        },
    }

    # Зведені списки варіантів та націнок для моделі та сумісності
    ALL_CHOICES = {
        "body_shape": [],
        "wood": [],
        "color": [],
        "frets_count": [],
        "strings_count": [],
        "pickups_set": [],
    }
    ALL_SURCHARGES = {
        "body_shape": {},
        "wood": {},
        "color": {},
        "frets_count": {},
        "strings_count": {},
        "pickups_set": {},
    }

    _seen = {}
    for _itype, _fields in CONFIG_OPTIONS.items():
        for _f, _opts in _fields.items():
            if _f not in _seen:
                _seen[_f] = set()
            for _val, _lbl, _surcharge in _opts:
                if _val not in _seen[_f]:
                    _seen[_f].add(_val)
                    ALL_CHOICES[_f].append((_val, _lbl))
                ALL_SURCHARGES[_f][_val] = _surcharge

    SURCHARGES = ALL_SURCHARGES

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
            name = f"Кастом {self.get_instrument_type_display()} ({self.get_body_shape_display()})"
        return f"Замовлення №{self.pk}: {name}"

    def options_surcharge(self):
        total = 0
        for field in ["body_shape", "wood", "color", "frets_count", "strings_count", "pickups_set"]:
            val = getattr(self, field, None)
            total += self.ALL_SURCHARGES.get(field, {}).get(val, 0)
        return total

    def calculate_unit_price(self):
        if self.guitar_id and self.guitar:
            return self.guitar.price
        base = self.BASE_CRAFT_PRICES.get(self.instrument_type, self.BASE_CRAFT_PRICE)
        return base + self.options_surcharge()

    @property
    def total_price(self):
        return self.unit_price * self.quantity

    def save(self, *args, **kwargs):
        if self.status == self.Status.CART or self.unit_price is None:
            self.unit_price = self.calculate_unit_price()
        super().save(*args, **kwargs)
