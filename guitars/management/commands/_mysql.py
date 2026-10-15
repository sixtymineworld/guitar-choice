"""Shared MySQL connection helpers for the data exchange commands."""
import os
from django.core.management.base import CommandError


def mysql_connection():
    try:
        import mysql.connector
    except ImportError as exc:
        raise CommandError(
            "Пакет mysql-connector-python не встановлено. Виконайте: pip install -r requirements.txt"
        ) from exc

    config = {
        "host": os.getenv("MYSQL_HOST", "127.0.0.1"),
        "port": int(os.getenv("MYSQL_PORT", "3306")),
        "user": os.getenv("MYSQL_USER", "root"),
        "password": os.getenv("MYSQL_PASSWORD", ""),
        "database": os.getenv("MYSQL_DATABASE", "guitar_exchange"),
    }
    try:
        return mysql.connector.connect(**config)
    except mysql.connector.Error as exc:
        raise CommandError(f"Не вдалося підключитися до MySQL: {exc}") from exc


CREATE_GUITARS_TABLE = """
CREATE TABLE IF NOT EXISTS guitars_exchange (
    id BIGINT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    brand VARCHAR(80) NOT NULL,
    guitar_type VARCHAR(20) NOT NULL,
    price DECIMAL(10, 2) NOT NULL,
    description TEXT NOT NULL,
    material VARCHAR(100) NOT NULL,
    strings_count SMALLINT UNSIGNED NOT NULL,
    is_available BOOLEAN NOT NULL,
    image_url VARCHAR(200) NOT NULL DEFAULT '',
    created_at DATETIME(6) NOT NULL
) CHARACTER SET utf8mb4
"""
