from decimal import Decimal
from django.core.management.base import BaseCommand
from guitars.models import Guitar


SAMPLE_GUITARS = [
    {"name": "LX1 Little Martin", "brand": "Martin", "guitar_type": "acoustic", "price": Decimal("28500.00"), "material": "червоне дерево HPL", "strings_count": 6, "is_available": True, "description": "Компактна тревел-гітара з виразним, збалансованим звучанням. Добре підходить для навчання, подорожей та домашнього запису."},
    {"name": "Player II Stratocaster", "brand": "Fender", "guitar_type": "electric", "price": Decimal("38900.00"), "material": "вільха", "strings_count": 6, "is_available": True, "description": "Універсальна електрогітара з трьома синглами, комфортним грифом і знайомим характером Stratocaster."},
    {"name": "SR300E", "brand": "Ibanez", "guitar_type": "bass", "price": Decimal("21900.00"), "material": "ньятон", "strings_count": 4, "is_available": True, "description": "Легка бас-гітара з активною електронікою та широкими можливостями корекції тембру."},
    {"name": "C40", "brand": "Yamaha", "guitar_type": "classical", "price": Decimal("8900.00"), "material": "ялина та меранті", "strings_count": 6, "is_available": False, "description": "Зручна класична модель із нейлоновими струнами для перших кроків у музиці."},
]


class Command(BaseCommand):
    help = "Додає демонстраційні моделі гітар до каталогу."

    def handle(self, *args, **options):
        count = 0
        for item in SAMPLE_GUITARS:
            _, created = Guitar.objects.get_or_create(brand=item["brand"], name=item["name"], defaults=item)
            count += int(created)
        self.stdout.write(self.style.SUCCESS(f"Додано демонстраційних моделей: {count}."))
