from django.conf import settings
from django.db import migrations


def seed_sample_reviews(apps, schema_editor):
    Guitar = apps.get_model("guitars", "Guitar")
    Review = apps.get_model("guitars", "Review")
    User = apps.get_model(settings.AUTH_USER_MODEL)

    # Get or create a sample user for the initial reviews
    demo_user, _ = User.objects.get_or_create(
        username="guitar_lover",
        defaults={"first_name": "Тарас", "email": "taras@example.com"},
    )

    sample_reviews = [
        ("Чудовий інструмент! Зручний гриф, якісна збірка та відмінне звучання.", 5),
        ("Дуже приємний тембр, ідеально підходить для репетицій та студійного запису.", 5),
        ("Гарне співвідношення ціни та якості, тримає стрій стабільно.", 4),
    ]

    # Add reviews to the first few guitars if any exist
    guitars = list(Guitar.objects.all()[: len(sample_reviews)])
    for guitar, (comment, rating) in zip(guitars, sample_reviews):
        Review.objects.get_or_create(
            guitar=guitar,
            user=demo_user,
            defaults={"rating": rating, "comment": comment},
        )


def unseed_sample_reviews(apps, schema_editor):
    Review = apps.get_model("guitars", "Review")
    Review.objects.filter(user__username="guitar_lover").delete()


class Migration(migrations.Migration):

    dependencies = [
        ("guitars", "0007_review"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RunPython(seed_sample_reviews, reverse_code=unseed_sample_reviews),
    ]

