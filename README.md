# GuitarChoice

Вебзастосунок для вибору, порівняння, конфігурування та замовлення гітар із системою швидкого підбору.

## Стек
* Python 3.13, Django 6.1.1
* MySQL 8.0+ (`mysql-connector-python`)
* `python-dotenv` для змінних оточення
* Django Templates, HTML5, CSS3, JavaScript

## Запуск

### 1. Клонування та залежності
```bash
git clone https://github.com/dmytrokalitovskyi/guitar-choice.git
cd guitar-choice
python -m venv venv
venv\Scripts\activate        # macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
```

### 2. Налаштування
Скопіюйте `.env.example` у `.env` і вкажіть дані вашої MySQL:
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

Базу даних потрібно створити заздалегідь:
```sql
CREATE DATABASE guitar_choice CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 3. Міграції та тестові дані
```bash
python manage.py migrate
python manage.py seed_guitars   # 20 моделей гітар
python manage.py seed_users     # тестовий користувач
```

### 4. Запуск
```bash
python manage.py runserver
```
Застосунок: http://127.0.0.1:8000/

## Тестовий акаунт

| Логін | Пароль |
|-------|--------|
| `testuser` | `testuser123` |

Лише для локальної розробки та демонстрації.

## Адмінпанель

Створіть адміністратора командою `python manage.py createsuperuser` і зайдіть на http://127.0.0.1:8000/admin/

## Структура
* `config/`: налаштування проєкту
* `guitars/`: основний застосунок (моделі, views, forms, urls, команди `seed_*`)
* `templates/`: HTML-шаблони
* `static/`: стилі, скрипти, зображення

## Від автора

Бажаю вам гарного користування програмою!