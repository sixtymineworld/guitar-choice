# GuitarChoice

Вебзастосунок для вибору, порівняння, конфігурування та замовлення гітар із системою швидкого підбору.

## Стек
* Python 3.13+, Django 6.1.1
* MySQL 8.0+ (`mysql-connector-python`) / TiDB Cloud
* `social-auth-app-django` (авторизація через Google OAuth 2.0)
* `gunicorn`, `whitenoise` (для продакшен-деплою)
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
DJANGO_CSRF_TRUSTED_ORIGINS=https://*.onrender.com

DB_NAME=guitar_choice
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_HOST=127.0.0.1
DB_PORT=3306

# Google OAuth 2.0 (необов'язково для базового тестування)
SOCIAL_AUTH_GOOGLE_OAUTH2_KEY=
SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET=
```

Згенерувати випадковий ключ для `DJANGO_SECRET_KEY`:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Базу даних потрібно створити заздалегідь:
```sql
CREATE DATABASE guitar_choice CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

### 2.1. Генерація ключів Google OAuth 2.0
Ключі потрібні, якщо ви хочете використовувати реєстрацію та вхід через Google:
1. Перейдіть у [Google Cloud Console](https://console.cloud.google.com/) та створіть проєкт `GuitarChoice`.
2. У розділі **APIs & Services** -> **OAuth consent screen** оберіть тип **External**, введіть назву додатка та вашу пошту.
3. У розділі **Credentials** натисніть **Create Credentials** -> **OAuth client ID** (Application type: **Web application**).
4. У пункті **Authorized redirect URIs** (Уповноважені URI переспрямування) додайте:
   - для локальної розробки:
     ```text
     http://127.0.0.1:8000/social-auth/complete/google-oauth2/
     ```
   - для хостингу на Render:
     ```text
     https://<назва-вашого-сервісу>.onrender.com/social-auth/complete/google-oauth2/
     ```
5. Скопіюйте отримані **Client ID** та **Client Secret** у змінні `SOCIAL_AUTH_GOOGLE_OAUTH2_KEY` та `SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET` у файлі `.env`.

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

Також права адміністратора можна призначити будь-якому обліковому запису, створеному через Google, встановивши прапорець `is_staff` та `is_superuser` в адмін-панелі.

## Деплой на Render

Для публікації застосунку на [Render.com](https://render.com/):
- **Build Command**: `./build.sh`
- **Start Command**: `gunicorn config.wsgi:application`
- У вкладці **Environment** задайте параметри з `.env` (включно з `DJANGO_DEBUG=0`, `DJANGO_ALLOWED_HOSTS=.onrender.com`, `DJANGO_CSRF_TRUSTED_ORIGINS=https://*.onrender.com` та параметрами хмарної бази даних).

## Структура
* `config/`: налаштування проєкту
* `guitars/`: основний застосунок (моделі, views, forms, urls, команди `seed_*`)
* `templates/`: HTML-шаблони
* `static/`: стилі, скрипти, зображення
* `build.sh`: скрипт збірки для деплою

## Від автора

Бажаю вам гарного користування програмою!
