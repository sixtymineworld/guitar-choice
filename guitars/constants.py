BASE_CRAFT_PRICE = 18500
BASE_CRAFT_PRICES = {
    "electric": 18500,
    "bass": 19500,
    "acoustic": 17000,
}

CONFIG_OPTIONS = {
    "electric": {
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
    "bass": {
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
    "acoustic": {
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

TYPE_SURCHARGES = {
    itype: {
        field: {val: surcharge for val, _, surcharge in opts}
        for field, opts in fields.items()
    }
    for itype, fields in CONFIG_OPTIONS.items()
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


DSS_GENRE_TYPE_MAP = {
    "rock": "electric",
    "metal": "electric",
    "blues": "electric",
    "acoustic": "acoustic",
    "indie": "acoustic",
    "classical": "classical",
    "bass": "bass",
}

DSS_GENRE_NAMES = {
    "rock": "Рок / Альтернатива",
    "metal": "Метал / Важкий рок",
    "blues": "Блюз / Джаз / Фанк",
    "acoustic": "Акустичний поп / Інді",
    "indie": "Інді / Авторська пісня",
    "classical": "Класика / Фламенко",
    "bass": "Бас / Ритм-секція",
}

