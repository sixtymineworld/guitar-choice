import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('guitars', '0008_data_seed_sample_reviews'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='guitarorder',
            name='user',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='orders', to=settings.AUTH_USER_MODEL, verbose_name='користувач'),
        ),
        migrations.AlterField(
            model_name='guitarorder',
            name='session_key',
            field=models.CharField(blank=True, db_index=True, default='', max_length=40, verbose_name='сесія'),
        ),
    ]
