from django.db import migrations, models


GUITAR_COLORS = {
    ("Fender", "Player II Stratocaster"): "3-Color Sunburst",
    ("Fender", "Player Telecaster"): "Butterscotch Blonde",
    ("Gibson", "Les Paul Standard '60s"): "Bourbon Burst",
    ("Gibson", "SG Standard"): "Heritage Cherry",
    ("Ibanez", "RG421"): "Black Flat",
    ("Epiphone", "Les Paul Standard 50s"): "Metallic Gold",
    ("Yamaha", "FG800M"): "Natural Satin",
    ("Fender", "CD-60S Dreadnought"): "Natural Gloss",
    ("Martin", "D-28 Standard"): "Natural Aging Toner",
    ("Martin", "LX1 Little Martin"): "Natural",
    ("Taylor", "214ce Grand Auditorium"): "Natural",
    ("Fender", "Player Precision Bass"): "Olympic White",
    ("Fender", "Player Jazz Bass"): "3-Color Sunburst",
    ("Ibanez", "SR300E"): "Iron Pewter",
    ("Sterling by Music Man", "StingRay Ray4"): "Vintage Sunburst",
    ("Yamaha", "TRBX174"): "Black",
    ("Yamaha", "C40"): "Natural",
    ("Cordoba", "C5 Iberia"): "Natural Gloss",
    ("Alhambra", "1C"): "Natural Cedar",
    ("Valencia", "VC204"): "Antique Natural",
}


def populate_guitar_colors(apps, schema_editor):
    Guitar = apps.get_model("guitars", "Guitar")
    for guitar in Guitar.objects.all():
        key = (guitar.brand, guitar.name)
        if key in GUITAR_COLORS:
            guitar.color = GUITAR_COLORS[key]
        elif not guitar.color:
            guitar.color = "Natural"
        guitar.save(update_fields=["color"])


class Migration(migrations.Migration):

    dependencies = [
        ("guitars", "0010_favorite"),
    ]

    operations = [
        migrations.AddField(
            model_name="guitar",
            name="color",
            field=models.CharField(default="Natural", max_length=80, verbose_name="колір"),
            preserve_default=False,
        ),
        migrations.RunPython(populate_guitar_colors, migrations.RunPython.noop),
    ]

