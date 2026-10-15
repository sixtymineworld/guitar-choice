"""Import the MySQL exchange table into the local Django database."""
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from guitars.models import Guitar
from ._mysql import mysql_connection


class Command(BaseCommand):
    help = "Імпортує гітари з таблиці MySQL guitars_exchange через mysql-connector-python."

    def handle(self, *args, **options):
        connection = mysql_connection()
        cursor = connection.cursor(dictionary=True)
        try:
            try:
                cursor.execute("SELECT * FROM guitars_exchange")
            except Exception as exc:
                raise CommandError("Таблицю guitars_exchange не знайдено. Спершу виконайте export_guitars_mysql.") from exc
            rows = cursor.fetchall()
        finally:
            cursor.close()
            connection.close()

        fields = ("name", "brand", "guitar_type", "price", "description", "material",
                  "strings_count", "is_available", "image_url", "created_at")
        with transaction.atomic():
            for row in rows:
                defaults = {field: row[field] for field in fields}
                Guitar.objects.update_or_create(id=row["id"], defaults=defaults)
        self.stdout.write(self.style.SUCCESS(f"Імпортовано або оновлено: {len(rows)} гітар."))
