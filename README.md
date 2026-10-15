# GuitarChoice

Навчальний багатосторінковий Django-застосунок для підтримки прийняття рішень під час вибору, конфігурування та замовлення гітар.

## Реалізовано

- Django-моделі `Guitar` (каталог), `Feedback` (звернення клієнтів) і `GuitarOrder` (конфігурація/замовлення);
- сторінки: Головна, Каталог із пошуком і фільтрацією, Деталі моделі, Конфігуратор, Кошик, Про сервіс, Консультація;
- детальний перегляд кожної гітари;
- конфігуратор: вибір базової моделі, покриття, накладки грифа, звукознімачів, струн і чохла з автоматичним розрахунком ціни;
- кошик (прив’язаний до сесії відвідувача): зміна кількості, видалення позицій, оформлення замовлення;
- форма зворотного зв’язку з валідацією й збереженням у БД;
- Django admin для наповнення каталогу;
- окремий файл стилів `static/css/style.css` у бордовій палітрі;
- імпорт та експорт каталогу в MySQL через `mysql-connector-python`.

## Запуск

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_guitars
python manage.py runserver
```

Відкрийте `http://127.0.0.1:8000/`. Для керування даними через адмін-панель створіть адміністратора командою `python manage.py createsuperuser`, а потім відкрийте `/admin/`.

## Обмін із MySQL

Веб-застосунок використовує SQLite, тому запускається без додаткових налаштувань. Для обміну каталогом із MySQL встановіть параметри підключення в оточенні:

```bash
export MYSQL_HOST=127.0.0.1
export MYSQL_PORT=3306
export MYSQL_USER=root
export MYSQL_PASSWORD=your_password
export MYSQL_DATABASE=guitar_exchange
```

База `guitar_exchange` має існувати. Команда експорту сама створює таблицю `guitars_exchange` і синхронізує записи за ID:

```bash
python manage.py export_guitars_mysql
python manage.py import_guitars_mysql
```

Обидві команди безпосередньо використовують бібліотеку `mysql.connector` з пакета `mysql-connector-python`.
