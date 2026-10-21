from decimal import Decimal
from django.core.management.base import BaseCommand
from guitars.models import Guitar


SAMPLE_GUITARS = [
    # --- Електрогітари (Electric) ---
    {
        "name": "Player II Stratocaster",
        "brand": "Fender",
        "guitar_type": "electric",
        "price": Decimal("38900.00"),
        "material": "Вільха (Alder)",
        "strings_count": 6,
        "is_available": True,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/05/FenderStandardStrat.jpg",
        "description": "Еталонний Stratocaster мексиканського виробництва з трьома синглами Player Series Alnico 5, модерновим профілем грифу Modern C та 2-точковим тремоло. Забезпечує фірмове прозоре 'скляне' звучання, ідеальне для блюзу, фанку, року та поп-музики.",
    },
    {
        "name": "Player Telecaster",
        "brand": "Fender",
        "guitar_type": "electric",
        "price": Decimal("37500.00"),
        "material": "Вільха (Alder)",
        "strings_count": 6,
        "is_available": True,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/b/bb/1966_Fender_Telecaster_%28SN159266%29.jpg",
        "description": "Перша серійна електрогітара в історії, яка й досі залишається синонімом неперевершеної надійності та яскравого твангового саунду. Оснащена двома синглами Alnico 5, струнами крізь корпус і бриджем із шістьма сідлами для точного інтонування.",
    },
    {
        "name": "Les Paul Standard '60s",
        "brand": "Gibson",
        "guitar_type": "electric",
        "price": Decimal("119000.00"),
        "material": "Махагоні з кленовим топом",
        "strings_count": 6,
        "is_available": True,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/1/1c/Full_front_R9_Les_Paul.jpg",
        "description": "Безкомпромісна американська класика золотого віку рок-н-ролу. Масивний цільний корпус з червоного дерева без полегшення, топ із фігурного клену, тонкий швидкісний профіль грифу SlimTaper та калібровані хамбакери 60s Burstbucker дарують нескінченний оксамитовий сустейн.",
    },
    {
        "name": "SG Standard",
        "brand": "Gibson",
        "guitar_type": "electric",
        "price": Decimal("74900.00"),
        "material": "Цільний махагоні",
        "strings_count": 6,
        "is_available": True,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/7b/Gibson_SG_Standard.jpg",
        "description": "Культовий 'рогатий' інструмент, улюблена гітара Ангуса Янга (AC/DC). Завдяки ультратонкому та легкому корпусу з глибоким подвійним вирізом гітара відкриває легкий доступ до 22-го ладу. Звукознімачі 490R та 490T забезпечують пробивне, гарчаще звучання для класичного року та важких рифів.",
    },
    {
        "name": "RG421",
        "brand": "Ibanez",
        "guitar_type": "electric",
        "price": Decimal("17200.00"),
        "material": "Меранті, гриф клен",
        "strings_count": 6,
        "is_available": True,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/ed/Ibanez_RG350EXZ_BK_Electric_Guitar_c.a._2011.jpg",
        "description": "Сучасний стандарт шред- та метал-гітари. Надтонкий швидкісний гриф Wizard III, фіксований бридж для максимальної стабільності строю та хамбакери Ibanez Quantum з потужним басовим відгуком і чіткою атакою у швидкісних пасажах.",
    },
    {
        "name": "Les Paul Standard 50s",
        "brand": "Epiphone",
        "guitar_type": "electric",
        "price": Decimal("28400.00"),
        "material": "Махагоні з кленовим топом",
        "strings_count": 6,
        "is_available": True,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/41/Gibson_Joe_Bonamassa_Les_Paul_Standard%2C_CES2013.jpg",
        "description": "Офіційна репліка культового Les Paul від дочірнього бренду Gibson. Оснащена висококласними звукознімачами Epiphone ProBucker із котушками з нікель-срібла, потенціометрами CTS та вінтажним округлим профілем грифу 50s Rounded Medium C.",
    },

    # --- Акустичні гітари (Acoustic) ---
    {
        "name": "FG800M",
        "brand": "Yamaha",
        "guitar_type": "acoustic",
        "price": Decimal("13800.00"),
        "material": "Цільна ялина, нато/окуме",
        "strings_count": 6,
        "is_available": True,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/0e/Yamaha_Acoustic_Guitar_FG-331v2.jpg",
        "description": "Найпопулярніша повнорозмірна акустична гітара у світі у своєму класі. Верхня дека виготовлена з цільної сітхінської ялини, а нова скалопована система пружин (scalloped bracing) забезпечує потужний резонанс, гучний бас і відкритий тембр.",
    },
    {
        "name": "CD-60S Dreadnought",
        "brand": "Fender",
        "guitar_type": "acoustic",
        "price": Decimal("11900.00"),
        "material": "Цільна ялина, махагоні",
        "strings_count": 6,
        "is_available": True,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/2/28/Kapodaster_an_Westerngitarre_und_3_verschiedene_Formen_--_2015_--_1951C.jpg",
        "description": "Класичний американський дредноут початкового та середнього рівня. Топ із масиву ялини, корпус із червоного дерева та фірмовий гриф Fender Easy-to-Play зі скругленими краями накладки, на якому надзвичайно комфортно затискати перші акорди.",
    },
    {
        "name": "D-28 Standard",
        "brand": "Martin",
        "guitar_type": "acoustic",
        "price": Decimal("145000.00"),
        "material": "Цільна сітхінська ялина, палісандр",
        "strings_count": 6,
        "is_available": True,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/0/0c/Martin_D-28_Acoustic_Guitar.jpg",
        "description": "Легенда акустичної музики, на якій грали Джон Леннон, Пол Маккартні, Боб Ділан та Ніл Янг. Поєднання масиву ялини та добірного палісандру створює глибокий бас, багатий обертонами діапазон і незрівнянну проекцію звуку.",
    },
    {
        "name": "LX1 Little Martin",
        "brand": "Martin",
        "guitar_type": "acoustic",
        "price": Decimal("28500.00"),
        "material": "Цільна ялина, махагоні HPL",
        "strings_count": 6,
        "is_available": True,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e0/Martin_D28_Acoustic_Guitar.jpg",
        "description": "Компактна travel-гітара розміру 3/4, яка стала візитівкою Еда Ширана. Незважаючи на зменшений корпус, цільний топ із ялини видає дивовижно дорослий, теплий та сфокусований звук, а зносостійкий HPL-корпус не боїться перепадів вологості.",
    },
    {
        "name": "214ce Grand Auditorium",
        "brand": "Taylor",
        "guitar_type": "acoustic",
        "price": Decimal("54600.00"),
        "material": "Цільна ялина, багатошарова коа",
        "strings_count": 6,
        "is_available": True,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/68/Yamaha_FG-312_12-String_Acoustic_Guitar_%281977-1981%29.jpg",
        "description": "Універсальний електроакустичний інструмент з фірмовою формою Grand Auditorium і зручним венеціанським вирізом (cutaway). Ідеальний баланс між пальцевою технікою (fingerstyle) та грою медіатором. Оснащений фірмовою електронікою Expression System 2.",
    },

    # --- Бас-гітари (Bass) ---
    {
        "name": "Player Precision Bass",
        "brand": "Fender",
        "guitar_type": "bass",
        "price": Decimal("42500.00"),
        "material": "Вільха (Alder)",
        "strings_count": 4,
        "is_available": True,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/5/53/Fender_AP_P-Bass_20230730.jpg",
        "description": "Найвідоміший бас у світі, що створив фундамент рок-, фанк- і поп-музики з 1951 року. Розділений звукознімач Player Series Alnico 5 Split-Coil генерує щільний, монолітний та глибокий низ, який миттєво сідає в будь-який студійний мікс.",
    },
    {
        "name": "Player Jazz Bass",
        "brand": "Fender",
        "guitar_type": "bass",
        "price": Decimal("43900.00"),
        "material": "Вільха (Alder)",
        "strings_count": 4,
        "is_available": True,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/9/9c/Fender_Jazz-Bass_1966.jpg",
        "description": "Вибір басистів, які цінують виразну артикуляцію, 'гарчащу' середину та співучі флажолети (від Джако Пасторіуса до Маркуса Міллера). Два сингли Jazz Bass дозволяють тонко змішувати нековий об'єм і бриджеву гостроту.",
    },
    {
        "name": "SR300E",
        "brand": "Ibanez",
        "guitar_type": "bass",
        "price": Decimal("21900.00"),
        "material": "Ньято (Nyatoh)",
        "strings_count": 4,
        "is_available": True,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/7/74/Ibanez_SR_Bass_and_Ibanez_SRC6_%28short_scale_bass_or_baryton_guitar%29.jpg",
        "description": "Суперзручний ергономічний бас із витонченим корпусом і тонким швидкісним грифом. Оснащений звукознімачами PowerSpan Dual Coil та активним 3-смуговим еквалайзером Ibanez Custom Electronics із перемикачем Power Tap (хамбакер/сингл/посилений сингл).",
    },
    {
        "name": "StingRay Ray4",
        "brand": "Sterling by Music Man",
        "guitar_type": "bass",
        "price": Decimal("24800.00"),
        "material": "Липа (Basswood)",
        "strings_count": 4,
        "is_available": True,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/1/13/Fender_Precision_Bass_Lyte_Body_1.jpg",
        "description": "Прямий спадкоємець культового басу Music Man StingRay, розробленого Лео Фендером у 1976 році. Потужний керамічний хамбакер біля бриджу та активний 2-смуговий преамп 9V забезпечують фірмовий ударний слеп-саунд і потужний драйв.",
    },
    {
        "name": "TRBX174",
        "brand": "Yamaha",
        "guitar_type": "bass",
        "price": Decimal("12400.00"),
        "material": "Вільха (Alder)",
        "strings_count": 4,
        "is_available": True,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/e/e4/Fender_Jazz_Bass_Special.jpg",
        "description": "Зразковий універсальний бас для початківців і репетицій. Конфігурація датчиків P/J (спліт-сингл Precision біля грифа і сингл Jazz біля бриджа) дає доступ до всього спектру сучасних басових тембрів за доступну ціну.",
    },

    # --- Класичні гітари (Classical) ---
    {
        "name": "C40",
        "brand": "Yamaha",
        "guitar_type": "classical",
        "price": Decimal("8900.00"),
        "material": "Ялина та меранті",
        "strings_count": 6,
        "is_available": True,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/6e/Classical_Guitar_two_views2.png",
        "description": "Золотий стандарт навчальної класичної гітари, рекомендований викладачами музичних шкіл по всьому світу. М'які нейлонові струни, вивірена мензура (650 мм) та стабільна кілкова механіка забезпечують легкий старт і правильну постановку рук.",
    },
    {
        "name": "C5 Iberia",
        "brand": "Cordoba",
        "guitar_type": "classical",
        "price": Decimal("19500.00"),
        "material": "Цільний канадський кедр, махагоні",
        "strings_count": 6,
        "is_available": True,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/46/Classical_Guitar_two_views2.png",
        "description": "Справжня іспанська класика ручної роботи. Топ із масиву канадського червоного кедра створює теплий, оксамитовий та чуйний тембр з багатими низькими частотами. Оснащена легким анкерним стрижнем для регулювання прогину грифа.",
    },
    {
        "name": "1C",
        "brand": "Alhambra",
        "guitar_type": "classical",
        "price": Decimal("26700.00"),
        "material": "Цільний червоний кедр, сапеле",
        "strings_count": 6,
        "is_available": True,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/6/6e/Classical_Guitar_two_views2.png",
        "description": "Автентична класична гітара, виготовлена в Іспанії майстрами з провінції Аліканте. Завдяки цільній верхній деці та традиційному іспанському кріпленню пружин має дивовижний резонанс, яскраву атаку та глибокий сустейн для академічного репертуару.",
    },
    {
        "name": "VC204",
        "brand": "Valencia",
        "guitar_type": "classical",
        "price": Decimal("5400.00"),
        "material": "Ялина, нато, жабон",
        "strings_count": 6,
        "is_available": True,
        "image_url": "https://upload.wikimedia.org/wikipedia/commons/4/46/Classical_Guitar_two_views2.png",
        "description": "Доступна класична повнорозмірна гітара серії 200 з вишуканим шовковисто-матовим покриттям Satin Finish. Легкий корпус, надійні нейлонові струни та комфортний профіль роблять її чудовим вибором для дому, подорожей і перших кроків у музиці.",
    },
]


class Command(BaseCommand):
    help = "Наповнює каталог базовими культовими моделями гітар з описами та фотографіями."

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear-test",
            action="store_true",
            help="Видалити тестові моделі (наприклад, з назвою 'test')",
        )

    def handle(self, *args, **options):
        # Видаляємо тестові записи
        deleted_count, _ = Guitar.objects.filter(name__iexact="test").delete()
        if deleted_count:
            self.stdout.write(self.style.WARNING(f"Видалено тестових записів: {deleted_count}"))

        created_count = 0
        updated_count = 0

        for item in SAMPLE_GUITARS:
            guitar, created = Guitar.objects.update_or_create(
                brand=item["brand"],
                name=item["name"],
                defaults=item,
            )
            if created:
                created_count += 1
            else:
                updated_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Успішно оновлено каталог: додано нових {created_count}, оновлено існуючих {updated_count}. Всього у каталозі: {Guitar.objects.count()} гітар."
            )
        )
