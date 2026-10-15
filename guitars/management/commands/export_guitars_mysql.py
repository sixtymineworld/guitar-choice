"""Export the Django Guitar model into a standalone MySQL table."""
from django.core.management.base import BaseCommand
from guitars.models import Guitar
from ._mysql import CREATE_GUITARS_TABLE, mysql_connection


class Command(BaseCommand):
    help = "Експортує каталог гітар до MySQL через mysql-connector-python."

    def handle(self, *args, **options):
        connection = mysql_connection()
        cursor = connection.cursor()
        try:
            cursor.execute(CREATE_GUITARS_TABLE)
            sql = """
                INSERT INTO guitars_exchange
                (id, name, brand, guitar_type, price, description, material,
                 strings_count, is_available, image_url, created_at)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                  name=VALUES(name), brand=VALUES(brand), guitar_type=VALUES(guitar_type),
                  price=VALUES(price), description=VALUES(description), material=VALUES(material),
                  strings_count=VALUES(strings_count), is_available=VALUES(is_available),
                  image_url=VALUES(image_url), created_at=VALUES(created_at)
            """
            rows = [
                (g.id, g.name, g.brand, g.guitar_type, g.price, g.description,
                 g.material, g.strings_count, g.is_available, g.image_url, g.created_at)
                for g in Guitar.objects.all()
            ]
            if rows:
                cursor.executemany(sql, rows)
            connection.commit()
            self.stdout.write(self.style.SUCCESS(f"Експортовано до MySQL: {len(rows)} гітар."))
        finally:
            cursor.close()
            connection.close()
