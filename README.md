# GuitarChoice — Вебзастосунок підбору та конфігурування гітар

Вебзастосунок для вибору, детального порівняння, кастомного конфігурування та замовлення музичних інструментів із підтримкою системи підтримки прийняття рішень (СППР / швидкий підбір).

---

## Стек технологій
* **Мова програмування:** Python 3.13
* **Вебфреймворк:** Django 6.1.1
* **Система керування базами даних (СУБД):** MySQL 8.0+ / 9.0 (підключення через `mysql-connector-python`)
* **Керування конфігурацією:** `python-dotenv` (секрети та реквізити зберігаються виключно у змінних оточення `.env`)
* **Фронтенд:** Django Template Language (DTL), HTML5, CSS3, JavaScript (Vanilla ES6+)

---

## Інструкція із запуску проєкту

### 1. Клонування репозиторію
```bash
git clone https://github.com/dmytrokalitovskyi/guitar-choice.git
cd guitar-choice
```

### 2. Створення та активація віртуального середовища
```bash
# macOS / Linux:
python3 -m venv venv
source venv/bin/activate

# Windows:
python -m venv venv
venv\Scripts\activate
```

### 3. Встановлення залежностей
Усі залежності із зафіксованими точними версіями знаходяться у `requirements.txt`:
```bash
pip install -r requirements.txt
```

### 4. Налаштування змінних оточення
Створіть файл `.env` на основі наданого зразка `.env.example`:
```bash
cp .env.example .env
```
Відкрийте `.env` і вкажіть параметри доступу до вашої бази даних MySQL:
```env
DJANGO_SECRET_KEY=your-secret-key-here
DJANGO_DEBUG=1
DJANGO_ALLOWED_HOSTS=127.0.0.1,localhost

DB_NAME=guitar_choice
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306
```

> **Примітка:** Переконайтеся, що в MySQL попередньо створено порожню базу даних:
> ```sql
> CREATE DATABASE guitar_choice CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
> ```

### 5. Застосування міграцій
```bash
python manage.py migrate
```

### 6. Наповнення каталогу демонстраційними даними
У проєкті реалізовано команду автоматичного наповнення бази 20 культовими моделями інструментів:
```bash
python manage.py seed_guitars
```

### 7. Створення суперкористувача (адміністратора)
```bash
python manage.py createsuperuser
```

### 8. Запуск сервера розробки
```bash
python manage.py runserver
```
Після цього застосунок доступний у браузері за адресою: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)  
Панель адміністратора: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

---

## Структура проєкту
* `config/` — глобальні налаштування проєкту (`settings.py`, `urls.py`, `wsgi.py`).
* `guitars/` — основний Django-застосунок:
  * `models.py` — моделі домену (`Guitar`, `GuitarOrder`, `Feedback` тощо).
  * `views.py` — контролери та представлення (Generic CBV і FBV).
  * `forms.py` — форми `ModelForm` та `forms.Form`.
  * `urls.py` — карта маршрутів із простором імен `app_name = "guitars"`.
  * `management/commands/` — команди наповнення та міграції даних.
* `templates/` — шаблони інтерфейсу (`base.html`, каталог, картка товару, кошик, конфігуратор).
* `static/` — стилі, скрипти та зображення.
